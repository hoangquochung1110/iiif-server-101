import yaml
import os
import json
import csv
from collections import defaultdict


def load_config(config_path):
    """Loads the YAML configuration file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def get_image_info(image_id, iiif_image_base_dir):
    """Reads the info.json for a given image to get its dimensions."""
    info_path = os.path.join(iiif_image_base_dir, image_id, 'info.json')
    if not os.path.exists(info_path):
        return None, None
    with open(info_path, 'r') as f:
        info = json.load(f)
        return info.get('width'), info.get('height')


def build_manifests(config, metadata_path, iiif_image_base_dir, output_dir):
    """Builds IIIF Presentation v3 manifests from metadata."""
    iiif_base_url = config['iiif_base_url']
    manifest_base_url = iiif_base_url.replace('/2/', '/presentation/')

    # Group images by object_id from the CSV
    objects = defaultdict(list)
    with open(metadata_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            objects[row['object_id']].append(row)

    # Create a manifest for each object
    for object_id, items in objects.items():
        manifest_id = f"{manifest_base_url}{object_id}/manifest.json"
        
        # Basic manifest structure
        manifest = {
            "@context": "http://iiif.io/api/presentation/3/context.json",
            "id": manifest_id,
            "type": "Manifest",
            "label": {"en": [f"Manifest for {object_id}"]},
            "items": []
        }

        # Add each image as a canvas to the manifest
        for i, item in enumerate(items):
            image_id = item['image_id']
            label = item['label']
            width, height = get_image_info(image_id, iiif_image_base_dir)

            if not width or not height:
                print(f"Warning: Could not find info.json for {image_id}. Skipping.")
                continue

            canvas_id = f"{manifest_id}/canvas/{i}"
            
            canvas = {
                "id": canvas_id,
                "type": "Canvas",
                "label": {"en": [label]},
                "height": height,
                "width": width,
                "items": [{
                    "id": f"{canvas_id}/page",
                    "type": "AnnotationPage",
                    "items": [{
                        "id": f"{canvas_id}/page/image",
                        "type": "Annotation",
                        "motivation": "painting",
                        "body": {
                            "id": f"{iiif_base_url}{image_id}/full/max/0/default.jpg",
                            "type": "Image",
                            "format": "image/jpeg", # Or use config value
                            "service": [{
                                "@id": f"{iiif_base_url}{image_id}",
                                "@type": "ImageService2",
                                "profile": "level0"
                            }]
                        },
                        "target": canvas_id
                    }]
                }]
            }
            manifest['items'].append(canvas)

        # Write the manifest file
        output_path = os.path.join(output_dir, f"{object_id}.json")
        os.makedirs(output_dir, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(manifest, f, indent=4)
        print(f"Created manifest for {object_id} at {output_path}")


def main():
    config = load_config('config/config.yaml')
    metadata_path = 'data/metadata.csv'
    iiif_image_base_dir = 'public/iiif/2'
    output_dir = 'public/iiif/presentation'
    
    build_manifests(config, metadata_path, iiif_image_base_dir, output_dir)

if __name__ == "__main__":
    main()