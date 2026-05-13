import matplotlib.pyplot as plt
from BWT import bwt_encode
from MTF import mtf_encode
from entropy_coding import shannon_entropy

def entropy_after_bwt_mtf(data: bytes, block_sizes: list) -> list:
    entropies = []
    for bs in block_sizes:
        bwt_stream = bwt_encode(data, block_size=bs)
        mtf_stream = mtf_encode(bwt_stream)
        _, ent_per_byte = shannon_entropy(mtf_stream, Ms=1)
        entropies.append(ent_per_byte)
        print(f"Block size {bs:8d}: entropy = {ent_per_byte:.4f} bits/byte")
    return entropies

with open("test_data/english.txt", "rb") as f:
    data_eng = f.read()

_, orig_eng = shannon_entropy(data_eng, 1)

block_sizes = [1000, 2000, 5000, 10000, 20000, 50000]
ent_eng = entropy_after_bwt_mtf(data_eng, block_sizes)

plt.figure(figsize=(10,6))
plt.plot(block_sizes, ent_eng, 'bo-', label='english (BWT+MTF)')
plt.axhline(y=orig_eng, color='b', linestyle='--', alpha=0.5, label=f'english исходная ({orig_eng:.3f})')
plt.xscale('log')
plt.xlabel('Размер блока BWT (байт, лог. шкала)')
plt.ylabel('Энтропия (бит/байт)')
plt.title('Зависимость энтропии после BWT+MTF от размера блока')
plt.legend()
plt.grid(True)
plt.savefig('entropy_vs_blocksize.png', dpi=150)
plt.show()