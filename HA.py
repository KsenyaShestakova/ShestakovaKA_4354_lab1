from collections import Counter
from heapq import heappush, heappop, heapify
from bitio import BitWriter, BitReader

class _Node:
    __slots__ = ('freq', 'symbol', 'left', 'right')
    def __init__(self, freq, symbol=None, left=None, right=None):
        self.freq = freq
        self.symbol = symbol
        self.left = left
        self.right = right
    def __lt__(self, other):
        return self.freq < other.freq

def _build_code_lengths(freq, limit=256):
    heap = [_Node(freq.get(i, 0), i) for i in range(limit) if freq.get(i, 0) > 0]
    if not heap:
        lengths = [0] * limit
        lengths[0] = 1
        return lengths
    heapify(heap)
    while len(heap) > 1:
        l = heappop(heap)
        r = heappop(heap)
        heappush(heap, _Node(l.freq + r.freq, left=l, right=r))
    root = heappop(heap)
    lengths = [0] * limit
    def walk(node, depth):
        if node.symbol is not None:
            lengths[node.symbol] = depth
        else:
            walk(node.left, depth + 1)
            walk(node.right, depth + 1)
    walk(root, 0)
    if max(lengths) == 0:
        lengths[0] = 1
    return lengths

def canonical_from_lengths(lengths):
    sym_len = [(ln, sym) for sym, ln in enumerate(lengths) if ln > 0]
    sym_len.sort(key=lambda x: (x[0], x[1]))
    codes = {}
    code = 0
    prev_len = 0
    for ln, sym in sym_len:
        code <<= (ln - prev_len)
        codes[sym] = f"{code:0{ln}b}"
        prev_len = ln
        code += 1
    return codes

def ha_encode(data: bytes) -> bytes:
    freq = Counter(data)
    MAX_SYM = 256
    lengths = _build_code_lengths(freq, MAX_SYM)
    codes = canonical_from_lengths(lengths)
    out = bytearray()
    out.extend(len(data).to_bytes(4, 'big'))
    for l in lengths:
        out.append(l)
    bw = BitWriter()
    for b in data:
        for ch in codes[b]:
            bw.write_bit(int(ch))
    bw.flush()
    out.extend(bw.buffer)
    return bytes(out)

def ha_decode(data: bytes) -> bytes:
    if len(data) < 4 + 256:
        raise ValueError("Invalid Huffman data")
    orig_len = int.from_bytes(data[0:4], 'big')
    lengths = list(data[4:4 + 256])
    codes = canonical_from_lengths(lengths)
    decode_map = {v: k for k, v in codes.items()}
    br = BitReader(data[4 + 256:])
    out = bytearray()
    current = ''
    while len(out) < orig_len:
        current += str(br.read_bit())
        if current in decode_map:
            out.append(decode_map[current])
            current = ''
    return bytes(out)