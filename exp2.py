import time
import matplotlib.pyplot as plt
from LZ import LZSS

def lzss_ratio_vs_window(data: bytes, window_sizes: list) -> list:
    results = []
    for ws in window_sizes:
        lz = LZSS(window_size=ws, max_match=255, min_match=3)
        start = time.time()
        compressed = lz.encode(data)
        enc_time = time.time() - start
        cr = len(data) / len(compressed)
        results.append((ws, cr, enc_time))
        print(f"Window {ws:6d}: CR = {cr:.3f}, time = {enc_time:.3f}s")
    return results

with open("test_data/english.txt", "rb") as f:
    data = f.read()

window_sizes = [512, 1024, 2048, 4096, 8192, 16384, 32768, 65535]
res = lzss_ratio_vs_window(data, window_sizes)
ws_vals, cr_vals, times = zip(*res)

fig, ax1 = plt.subplots(figsize=(10, 6))
ax1.plot(ws_vals, cr_vals, 'b-o', label='Коэффициент сжатия (CR)')
ax1.set_xscale('log')
ax1.set_xlabel('Размер окна (байт, логарифмическая шкала)')
ax1.set_ylabel('CR', color='b')
ax1.tick_params(axis='y', labelcolor='b')

ax2 = ax1.twinx()
ax2.plot(ws_vals, times, 'r-s', label='Время кодирования (с)')
ax2.set_ylabel('Время (с)', color='r')
ax2.tick_params(axis='y', labelcolor='r')

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

plt.title('Зависимость LZSS от размера окна')
plt.grid(True)
plt.savefig('lzss_window.png', dpi=150)
plt.show()