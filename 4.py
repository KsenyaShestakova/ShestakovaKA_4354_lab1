# experiment_lzw_dict.py
import matplotlib.pyplot as plt
from LZ import LZW

def lzw_ratio_vs_dict(data: bytes, dict_sizes: list, label: str):
    cr_vals = []
    for ds in dict_sizes:
        lzw = LZW(max_dict_size=ds)
        compressed = lzw.encode(data)
        cr = len(data) / len(compressed)
        cr_vals.append(cr)
        print(f"[{label}] Dict size {ds:>6}: CR = {cr:.3f}")
    return cr_vals


with open("test_data/english.txt", "rb") as f:
    data_eng = f.read()
with open("test_data/enwik7.txt", "rb") as f:
    data_enwik7 = f.read()

dict_sizes = [1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072]

cr_eng = lzw_ratio_vs_dict(data_eng, dict_sizes, "english")
cr_enwik7 = lzw_ratio_vs_dict(data_enwik7, dict_sizes, "enwik7")


plt.figure(figsize=(10, 6))
plt.plot(dict_sizes, cr_eng, 'g-o', label='english.txt')
plt.plot(dict_sizes, cr_enwik7, 'm-s', label='enwik7')
plt.xscale('log')
plt.xlabel('Максимальный размер словаря (записей, лог. шкала)')
plt.ylabel('Коэффициент сжатия (CR)')
plt.title('Зависимость LZW от размера словаря')
plt.legend()
plt.grid(True)
plt.savefig('lzw_dict.png', dpi=150)
plt.show()