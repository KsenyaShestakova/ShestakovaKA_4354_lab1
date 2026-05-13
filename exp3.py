import matplotlib.pyplot as plt
from LZ import LZW

def lzw_ratio_vs_dict(data: bytes, dict_sizes: list) -> list:
    results = []
    for ds in dict_sizes:
        lzw = LZW(max_dict_size=ds)
        compressed = lzw.encode(data)
        cr = len(data) / len(compressed)
        results.append((ds, cr))
        print(f"Dict size {ds:6d}: CR = {cr:.3f}")
    return results

with open("test_data/english.txt", "rb") as f:
    data = f.read()

dict_sizes = [1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072]
res = lzw_ratio_vs_dict(data, dict_sizes)
sizes, cr_vals = zip(*res)

plt.figure(figsize=(10, 6))
plt.plot(sizes, cr_vals, 'g-o')
plt.xscale('log')
plt.xlabel('Максимальный размер словаря (записей, логарифмическая шкала)')
plt.ylabel('Коэффициент сжатия (CR)')
plt.title('Зависимость LZW от размера словаря')
plt.grid(True)
plt.savefig('lzw_dict.png', dpi=150)
plt.show()