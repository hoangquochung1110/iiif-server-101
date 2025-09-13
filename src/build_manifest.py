import os
import json
import csv
import logging
from collections import defaultdict
from config_loader import load_config
from config_validator import validate_directories, ConfigValidationError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_image_info(image_id, iiif_image_base_dir):
    """Reads the info.json for a given image to get its dimensions."""
    # Normalize image_id by replacing spaces with underscores to match directory structure
    # Preserve case to match actual directory names
    normalized_id = image_id.replace(' ', '_')
    
    # Check if the directory exists with the current case
    dir_path = os.path.join(iiif_image_base_dir, normalized_id)
    if not os.path.exists(dir_path):
        # Try to find the actual directory with correct case
        parent_dir = os.path.dirname(dir_path)
        if os.path.exists(parent_dir):
            for item in os.listdir(parent_dir):
                if item.lower() == normalized_id.lower():
                    normalized_id = item
                    logger.info(f"Found actual directory name: {normalized_id}")
                    break
    
    info_path = os.path.join(iiif_image_base_dir, normalized_id, 'info.json')
    if not os.path.exists(info_path):
        logger.warning(f"Info file not found: {info_path}")
        return None, None
    
    try:
        with open(info_path, 'r') as f:
            info = json.load(f)
            return info.get('width'), info.get('height')
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error reading info file {info_path}: {e}")
        return None, None





def build_manifest_v2(object_id, items, config, iiif_image_base_dir):
    """Builds a IIIF Presentation API v2 manifest for a given object."""
    iiif_base_url = config['iiif_base_url']
    manifest_base_url = iiif_base_url.replace('/2/', '/presentation/')
    manifest_id = f"{manifest_base_url}{object_id}/manifest.json"
    
    # Basic manifest structure for v2
    manifest = {
        "@context": "http://iiif.io/api/presentation/2/context.json",
        "@id": manifest_id,
        "@type": "sc:Manifest",
        "label": f"Manifest for {object_id}",
        "sequences": [{
            "@id": f"{manifest_id}/sequence/normal",
            "@type": "sc:Sequence",
            "canvases": []
        }]
    }

    # Add each image as a canvas to the sequence
    for i, item in enumerate(items):
        image_id = item['image_id']
        label = item['label']
        width, height = get_image_info(image_id, iiif_image_base_dir)

        if not width or not height:
            print(f"Warning: Could not find info.json for {image_id}. Skipping.")
            continue

        canvas_id = f"{manifest_id}/canvas/{i}"
        
        # Normalize image_id for URLs - preserve case
        # Important: Keep the original case (uppercase/lowercase) to match actual directory names
        normalized_id = image_id.replace(' ', '_')
        
        # Check if the directory exists with the current case
        dir_path = os.path.join(iiif_image_base_dir, normalized_id)
        if not os.path.exists(dir_path):
            # Try to find the actual directory with correct case
            parent_dir = os.path.dirname(dir_path)
            if os.path.exists(parent_dir):
                for item in os.listdir(parent_dir):
                    if item.lower() == normalized_id.lower():
                        normalized_id = item
                        logger.info(f"Found actual directory name: {normalized_id}")
                        break
        
        # For debugging
        logger.info(f"Using normalized_id: {normalized_id} for image_id: {image_id}")
        
        canvas = {
            "@id": canvas_id,
            "@type": "sc:Canvas",
            "label": label,
            "height": height,
            "width": width,
            "images": [{
                "@id": f"{canvas_id}/annotation/0",
                "@type": "oa:Annotation",
                "motivation": "sc:painting",
                "resource": {
                    "@id": f"{iiif_base_url}{normalized_id}/full/full/0/default.jpg",
                    "@type": "dcterms:Image",
                    "format": "image/jpeg",
                    "width": width,
                    "height": height,
                    "service": {
                        "@context": "http://iiif.io/api/image/2/context.json",
                        "@id": f"{iiif_base_url}{normalized_id}",
                        "profile": "http://iiif.io/api/image/2/level2.json"
                    }
                },
                "on": canvas_id
            }]
        }
        manifest['sequences'][0]['canvases'].append(canvas)
    
    return manifest


def build_manifests(config, metadata_path, iiif_image_base_dir, output_dir):
    """Builds IIIF Presentation API v2 manifests from metadata.
    
    Args:
        config: Configuration dictionary
        metadata_path: Path to metadata CSV file
        iiif_image_base_dir: Base directory for IIIF image tiles
        output_dir: Base output directory for manifests
    """
    try:
        # Validate metadata file exists
        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
        
        # Group images by object_id from the CSV
        objects = defaultdict(list)
        with open(metadata_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                object_id = row.get('object_id')
                if not object_id:
                    logger.warning(f"Row missing object_id: {row}")
                    continue
                objects[object_id].append(row)
        
        logger.info(f"Found {len(objects)} objects in metadata")
        
        if not objects:
            logger.warning("No valid objects found in metadata")
            return
        
        # Create manifests for each object
        successful_count = 0
        failed_count = 0
        
        for object_id, items in objects.items():
            try:
                logger.info(f"Building manifest for object: {object_id}")
                
                # Generate v2 manifest
                manifest_v2 = build_manifest_v2(object_id, items, config, iiif_image_base_dir)
                output_path = os.path.join(output_dir, f"{object_id}.json")
                os.makedirs(output_dir, exist_ok=True)
                with open(output_path, 'w') as f:
                    json.dump(manifest_v2, f, indent=4)
                logger.info(f"Created manifest for {object_id}")
                
                successful_count += 1
                
            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to build manifest for {object_id}: {e}")
                continue
        
        logger.info(f"Manifest generation completed: {successful_count} successful, {failed_count} failed")
        
    except Exception as e:
        logger.error(f"Error in build_manifests: {e}")
        raise


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Build IIIF Presentation API v2 manifests')
    parser.add_argument('--metadata', default='data/metadata.csv',
                       help='Path to metadata CSV file')
    parser.add_argument('--image-dir', default='public/iiif/2',
                       help='Base directory for IIIF image tiles')
    parser.add_argument('--output-dir', default='public/iiif/presentation',
                       help='Output directory for manifests')
    
    args = parser.parse_args()
    
    try:
        # Load and validate configuration
        logger.info("Loading configuration...")
        config = load_config()
        logger.info("Configuration loaded and validated successfully")
        
        # Validate directories
        logger.info("Validating directories...")
        validate_directories(config)
        
        # Build manifests
        logger.info("Building v2 manifests...")
        build_manifests(config, args.metadata, args.image_dir, args.output_dir)
        
        logger.info("\nManifest generation complete")
        logger.info(f"Output directory: {args.output_dir}")
            
    except ConfigValidationError as e:
        logger.error(f"Configuration validation failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        raise

if __name__ == "__main__":
    main()