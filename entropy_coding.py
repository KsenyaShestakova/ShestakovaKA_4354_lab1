import math
from collections import Counter

def shannon_entropy(data: bytes, Ms=1):
    if len(data) == 0:
        return 0.0, 0.0
    n = len(data) // Ms
    freq = Counter()
    for i in range(n):
        symbol = data[i * Ms:(i + 1) * Ms]
        freq[symbol] += 1
    total = sum(freq.values())
    ent = 0.0
    for cnt in freq.values():
        p = cnt / total
        ent -= p * math.log2(p)
    return ent, ent / Ms