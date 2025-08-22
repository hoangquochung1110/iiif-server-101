import yaml
import os
import json
from PIL import Image

# Disable decompression bomb check
Image.MAX_IMAGE_PIXELS = None


def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def process_image(image_path, output_dir, config):
    tile_size = config['tile_size']
    fmt = config['image_format']
    quality = config['quality']
    iiif_base_url = config['iiif_base_url']

    image_id = os.path.splitext(os.path.basename(image_path))[0]
    image_dir = os.path.join(output_dir, image_id)
    os.makedirs(image_dir, exist_ok=True)

    img = Image.open(image_path)
    width, height = img.size

    # Create info.json
    info = {
        "@context": "http://iiif.io/api/image/2/context.json",
        "@id": f"{iiif_base_url}{image_id}",
        "protocol": "http://iiif.io/api/image",
        "width": width,
        "height": height,
        "tiles": [{
            "width": tile_size,
            "scaleFactors": [1, 2, 4, 8, 16]
        }],
        "profile": ["http://iiif.io/api/image/2/level0.json"]
    }

    with open(os.path.join(image_dir, 'info.json'), 'w') as f:
        json.dump(info, f, indent=4)

    # Create tiles
    for y in range(0, height, tile_size):
        for x in range(0, width, tile_size):
            tile = img.crop((x, y, x + tile_size, y + tile_size))
            tile_dir = os.path.join(image_dir, f"{x},{y},{tile_size},{tile_size}")
            os.makedirs(tile_dir, exist_ok=True)
            tile.save(os.path.join(tile_dir, f"0.{fmt}"), quality=quality)


def main():
    config = load_config('config/config.yaml')
    masters_dir = 'data/masters'
    output_dir = 'public/iiif/2'

    for filename in os.listdir(masters_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            image_path = os.path.join(masters_dir, filename)
            print(f"Processing {image_path}...")
            process_image(image_path, output_dir, config)
            print(f"Finished processing {image_path}.")

if __name__ == "__main__":
    main()