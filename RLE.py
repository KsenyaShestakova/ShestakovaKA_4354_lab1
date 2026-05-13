def rle_encode(data: bytes, Ms=1, Mc=1) -> bytes:
    assert Mc == 1, "Only Mc=1 implemented"
    if len(data) == 0:
        return bytes([Ms, Mc])
    out = bytearray([Ms, Mc])
    i = 0
    n = len(data) // Ms
    while i < n:
        run_start = i
        sym = data[i * Ms:(i + 1) * Ms]
        i += 1
        while i < n and data[i * Ms:(i + 1) * Ms] == sym:
            i += 1
        run_len = i - run_start
        if run_len >= 2:
            while run_len > 0:
                chunk = min(run_len, 127)
                out.append(chunk & 0x7F)
                out.extend(sym)
                run_len -= chunk
                run_start += chunk
        else:
            lit_start = run_start
            while i < n and (i + 1 >= n or data[i * Ms:(i + 1) * Ms] != data[(i + 1) * Ms:(i + 2) * Ms]):
                i += 1
            lit_len = i - lit_start
            while lit_len > 0:
                chunk = min(lit_len, 127)
                out.append(0x80 | chunk)
                out.extend(data[lit_start * Ms:(lit_start + chunk) * Ms])
                lit_len -= chunk
                lit_start += chunk
    return bytes(out)


def rle_decode(data: bytes) -> bytes:
    if len(data) < 2:
        return b''
    Ms = data[0]
    Mc = data[1]
    assert Mc == 1
    out = bytearray()
    i = 2
    while i < len(data):
        ctrl = data[i]
        i += 1
        if ctrl & 0x80:
            length = ctrl & 0x7F
            out.extend(data[i:i + length * Ms])
            i += length * Ms
        else:
            count = ctrl & 0x7F
            sym = data[i:i + Ms]
            out.extend(sym * count)
            i += Ms
    return bytes(out)