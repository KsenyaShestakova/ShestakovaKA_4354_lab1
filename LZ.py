import struct
import math
from bitio import BitWriter, BitReader

class LZSS:
    def __init__(self, window_size=32768, max_match=255, min_match=3):
        self.window_size = window_size
        self.max_match = max_match
        self.min_match = min_match

    def encode(self, data: bytes) -> bytes:
        win = self.window_size
        max_len = self.max_match
        min_len = self.min_match
        n = len(data)

        output = bytearray()
        output.extend(struct.pack('>H', win))
        output.extend(struct.pack('>I', n))
        bw = BitWriter()
        i = 0
        off_bits = math.ceil(math.log2(win + 1))
        len_bits = 8

        if max_len >= 3:
            hash_table = {}
        else:
            hash_table = None

        while i < n:
            best_len = min_len - 1
            best_dist = 0

            if hash_table is not None and i + 3 <= n:
                key = data[i:i+3]
                if key in hash_table:
                    for pos in hash_table[key]:
                        if i - pos > win:
                            continue
                        l = 3
                        while l < max_len and i + l < n and data[pos + l] == data[i + l]:
                            l += 1
                        if l > best_len:
                            best_len = l
                            best_dist = i - pos
                            if best_len == max_len:
                                break

            if best_len < min_len:
                bw.write_bit(0)
                bw.write_bits(data[i], 8)
                if hash_table is not None and i + 3 <= n:
                    key = data[i:i+3]
                    if key not in hash_table:
                        hash_table[key] = []
                    lst = hash_table[key]
                    lst.append(i)
                    if len(lst) > 100 and i % 100 == 0:
                        hash_table[key] = [p for p in lst if i - p <= win]
                i += 1
            else:
                bw.write_bit(1)
                bw.write_bits(best_dist, off_bits)
                bw.write_bits(best_len - min_len, len_bits)
                if hash_table is not None:
                    for j in range(i, i + best_len):
                        if j + 3 <= n:
                            key = data[j:j+3]
                            if key not in hash_table:
                                hash_table[key] = []
                            lst = hash_table[key]
                            lst.append(j)
                            if len(lst) > 100 and j % 100 == 0:
                                hash_table[key] = [p for p in lst if j - p <= win]
                i += best_len

        bw.flush()
        output.extend(bw.buffer)
        return bytes(output)

    def decode(self, compressed: bytes) -> bytes:
        pos = 0
        win = struct.unpack('>H', compressed[pos:pos + 2])[0]; pos += 2
        orig_len = struct.unpack('>I', compressed[pos:pos + 4])[0]; pos += 4
        br = BitReader(compressed[pos:])
        out = bytearray()
        off_bits = math.ceil(math.log2(win + 1))
        len_bits = 8
        while len(out) < orig_len:
            if br.read_bit() == 0:
                out.append(br.read_bits(8))
            else:
                dist = br.read_bits(off_bits)
                length = br.read_bits(len_bits) + self.min_match
                start = len(out) - dist
                if start < 0 or start >= len(out):
                    raise ValueError(f"LZSS decode: invalid distance {dist} at len {len(out)}")
                for _ in range(length):
                    out.append(out[start])
                    start += 1
        return bytes(out)


class LZW:
    def __init__(self, max_dict_size=65535):
        self.max_dict = max_dict_size

    def encode(self, data: bytes) -> bytes:
        max_entries = self.max_dict
        dictionary = {bytes([i]): i for i in range(256)}
        next_code = 256
        w = b''
        codes = []
        for c in data:
            wc = w + bytes([c])
            if wc in dictionary:
                w = wc
            else:
                codes.append(dictionary[w])
                if next_code < max_entries:
                    dictionary[wc] = next_code
                    next_code += 1
                w = bytes([c])
        if w:
            codes.append(dictionary[w])

        max_code_val = max(codes) if codes else 0
        bit_len = max(9, math.ceil(math.log2(max_code_val + 1))) if codes else 9

        out = bytearray()
        out.extend(struct.pack('>I', max_entries))
        out.extend(struct.pack('>I', len(data)))
        out.append(bit_len)
        bw = BitWriter()
        for code in codes:
            bw.write_bits(code, bit_len)
        bw.flush()
        out.extend(bw.buffer)
        return bytes(out)

    def decode(self, compressed: bytes) -> bytes:
        pos = 0
        max_entries = struct.unpack('>I', compressed[pos:pos + 4])[0]; pos += 4
        orig_len = struct.unpack('>I', compressed[pos:pos + 4])[0]; pos += 4
        bit_len = compressed[pos]; pos += 1
        br = BitReader(compressed[pos:])
        dictionary = {i: bytes([i]) for i in range(256)}
        next_code = 256
        code = br.read_bits(bit_len)
        if code not in dictionary:
            raise ValueError("Invalid LZW stream")
        entry = dictionary[code]
        out = bytearray(entry)
        prev = entry
        while len(out) < orig_len:
            try:
                code = br.read_bits(bit_len)
            except EOFError:
                break
            if code in dictionary:
                entry = dictionary[code]
            elif code == next_code:
                entry = prev + prev[:1]
            else:
                raise ValueError("Invalid LZW code")
            out.extend(entry)
            if next_code < max_entries:
                dictionary[next_code] = prev + entry[:1]
                next_code += 1
            prev = entry
            if next_code > (1 << bit_len) and bit_len < 16:
                bit_len += 1
        return bytes(out[:orig_len])