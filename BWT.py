import struct

def bwt_encode_block(block: bytes, sentinel: int):
    n = len(block)
    if n == 0:
        return sentinel, bytes([sentinel])

    T = list(block) + [sentinel]
    shifts = [T[i:] + T[:i] for i in range(n + 1)]
    shifts.sort()
    L = bytes(row[-1] for row in shifts)
    return sentinel, L


def bwt_decode_block(sentinel: int, L: bytes):
    n1 = len(L)
    if n1 == 1:
        return b''

    F = sorted(L)
    count = [0] * 256
    for b in L:
        count[b] += 1

    C = [0] * 256
    total = 0
    for i in range(256):
        C[i] = total
        total += count[i]

    occ = [0] * 256
    next_row = [0] * n1
    for i, b in enumerate(L):
        next_row[i] = C[b] + occ[b]
        occ[b] += 1

    row = L.index(sentinel)

    T = bytearray()
    for _ in range(n1):
        b = L[row]
        T.append(b)
        row = next_row[row]

    T_rev = T[::-1]
    assert T_rev[-1] == sentinel, f"Sentinel mismatch: ожидался {sentinel}, получен {T_rev[-1]}"
    return bytes(T_rev[:-1])


def bwt_encode(data: bytes, block_size=2000) -> bytes:
    out = bytearray()
    blocks_meta = []
    pos = 0
    while pos < len(data):
        block = data[pos:pos + block_size]
        pos += len(block)
        present = set(block)
        sentinel = None
        for b in range(256):
            if b not in present:
                sentinel = b
                break
        if sentinel is not None:
            _, L = bwt_encode_block(block, sentinel)
            blocks_meta.append((1, len(block), sentinel, L))
        else:
            blocks_meta.append((0, len(block), 0, block))

    out.extend(struct.pack('>I', len(blocks_meta)))
    for flag, blen, sent, payload in blocks_meta:
        out.append(flag)
        out.extend(struct.pack('>I', blen))
        if flag == 1:
            out.append(sent)
        out.extend(payload)
    return bytes(out)


def bwt_decode(data: bytes) -> bytes:
    pos = 0
    n_blocks = struct.unpack('>I', data[pos:pos + 4])[0]
    pos += 4
    out = bytearray()
    for _ in range(n_blocks):
        flag = data[pos]; pos += 1
        blen = struct.unpack('>I', data[pos:pos + 4])[0]; pos += 4
        if flag == 0:
            out.extend(data[pos:pos + blen])
            pos += blen
        else:
            sentinel = data[pos]; pos += 1
            L = data[pos:pos + blen + 1]; pos += blen + 1
            out.extend(bwt_decode_block(sentinel, L))
    return bytes(out)