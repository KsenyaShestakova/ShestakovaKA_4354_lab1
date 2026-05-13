def mtf_encode(data: bytes) -> bytes:
    alphabet = list(range(256))
    res = bytearray()
    for b in data:
        idx = alphabet.index(b)
        res.append(idx)
        del alphabet[idx]
        alphabet.insert(0, b)
    return bytes(res)


def mtf_decode(data: bytes) -> bytes:
    alphabet = list(range(256))
    res = bytearray()
    for idx in data:
        b = alphabet[idx]
        res.append(b)
        del alphabet[idx]
        alphabet.insert(0, b)
    return bytes(res)