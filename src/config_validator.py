import os
import logging
from typing import Dict, Any, List, Union, Optional
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class ConfigValidationError(Exception):
    """Custom exception for configuration validation errors"""
    pass

class ConfigValidator:
    """Comprehensive configuration validator for IIIF All-Static system"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate complete configuration and return sanitized config.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            Validated and sanitized configuration
            
        Raises:
            ConfigValidationError: If critical validation errors are found
        """
        self.errors = []
        self.warnings = []
        
        # Validate basic IIIF settings
        self._validate_basic_settings(config)
        
        # Validate tiling configuration
        if 'tiling' in config:
            self._validate_tiling_config(config['tiling'])
        
        # Validate deployment settings if present
        self._validate_deployment_config(config)
        
        # Check for critical errors
        if self.errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in self.errors)
            raise ConfigValidationError(error_msg)
        
        # Log warnings
        for warning in self.warnings:
            logger.warning(f"Config warning: {warning}")
        
        return self._sanitize_config(config)
    
    def _validate_basic_settings(self, config: Dict[str, Any]) -> None:
        """Validate basic IIIF settings"""
        # Validate tile_size
        tile_size = config.get('tile_size', 512)
        if not isinstance(tile_size, int):
            self.errors.append("tile_size must be an integer")
        elif tile_size < 64 or tile_size > 2048:
            self.errors.append("tile_size must be between 64 and 2048 pixels")
        elif tile_size & (tile_size - 1) != 0:
            self.warnings.append("tile_size should be a power of 2 for optimal performance")
        
        # Validate image_format
        image_format = config.get('image_format', 'webp')
        valid_formats = ['webp', 'jpg', 'jpeg', 'png']
        if not isinstance(image_format, str):
            self.errors.append("image_format must be a string")
        elif image_format.lower() not in valid_formats:
            self.errors.append(f"image_format must be one of: {', '.join(valid_formats)}")
        
        # Validate quality
        quality = config.get('quality', 80)
        if not isinstance(quality, int):
            self.errors.append("quality must be an integer")
        elif quality < 1 or quality > 100:
            self.errors.append("quality must be between 1 and 100")
        elif quality < 60:
            self.warnings.append("quality below 60 may result in poor image quality")
        
        # Validate iiif_base_url
        iiif_base_url = config.get('iiif_base_url', '')
        if not isinstance(iiif_base_url, str):
            self.errors.append("iiif_base_url must be a string")
        elif not iiif_base_url:
            self.warnings.append("iiif_base_url is empty, using default localhost URL")
        elif not (iiif_base_url.startswith('http://') or iiif_base_url.startswith('https://')):
            self.errors.append("iiif_base_url must start with http:// or https://")
        elif not iiif_base_url.endswith('/'):
            self.warnings.append("iiif_base_url should end with '/' for proper URL construction")
    
    def _validate_tiling_config(self, tiling_config: Dict[str, Any]) -> None:
        """Validate tiling configuration section"""
        # Validate width_constraints
        width_constraints = tiling_config.get('width_constraints', [])
        self._validate_size_list(width_constraints, 'width_constraints')
        
        # Validate height_constraints
        height_constraints = tiling_config.get('height_constraints', [])
        self._validate_size_list(height_constraints, 'height_constraints')
        
        # Validate percentages
        percentages = tiling_config.get('percentages', [])
        self._validate_percentages(percentages)
        
        # Validate exact_sizes
        exact_sizes = tiling_config.get('exact_sizes', [])
        self._validate_exact_sizes(exact_sizes)
        
        # Validate best_fit_sizes
        best_fit_sizes = tiling_config.get('best_fit_sizes', [])
        self._validate_exact_sizes(best_fit_sizes, 'best_fit_sizes')
        
        # Validate custom_regions
        custom_regions = tiling_config.get('custom_regions', [])
        self._validate_custom_regions(custom_regions)
        
        # Validate rotations
        rotations = tiling_config.get('rotations', [0])
        self._validate_rotations(rotations)
        
        # Validate qualities
        qualities = tiling_config.get('qualities', ['default'])
        self._validate_qualities(qualities)
        
        # Validate formats
        formats = tiling_config.get('formats', ['webp'])
        self._validate_formats(formats)
        
        # Validate enable configuration
        enable_config = tiling_config.get('enable', {})
        self._validate_enable_config(enable_config)
    
    def _validate_size_list(self, size_list: List[int], field_name: str) -> None:
        """Validate a list of size constraints"""
        if not isinstance(size_list, list):
            self.errors.append(f"{field_name} must be a list")
            return
        
        for i, size in enumerate(size_list):
            if not isinstance(size, int):
                self.errors.append(f"{field_name}[{i}] must be an integer")
            elif size < 1 or size > 10000:
                self.errors.append(f"{field_name}[{i}] must be between 1 and 10000 pixels")
        
        # Check for duplicates
        if len(size_list) != len(set(size_list)):
            self.warnings.append(f"{field_name} contains duplicate values")
        
        # Check if sorted
        if size_list != sorted(size_list):
            self.warnings.append(f"{field_name} should be sorted in ascending order for better organization")
    
    def _validate_percentages(self, percentages: List[int]) -> None:
        """Validate percentage list"""
        if not isinstance(percentages, list):
            self.errors.append("percentages must be a list")
            return
        
        for i, pct in enumerate(percentages):
            if not isinstance(pct, int):
                self.errors.append(f"percentages[{i}] must be an integer")
            elif pct < 1 or pct > 100:
                self.errors.append(f"percentages[{i}] must be between 1 and 100")
        
        # Check for duplicates
        if len(percentages) != len(set(percentages)):
            self.warnings.append("percentages contains duplicate values")
    
    def _validate_exact_sizes(self, sizes: List[List[int]], field_name: str = 'exact_sizes') -> None:
        """Validate exact size specifications"""
        if not isinstance(sizes, list):
            self.errors.append(f"{field_name} must be a list")
            return
        
        for i, size in enumerate(sizes):
            if not isinstance(size, list) or len(size) != 2:
                self.errors.append(f"{field_name}[{i}] must be a list of [width, height]")
                continue
            
            width, height = size
            if not isinstance(width, int) or not isinstance(height, int):
                self.errors.append(f"{field_name}[{i}] width and height must be integers")
            elif width < 1 or height < 1 or width > 10000 or height > 10000:
                self.errors.append(f"{field_name}[{i}] dimensions must be between 1 and 10000 pixels")
    
    def _validate_custom_regions(self, regions: List[List[int]]) -> None:
        """Validate custom region specifications"""
        if not isinstance(regions, list):
            self.errors.append("custom_regions must be a list")
            return
        
        for i, region in enumerate(regions):
            if not isinstance(region, list) or len(region) != 4:
                self.errors.append(f"custom_regions[{i}] must be a list of [x, y, width, height]")
                continue
            
            x, y, width, height = region
            if not all(isinstance(val, int) for val in [x, y, width, height]):
                self.errors.append(f"custom_regions[{i}] all values must be integers")
            elif x < 0 or y < 0:
                self.errors.append(f"custom_regions[{i}] x and y coordinates must be non-negative")
            elif width < 1 or height < 1:
                self.errors.append(f"custom_regions[{i}] width and height must be positive")
            elif width > 10000 or height > 10000:
                self.errors.append(f"custom_regions[{i}] dimensions must not exceed 10000 pixels")
    
    def _validate_rotations(self, rotations: List[int]) -> None:
        """Validate rotation angles"""
        if not isinstance(rotations, list):
            self.errors.append("rotations must be a list")
            return
        
        valid_rotations = [0, 90, 180, 270]
        for i, rotation in enumerate(rotations):
            if not isinstance(rotation, int):
                self.errors.append(f"rotations[{i}] must be an integer")
            elif rotation not in valid_rotations:
                self.errors.append(f"rotations[{i}] must be one of: {valid_rotations}")
    
    def _validate_qualities(self, qualities: List[str]) -> None:
        """Validate quality specifications"""
        if not isinstance(qualities, list):
            self.errors.append("qualities must be a list")
            return
        
        valid_qualities = ['default', 'color', 'gray', 'bitonal']
        for i, quality in enumerate(qualities):
            if not isinstance(quality, str):
                self.errors.append(f"qualities[{i}] must be a string")
            elif quality not in valid_qualities:
                self.errors.append(f"qualities[{i}] must be one of: {valid_qualities}")
    
    def _validate_formats(self, formats: List[str]) -> None:
        """Validate format specifications"""
        if not isinstance(formats, list):
            self.errors.append("formats must be a list")
            return
        
        valid_formats = ['webp', 'jpg', 'jpeg', 'png']
        for i, fmt in enumerate(formats):
            if not isinstance(fmt, str):
                self.errors.append(f"formats[{i}] must be a string")
            elif fmt.lower() not in valid_formats:
                self.errors.append(f"formats[{i}] must be one of: {valid_formats}")
    
    def _validate_enable_config(self, enable_config: Dict[str, bool]) -> None:
        """Validate enable/disable flags"""
        if not isinstance(enable_config, dict):
            self.errors.append("enable configuration must be a dictionary")
            return
        
        valid_flags = ['regions', 'tiles', 'rotations', 'qualities', 'size_variants']
        for key, value in enable_config.items():
            if key not in valid_flags:
                self.warnings.append(f"Unknown enable flag: {key}")
            elif not isinstance(value, bool):
                self.errors.append(f"enable.{key} must be a boolean (true/false)")
    
    def _validate_deployment_config(self, config: Dict[str, Any]) -> None:
        """Validate deployment-related configuration"""
        # Check for sensitive data in main config (should be in environment)
        sensitive_keys = ['access_key', 'secret_key', 'password', 'token']
        for key in config.keys():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                self.warnings.append(f"Sensitive configuration '{key}' should be in environment variables, not config file")
    
    def _sanitize_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize and normalize configuration values"""
        sanitized = config.copy()
        
        # Normalize image format
        if 'image_format' in sanitized:
            sanitized['image_format'] = sanitized['image_format'].lower()
            if sanitized['image_format'] == 'jpeg':
                sanitized['image_format'] = 'jpg'
        
        # Ensure iiif_base_url ends with slash
        if 'iiif_base_url' in sanitized and sanitized['iiif_base_url']:
            if not sanitized['iiif_base_url'].endswith('/'):
                sanitized['iiif_base_url'] += '/'
        
        # Normalize tiling formats
        if 'tiling' in sanitized and 'formats' in sanitized['tiling']:
            formats = []
            for fmt in sanitized['tiling']['formats']:
                fmt_lower = fmt.lower()
                if fmt_lower == 'jpeg':
                    fmt_lower = 'jpg'
                formats.append(fmt_lower)
            sanitized['tiling']['formats'] = formats
        
        # Sort size lists for consistency
        if 'tiling' in sanitized:
            tiling = sanitized['tiling']
            for key in ['width_constraints', 'height_constraints', 'percentages']:
                if key in tiling and isinstance(tiling[key], list):
                    tiling[key] = sorted(list(set(tiling[key])))
        
        return sanitized

def validate_directories(config: Dict[str, Any]) -> None:
    """
    Validate that required directories exist and are accessible.
    
    Args:
        config: Configuration dictionary
        
    Raises:
        ConfigValidationError: If directory validation fails
    """
    errors = []
    
    # Check masters directory
    masters_dir = Path("data/masters")
    if not masters_dir.exists():
        errors.append(f"Masters directory does not exist: {masters_dir}")
    elif not masters_dir.is_dir():
        errors.append(f"Masters path is not a directory: {masters_dir}")
    elif not os.access(masters_dir, os.R_OK):
        errors.append(f"Masters directory is not readable: {masters_dir}")
    
    # Check metadata file
    metadata_file = Path("data/metadata.csv")
    if not metadata_file.exists():
        logger.warning(f"Metadata file does not exist: {metadata_file}")
    elif not os.access(metadata_file, os.R_OK):
        errors.append(f"Metadata file is not readable: {metadata_file}")
    
    # Check/create output directory
    output_dir = Path("public/iiif")
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        if not os.access(output_dir, os.W_OK):
            errors.append(f"Output directory is not writable: {output_dir}")
    except PermissionError:
        errors.append(f"Cannot create output directory: {output_dir}")
    
    if errors:
        raise ConfigValidationError("Directory validation failed:\n" + "\n".join(f"  - {error}" for error in errors))

def validate_image_files(masters_dir: str = "data/masters") -> List[str]:
    """
    Validate image files in masters directory.
    
    Args:
        masters_dir: Path to masters directory
        
    Returns:
        List of valid image file paths
        
    Raises:
        ConfigValidationError: If no valid images found
    """
    valid_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.webp'}
    valid_images = []
    errors = []
    
    masters_path = Path(masters_dir)
    if not masters_path.exists():
        raise ConfigValidationError(f"Masters directory does not exist: {masters_dir}")
    
    for file_path in masters_path.iterdir():
        if file_path.is_file():
            if file_path.suffix.lower() in valid_extensions:
                try:
                    # Quick validation that file can be opened
                    from PIL import Image
                    with Image.open(file_path) as img:
                        img.verify()
                    valid_images.append(str(file_path))
                except Exception as e:
                    errors.append(f"Invalid image file {file_path}: {e}")
            elif file_path.suffix:
                logger.warning(f"Skipping unsupported file type: {file_path}")
    
    if not valid_images:
        raise ConfigValidationError(f"No valid image files found in {masters_dir}")
    
    if errors:
        logger.warning(f"Found {len(errors)} invalid image files:\n" + "\n".join(f"  - {error}" for error in errors))
    
    logger.info(f"Found {len(valid_images)} valid image files")
    return valid_images