from bitio import BitWriter, BitReader
import struct

def arithmetic_encode(data: bytes) -> bytes:
    freq = [0] * 256
    for byte in data:
        freq[byte] += 1

    total = len(data)
    if total == 0:
        return struct.pack('>I', 0) + b'\x00' * 1024

    cum = [0] * 257
    for i in range(256):
        cum[i + 1] = cum[i] + freq[i]
    cum[256] = total

    low = 0
    high = 0xFFFFFFFFFFFFFFFF
    pending_bits = 0
    bw = BitWriter()

    def output_bit(bit):
        nonlocal pending_bits
        bw.write_bit(bit)
        while pending_bits > 0:
            bw.write_bit(bit ^ 1)
            pending_bits -= 1

    for byte in data:
        sym_low = cum[byte]
        sym_high = cum[byte + 1]
        rng = high - low + 1
        high = low + (rng * sym_high) // total - 1
        low  = low + (rng * sym_low)  // total

        # нормализация
        while True:
            if high < 0x8000000000000000:
                output_bit(0)
            elif low >= 0x8000000000000000:
                output_bit(1)
                low  -= 0x8000000000000000
                high -= 0x8000000000000000
            elif low >= 0x4000000000000000 and high < 0xC000000000000000:
                pending_bits += 1
                low  -= 0x4000000000000000
                high -= 0x4000000000000000
            else:
                break
            low  <<= 1
            high = (high << 1) | 1

    pending_bits += 1
    if low < 0x4000000000000000:
        output_bit(0)
    else:
        output_bit(1)

    bw.flush()
    bitstream = bytes(bw.buffer)

    out = bytearray()
    out.extend(struct.pack('>I', total))
    for f in freq:
        out.extend(struct.pack('>I', f))
    out.extend(bitstream)
    return bytes(out)


def arithmetic_decode(compressed: bytes) -> bytes:
    pos = 0
    total = struct.unpack('>I', compressed[pos:pos+4])[0]
    pos += 4
    if total == 0:
        return b''

    freq = []
    for _ in range(256):
        f = struct.unpack('>I', compressed[pos:pos+4])[0]
        freq.append(f)
        pos += 4

    cum = [0] * 257
    for i in range(256):
        cum[i+1] = cum[i] + freq[i]
    cum[256] = total

    bitstream = compressed[pos:]
    br = BitReader(bitstream)

    code = 0
    for _ in range(64):
        try:
            code = (code << 1) | br.read_bit()
        except EOFError:
            code <<= 1

    low = 0
    high = 0xFFFFFFFFFFFFFFFF
    out = bytearray()

    for _ in range(total):
        rng = high - low + 1
        scaled = ((code - low + 1) * total - 1) // rng

        lo, hi = 0, 256
        while lo < hi:
            mid = (lo + hi) // 2
            if cum[mid+1] <= scaled:
                lo = mid + 1
            else:
                hi = mid
        symbol = lo
        out.append(symbol)

        sym_low  = cum[symbol]
        sym_high = cum[symbol + 1]
        high = low + (rng * sym_high) // total - 1
        low  = low + (rng * sym_low)  // total

        while True:
            if high < 0x8000000000000000:
                pass
            elif low >= 0x8000000000000000:
                code -= 0x8000000000000000
                low  -= 0x8000000000000000
                high -= 0x8000000000000000
            elif low >= 0x4000000000000000 and high < 0xC000000000000000:
                code -= 0x4000000000000000
                low  -= 0x4000000000000000
                high -= 0x4000000000000000
            else:
                break
            low  <<= 1
            high = (high << 1) | 1
            try:
                code = (code << 1) | br.read_bit()
            except EOFError:
                code <<= 1

    return bytes(out)