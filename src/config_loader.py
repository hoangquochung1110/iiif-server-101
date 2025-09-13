import os
import logging
from typing import Dict, Any, Optional, Callable
import yaml
from config_validator import ConfigValidator, ConfigValidationError

try:
    from dotenv import load_dotenv as _load_dotenv
except ImportError:
    _load_dotenv: Optional[Callable] = None

# Configure logging
logger = logging.getLogger(__name__)


def load_config(config_path: str = 'config/config.yaml', validate: bool = True) -> Dict[str, Any]:
    """
    Load configuration from YAML file with environment variable substitution and validation.
    
    Environment variables take precedence over YAML values.
    Supports .env file loading if python-dotenv is installed.
    
    Args:
        config_path: Path to the YAML configuration file
        validate: Whether to validate the configuration (default: True)
        
    Returns:
        Dictionary containing validated configuration values
        
    Raises:
        ConfigValidationError: If configuration validation fails
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If YAML parsing fails
    """
    # Load .env file if available
    if _load_dotenv is not None:
        _load_dotenv()
    
    # Load YAML configuration
    config: Dict[str, Any] = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Failed to parse YAML configuration file {config_path}: {e}")
    else:
        logger.warning(f"Configuration file not found: {config_path}, using defaults")
    
    # Override with environment variables
    env_mappings = {
        'IIIF_BASE_URL': 'iiif_base_url',
        'TILE_SIZE': 'tile_size',
        'IMAGE_FORMAT': 'image_format',
        'QUALITY': 'quality'
    }
    
    for env_var, config_key in env_mappings.items():
        env_value = os.getenv(env_var)
        if env_value is not None:
            # Convert to appropriate type
            if config_key in ['tile_size', 'quality']:
                try:
                    config[config_key] = int(env_value)
                except ValueError:
                    logger.warning(f"Invalid integer value for {env_var}: {env_value}, ignoring")
            else:
                config[config_key] = env_value
    
    # Set defaults if not provided
    defaults = {
        'tile_size': 512,
        'image_format': 'webp',
        'quality': 80,
        'iiif_base_url': 'http://localhost:8080/iiif/2/',
        'tiling': {
            'width_constraints': [512, 1024, 2048],
            'height_constraints': [512, 1024, 2048],
            'percentages': [10, 25, 50, 75, 90],
            'exact_sizes': [[256, 256], [512, 512], [1024, 1024]],
            'best_fit_sizes': [[512, 512], [1024, 1024]],
            'custom_regions': [],
            'rotations': [0],
            'qualities': ['default'],
            'formats': ['webp'],
            'enable': {
                'regions': True,
                'tiles': True,
                'rotations': False,
                'qualities': True,
                'size_variants': True
            }
        }
    }
    
    # Merge defaults with loaded config
    for key, default_value in defaults.items():
        if key not in config:
            config[key] = default_value
        elif key == 'tiling' and isinstance(config[key], dict) and isinstance(default_value, dict):
            # Merge tiling defaults
            tiling_config = config[key]
            for tiling_key, tiling_default in default_value.items():
                if tiling_key not in tiling_config:
                    tiling_config[tiling_key] = tiling_default
                elif tiling_key == 'enable' and isinstance(tiling_config[tiling_key], dict) and isinstance(tiling_default, dict):
                    # Merge enable defaults
                    enable_config = tiling_config[tiling_key]
                    for enable_key, enable_default in tiling_default.items():
                        if enable_key not in enable_config:
                            enable_config[enable_key] = enable_default
    
    # Validate configuration if requested
    if validate:
        try:
            validator = ConfigValidator()
            config = validator.validate_config(config)
            logger.info("Configuration validation passed")
        except ConfigValidationError as e:
            logger.error(f"Configuration validation failed: {e}")
            raise
    
    return config


def get_deployment_config() -> Dict[str, str]:
    """
    Get deployment-specific configuration from environment variables.
    
    Returns:
        Dictionary containing deployment configuration
    """
    if _load_dotenv is not None:
        _load_dotenv()
    
    return {
        'r2_account_id': os.getenv('R2_ACCOUNT_ID', ''),
        'r2_access_key_id': os.getenv('R2_ACCESS_KEY_ID', ''),
        'r2_secret_access_key': os.getenv('R2_SECRET_ACCESS_KEY', ''),
        'r2_bucket_name': os.getenv('R2_BUCKET_NAME', ''),
        'aws_access_key_id': os.getenv('AWS_ACCESS_KEY_ID', ''),
        'aws_secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY', ''),
        'aws_region': os.getenv('AWS_REGION', 'us-east-1'),
        's3_bucket_name': os.getenv('S3_BUCKET_NAME', ''),
        'b2_key_id': os.getenv('B2_KEY_ID', ''),
        'b2_application_key': os.getenv('B2_APPLICATION_KEY', ''),
        'b2_bucket_name': os.getenv('B2_BUCKET_NAME', '')
    }