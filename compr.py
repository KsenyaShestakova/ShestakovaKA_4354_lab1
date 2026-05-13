import os
import csv
from RLE import rle_encode, rle_decode
from HA import ha_encode, ha_decode
from BWT import bwt_encode, bwt_decode
from MTF import mtf_encode, mtf_decode
from LZ import LZSS, LZW
from arithmetic import arithmetic_encode, arithmetic_decode

def read_file(path):
    with open(path, 'rb') as f:
        return f.read()

def write_file(path, data):
    with open(path, 'wb') as f:
        f.write(data)

def compress_HA(data): return ha_encode(data)
def decompress_HA(data): return ha_decode(data)

def compress_RLE(data): return rle_encode(data, Ms=1, Mc=1)
def decompress_RLE(data): return rle_decode(data)

def compress_BWT_RLE(data):
    return rle_encode(bwt_encode(data), Ms=1, Mc=1)
def decompress_BWT_RLE(data):
    return bwt_decode(rle_decode(data))

def compress_BWT_MTF_HA(data):
    return ha_encode(mtf_encode(bwt_encode(data)))
def decompress_BWT_MTF_HA(data):
    return bwt_decode(mtf_decode(ha_decode(data)))

def compress_BWT_MTF_RLE_HA(data):
    return ha_encode(rle_encode(mtf_encode(bwt_encode(data)), Ms=1, Mc=1))
def decompress_BWT_MTF_RLE_HA(data):
    return bwt_decode(mtf_decode(rle_decode(ha_decode(data))))

lzss = LZSS()
lzw = LZW()

def compress_LZSS(data): return lzss.encode(data)
def decompress_LZSS(data): return lzss.decode(data)

def compress_LZSS_HA(data): return ha_encode(lzss.encode(data))
def decompress_LZSS_HA(data): return lzss.decode(ha_decode(data))

def compress_LZW(data): return lzw.encode(data)
def decompress_LZW(data): return lzw.decode(data)

def compress_LZW_HA(data): return ha_encode(lzw.encode(data))
def decompress_LZW_HA(data): return lzw.decode(ha_decode(data))

def compress_arithmetic(data): return arithmetic_encode(data)
def decompress_arithmetic(data): return arithmetic_decode(data)

all_compressors = [
    ("HA", compress_HA, decompress_HA),
    ("RLE", compress_RLE, decompress_RLE),
    ("BWT+RLE", compress_BWT_RLE, decompress_BWT_RLE),
    ("BWT+MTF+HA", compress_BWT_MTF_HA, decompress_BWT_MTF_HA),
    ("BWT+MTF+RLE+HA", compress_BWT_MTF_RLE_HA, decompress_BWT_MTF_RLE_HA),
    ("LZSS", compress_LZSS, decompress_LZSS),
    ("LZSS+HA", compress_LZSS_HA, decompress_LZSS_HA),
    ("LZW", compress_LZW, decompress_LZW),
    ("LZW+HA", compress_LZW_HA, decompress_LZW_HA),
    # ("Arithmetic", compress_arithmetic, decompress_arithmetic),
]


def main():
    test_files = {
        "gray.raw": "test_data/gray_picture2.raw",
        "color.raw": "test_data/colour_picture2.raw",
        "enwik7": "test_data/enwik7.txt",
        "english": "test_data/english.txt",
        "random.exe": "test_data/binary.bin",
        "bw.raw": "test_data/black_and_white_picture.raw",
    }

    results = []
    for label, path in test_files.items():
        if not os.path.exists(path):
            print(f"File {path} not found, skipping.")
            continue
        original = read_file(path)
        print(f"\n--- {label} ({len(original)} bytes) ---")
        for name, enc, dec in all_compressors:
            try:
                comp = enc(original)
                decomp = dec(comp)
                if decomp != original:
                    print(f"  {name}: MISMATCH")
                else:
                    cr = len(comp) / len(original) if original else 0
                    print(f"  {name}: {len(comp)} B, CR={cr:.4f}")
                    results.append((label, name, len(original), len(comp), cr))
            except Exception as e:
                print(f"  {name}: ERROR {e}")
    with open('compression_results3.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['File', 'Compressor', 'Original_Size', 'Compressed_Size', 'CR'])
        w.writerows(results)
    print("\nResults written to compression_results.csv")


if __name__ == '__main__':
    main()