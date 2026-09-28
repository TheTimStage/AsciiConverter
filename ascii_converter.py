import os
import xml.sax.saxutils as saxutils
from PIL import Image, ImageSequence

def rgb_to_hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"


def generate_svg(input_path, output_path, target_width=80):
    if not os.path.exists(input_path):
        print(f"Ошибка: Файл {input_path} не найден")
        return

    print(f"Открываю файл: {input_path}...")
    img = Image.open(input_path)

    # Настройки
    FONT_SIZE = 14
    CHAR_WIDTH = 8.4  # Ширина символа
    ROW_HEIGHT = 15  # Высота строки
    PADDING = 20  # Отступы по краям
    BG_COLOR = "#0d1117"  # Цвет фона

    ascii_chars = r"$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. "
    num_chars = len(ascii_chars)

    orig_w, orig_h = img.size
    aspect_ratio = orig_h / float(orig_w)
    target_height = int(aspect_ratio * target_width * 0.56)
    if target_height < 1:
        target_height = 1

    frames_svg = []
    frame_count = getattr(img, "n_frames", 1)
    print(f"Генерирую SVG с абсолютным позиционированием...")

    for frame_idx, frame in enumerate(ImageSequence.Iterator(img)):
        frame_rgb = frame.convert("RGB")
        frame_resized = frame_rgb.resize((target_width, target_height), Image.Resampling.LANCZOS)
        frame_gray = frame_resized.convert("L")
        svg_lines = []

        for y in range(target_height):
            y_pos = PADDING + (y + 1) * ROW_HEIGHT - 3
            line_svg = f'    <text x="{PADDING}" y="{y_pos}">'

            current_hex = None
            current_text = ""
            start_x = 0

            for x in range(target_width):
                g_val = frame_gray.getpixel((x, y))
                r, g, b = frame_resized.getpixel((x, y))
                hex_color = rgb_to_hex(r, g, b)

                char_idx = int((g_val * (num_chars - 1)) / 255)
                char = ascii_chars[num_chars - 1 - char_idx]
                char_esc = saxutils.escape(char)

                if hex_color == current_hex:
                    current_text += char_esc
                else:
                    if current_hex is not None:
                        tspan_x = PADDING + (start_x * CHAR_WIDTH)
                        line_svg += f'<tspan x="{tspan_x:.2f}" fill="{current_hex}">{current_text}</tspan>'

                    current_hex = hex_color
                    current_text = char_esc
                    start_x = x

            if current_hex is not None:
                tspan_x = PADDING + (start_x * CHAR_WIDTH)
                line_svg += f'<tspan x="{tspan_x:.2f}" fill="{current_hex}">{current_text}</tspan>'

            line_svg += '</text>\n'
            svg_lines.append(line_svg)

        frames_svg.append("".join(svg_lines))
        if frame_idx % 5 == 0 and frame_idx > 0:
            print(f"Обработано {frame_idx} кадров...")

    svg_width = int(target_width * CHAR_WIDTH) + (2 * PADDING)
    svg_height = int(target_height * ROW_HEIGHT) + (2 * PADDING)

    print("Сохранение результата...")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f'<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
        f.write(f'<svg width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" xmlns="http://www.w3.org/2000/svg">\n')
        f.write(f'  <rect width="100%" height="100%" fill="{BG_COLOR}"/>\n')
        f.write(f'  <style>\n')
        f.write(f'    text {{ font-family: "Courier New", Consolas, monospace; font-size: {FONT_SIZE}px; font-weight: bold; white-space: pre; }}\n')
        f.write(f'  </style>\n')

        dur_s = frame_count * 0.1
        for i, frame_content in enumerate(frames_svg):
            if frame_count > 1:
                f.write('  <g visibility="hidden">\n')
                vals = ["hidden"] * frame_count
                vals[i] = "visible"
                val_str = ";".join(vals)
                f.write(f'    <animate attributeName="visibility" values="{val_str}" dur="{dur_s}s" calcMode="discrete" repeatCount="indefinite"/>\n')
            else:
                f.write('  <g visibility="visible">\n')

            f.write(frame_content)
            f.write('  </g>\n')

        f.write('</svg>\n')
    print(f"Файл сохранен: {output_path} (Размер: {svg_width}x{svg_height}px)")


# Вот бы сделать интерфейс в будущем...
if __name__ == "__main__":
    # МЕНЯТЬ ФАЙЛ ТУТ
    INPUT_FILE = ("gandon.png")
    OUTPUT_FILE = "gandon.svg"

    generate_svg(INPUT_FILE, OUTPUT_FILE, target_width=80)