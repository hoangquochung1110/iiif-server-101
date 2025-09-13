import os
import json
import math
import logging
from PIL import Image, ImageOps
from config_loader import load_config
from config_validator import validate_directories, validate_image_files, ConfigValidationError

# Disable decompression bomb check
Image.MAX_IMAGE_PIXELS = None

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_size_variants(img, base_dir, region_path, rotation, quality, formats, base_quality, tiling_config):
    """Generate all IIIF Image API 2.0 size variants based on configuration"""
    width, height = img.size
    
    # Size variants to generate
    size_variants = [
        ("full", img),  # full size
        ("max", img),   # alias for full
    ]
    
    # Get configuration parameters
    width_constraints = tiling_config.get('width_constraints', [512, 1024, 2048])
    height_constraints = tiling_config.get('height_constraints', [512, 1024, 2048])
    percentages = tiling_config.get('percentages', [10, 25, 50, 75, 90])
    exact_sizes = tiling_config.get('exact_sizes', [[256, 256], [512, 512], [1024, 1024]])
    best_fit_sizes = tiling_config.get('best_fit_sizes', [[512, 512], [1024, 1024]])
    
    # Generate width constraints
    for w in width_constraints:
        if w < width:
            ratio = w / width
            new_height = int(height * ratio)
            resized = img.resize((w, new_height), Image.Resampling.LANCZOS)
            size_variants.append((f"{w},", resized))
    
    # Generate height constraints  
    for h in height_constraints:
        if h < height:
            ratio = h / height
            new_width = int(width * ratio)
            resized = img.resize((new_width, h), Image.Resampling.LANCZOS)
            size_variants.append((f",{h}", resized))
    
    # Generate percentage scaling
    for pct in percentages:
        ratio = pct / 100.0
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        if new_width > 0 and new_height > 0:
            resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            size_variants.append((f"pct:{pct}", resized))
    
    # Generate exact size variants (w,h)
    for w, h in exact_sizes:
        if w <= width and h <= height:
            resized = img.resize((w, h), Image.Resampling.LANCZOS)
            size_variants.append((f"{w},{h}", resized))
    
    # Generate best fit variants (!w,h)
    for w, h in best_fit_sizes:
        # Calculate scaling to fit within bounds while maintaining aspect ratio
        ratio = min(w / width, h / height)
        if ratio < 1.0:
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            size_variants.append((f"!{w},{h}", resized))
    
    # Save all size variants
    for size_name, size_img in size_variants:
        size_dir = os.path.join(base_dir, region_path, size_name, str(rotation))
        os.makedirs(size_dir, exist_ok=True)
        
        for fmt in formats:
            filename = f"{quality}.{fmt}"
            filepath = os.path.join(size_dir, filename)
            
            if fmt in ['jpg', 'jpeg']:
                # Convert to RGB if necessary for JPEG
                save_img = size_img.convert('RGB') if size_img.mode in ('RGBA', 'LA', 'P') else size_img
                save_img.save(filepath, quality=base_quality, optimize=True)
            elif fmt == 'webp':
                size_img.save(filepath, quality=base_quality, optimize=True)
            elif fmt == 'png':
                size_img.save(filepath, optimize=True)
            else:
                size_img.save(filepath)


def generate_quality_variants(img, quality_type):
    """Generate different quality variants of an image"""
    if quality_type == 'default' or quality_type == 'color':
        return img
    elif quality_type == 'gray':
        return ImageOps.grayscale(img)
    elif quality_type == 'bitonal':
        # Convert to 1-bit black and white
        gray = ImageOps.grayscale(img)
        return gray.convert('1')
    else:
        return img


def generate_rotation_variants(img):
    """Generate rotation variants (0, 90, 180, 270)"""
    rotations = {
        0: img,
        90: img.rotate(-90, expand=True),
        180: img.rotate(180, expand=True),
        270: img.rotate(90, expand=True)
    }
    return rotations


def generate_region_variants(img, tiling_config):
    """Generate region variants based on configuration"""
    width, height = img.size
    regions = {
        'full': img,
        'square': None  # Will be calculated below
    }
    
    # Generate square region (center crop to largest square)
    min_dim = min(width, height)
    left = (width - min_dim) // 2
    top = (height - min_dim) // 2
    right = left + min_dim
    bottom = top + min_dim
    regions['square'] = img.crop((left, top, right, bottom))
    
    # Get custom regions from configuration
    custom_regions = tiling_config.get('custom_regions', [])
    
    # Process custom regions
    for region_config in custom_regions:
        x, y, w, h = region_config
        
        # Validate region bounds
        if x + w <= width and y + h <= height:
            region_key = f"{x},{y},{w},{h}"
            regions[region_key] = img.crop((x, y, x + w, y + h))
        else:
            logger.warning(f"Region {region_config} exceeds image bounds ({width}x{height}), skipping")
    
    return regions


def process_image(image_path, output_dir, config):
    """Process image and generate all IIIF Image API 2.0 variants"""
    tile_size = config['tile_size']
    base_quality = config['quality']
    iiif_base_url = config['iiif_base_url']
    tiling_config = config.get('tiling', {})
    
    # Get configuration parameters
    formats = tiling_config.get('formats', ['webp'])
    qualities = tiling_config.get('qualities', ['default'])
    rotations = tiling_config.get('rotations', [0])
    enable_config = tiling_config.get('enable', {})
    
    logger.info(f"Processing image: {image_path}")
    
    # Generate URL-safe image_id
    image_id = os.path.splitext(os.path.basename(image_path))[0]
    image_id = image_id.replace(' ', '_').replace('(', '').replace(')', '').replace('[', '').replace(']', '').replace('#', '').replace('?', '').replace('&', '')
    image_dir = os.path.join(output_dir, image_id)
    os.makedirs(image_dir, exist_ok=True)
    
    img = Image.open(image_path)
    width, height = img.size
    
    logger.info(f"Generating comprehensive IIIF variants for {image_id} ({width}x{height})")
    
    # Generate all region variants if enabled
    if enable_config.get('regions', True):
        regions = generate_region_variants(img, tiling_config)
    else:
        regions = {'full': img}
    
    total_variants = 0
    for region_name, region_img in regions.items():
        logger.debug(f"Processing region: {region_name}")
        
        # Generate rotation variants if enabled
        if enable_config.get('rotations', False) and len(rotations) > 1:
            rotation_variants = generate_rotation_variants(region_img)
            rotation_list = [(angle, img) for angle, img in rotation_variants.items() if angle in rotations]
        else:
            rotation_list = [(0, region_img)]
        
        for rotation_angle, rotated_img in rotation_list:
            # Generate all quality variants
            for quality in qualities:
                quality_img = generate_quality_variants(rotated_img, quality)
                
                # Generate all size variants for this combination
                if enable_config.get('size_variants', True):
                    generate_size_variants(
                        quality_img, image_dir, region_name, 
                        rotation_angle, quality, formats, base_quality, tiling_config
                    )
                    total_variants += 1
    
    # Calculate scale factors for info.json
    max_dimension = max(width, height)
    scale_factors = []
    scale = 1
    while max_dimension // scale >= 64:  # Generate down to 64px minimum
        scale_factors.append(scale)
        scale *= 2
    if not scale_factors:
        scale_factors = [1]
    
    # Create dynamic info.json based on configuration
    profile_features = {
        "formats": formats,
        "qualities": qualities,
        "supports": []
    }
    
    # Add supported features based on configuration
    if enable_config.get('regions', True):
        profile_features["supports"].extend(["regionByPx", "regionSquare"])
    
    if enable_config.get('size_variants', True):
        profile_features["supports"].extend([
            "sizeByW", "sizeByH", "sizeByPct", "sizeByConfinedWh",
            "sizeByWh", "sizeByForcedWh"
        ])
    
    if enable_config.get('rotations', False):
        profile_features["supports"].extend(["rotationBy90s"])
        if len(rotations) > 1:
            profile_features["supports"].append("mirroring")
    
    info = {
        "@context": "http://iiif.io/api/image/2/context.json",
        "@id": f"{iiif_base_url}{image_id}",
        "protocol": "http://iiif.io/api/image",
        "width": width,
        "height": height,
        "profile": ["http://iiif.io/api/image/2/level2.json", profile_features]
    }
    
    # Add tiles if enabled
    if enable_config.get('tiles', True):
        info["tiles"] = [{
            "width": tile_size,
            "height": tile_size,
            "scaleFactors": scale_factors
        }]
    
    with open(os.path.join(image_dir, 'info.json'), 'w') as f:
        json.dump(info, f, indent=2)
    
    logger.info(f"Generated {total_variants} variant combinations for {image_id}")
    logger.info(f"Generated info.json with Level 2 compliance for {image_id}")


def main():
    """Main function to process all images in the masters directory"""
    try:
        # Load and validate configuration
        logger.info("Loading configuration...")
        config = load_config()
        logger.info("Configuration loaded and validated successfully")
        
        # Validate directories and files
        logger.info("Validating directories and files...")
        validate_directories(config)
        
        masters_dir = "data/masters"
        output_dir = "public/iiif/2"
        
        # Get and validate image files
        image_files = validate_image_files(masters_dir)
        logger.info(f"Found {len(image_files)} valid image files to process")
        
        # Process each image with progress tracking
        successful_count = 0
        failed_count = 0
        
        for i, image_path in enumerate(image_files, 1):
            try:
                logger.info(f"[{i}/{len(image_files)}] Processing: {os.path.basename(image_path)}")
                process_image(image_path, output_dir, config)
                successful_count += 1
                logger.info(f"[{i}/{len(image_files)}] ✓ Successfully processed {os.path.basename(image_path)}")
            except Exception as e:
                failed_count += 1
                logger.error(f"[{i}/{len(image_files)}] ✗ Failed to process {os.path.basename(image_path)}: {e}")
                continue
        
        # Summary
        logger.info(f"Processing completed: {successful_count} successful, {failed_count} failed")
        
        if failed_count > 0:
            logger.warning(f"Some images failed to process. Check logs for details.")
        
    except ConfigValidationError as e:
        logger.error(f"Configuration validation failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        raise


if __name__ == "__main__":
    main()