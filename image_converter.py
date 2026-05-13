from PIL import Image
import os
import sys

def image_to_raw(input_path):
    img = Image.open(input_path)
    w, h = img.size
    scale = max(800 / w, 600 / h)
    if scale > 1:
        new_w = int(w * scale)
        new_h = int(h * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)
    if img.mode == '1':
        img_type = 0
        img = img.convert('L')
    elif img.mode == 'L':
        img_type = 1
    elif img.mode in ('RGB', 'RGBA'):
        img = img.convert('RGB')
        img_type = 2
    else:
        try:
            img = img.convert('RGB')
            img_type = 2
        except:
            img = img.convert('L')
            img_type = 1
    pixel_data = img.tobytes()
    raw = bytearray()
    raw.append(img_type)
    raw.extend(pixel_data)
    return bytes(raw)

def convert_all_images_in_folder(folder):
    for root, dirs, files in os.walk(folder):
        for f in files:
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp')):
                full_path = os.path.join(root, f)
                try:
                    raw = image_to_raw(full_path)
                    base = os.path.splitext(f)[0]
                    out_path = os.path.join(root, base + '.raw')
                    with open(out_path, 'wb') as out:
                        out.write(raw)
                    print(f'Converted {full_path} -> {out_path}  ({len(raw)} bytes)')
                except Exception as e:
                    print(f'Error converting {full_path}: {e}')

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else 'test_data'
    convert_all_images_in_folder(target)