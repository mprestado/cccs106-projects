import os
from PIL import Image, ImageOps

input_folder = "assets/icons/"
output_folder = "assets/icons_dark/"

os.makedirs(output_folder, exist_ok=True)

for file in os.listdir(input_folder):
    if file.endswith(".png"):
        src_path = os.path.join(input_folder, file)
        dst_path = os.path.join(output_folder, file)

        img = Image.open(src_path).convert("RGBA")

        # Split alpha and invert only RGB
        r, g, b, a = img.split()
        rgb_image = Image.merge("RGB", (r, g, b))
        inverted_image = ImageOps.invert(rgb_image)
        inverted_image = Image.merge("RGBA", (*inverted_image.split(), a))

        inverted_image.save(dst_path)

        print(f"Inverted: {file}")
