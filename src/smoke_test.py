import json
import os
import sys
import logging
from urllib.parse import urlparse
from config_loader import load_config
from config_validator import validate_directories, ConfigValidationError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Smoke test to check the validity of generated IIIF resources.


def check_file_exists(base_dir, url):
    """Checks if a file referenced by a URL exists on the local filesystem."""
    try:
        parsed_url = urlparse(url)
        # Assumes the path starts with /iiif/
        relative_path = parsed_url.path.lstrip("/")
        local_path = os.path.join(base_dir, relative_path)
        if not os.path.exists(local_path):
            logger.error(f"File not found at {local_path} (from URL: {url})")
            return False
        logger.debug(f"Found {local_path}")
        return True
    except Exception as e:
        logger.error(f"Error checking file existence for URL {url}: {e}")
        return False



def test_manifest_v2(manifest, public_dir):
    """Test IIIF Presentation API v2 manifest structure."""
    errors = 0
    
    # Check thumbnail
    if "thumbnail" in manifest and manifest["thumbnail"]:
        thumbnail_url = manifest["thumbnail"]["@id"]
        if not check_file_exists(public_dir, thumbnail_url):
            errors += 1

    # Check canvases and their images (v2 structure)
    if "sequences" in manifest:
        for sequence in manifest["sequences"]:
            if "canvases" in sequence:
                for canvas in sequence["canvases"]:
                    if "images" in canvas:
                        for image in canvas["images"]:
                            if "resource" in image and "service" in image["resource"]:
                                service = image["resource"]["service"]
                                info_url = service.get("@id")
                                if info_url:
                                    # The @id in the service block is the folder, so append info.json
                                    if not info_url.endswith("info.json"):
                                        info_url = os.path.join(info_url, "info.json")
                                else:
                                    print(f"Warning: No '@id' found in service for canvas")
                                    errors += 1
                                    continue

                                if not check_file_exists(public_dir, info_url):
                                    errors += 1
    
    return errors


def test_manifests_in_directory(directory, config):
    """Test all manifests in a specific directory."""
    public_dir = "public"
    total_errors = 0
    
    if not os.path.isdir(directory):
        print(f"INFO: Directory not found: {directory} (skipping)")
        return 0
    
    print(f"\nScanning manifests in {directory}...")
    
    for filename in sorted(os.listdir(directory)):
        if filename.endswith(".json"):
            manifest_path = os.path.join(directory, filename)
            print(f"\nTesting manifest: {manifest_path}")
            manifest_errors = 0

            try:
                with open(manifest_path, "r") as f:
                    manifest = json.load(f)
            except json.JSONDecodeError:
                print(f"  FAIL: Invalid JSON in {manifest_path}")
                total_errors += 1
                continue
            
            # Check if it's a v2 manifest
            context = manifest.get("@context", "")
            if "presentation/2" in context:
                manifest_errors = test_manifest_v2(manifest, public_dir)
            else:
                print(f"  WARNING: Not a v2 manifest in {manifest_path}")
                continue
            
            if manifest_errors == 0:
                print("  SUCCESS: All checks passed.")
            else:
                total_errors += manifest_errors
    
    return total_errors


def test_manifests(config):
    """
    Tests all generated manifests in the presentation directory.
    - Checks if manifest files are valid JSON.
    - Checks if linked info.json and thumbnail files exist.
    - Tests v2 API version.
    """
    presentation_dir = os.path.join("public", "iiif", "presentation")
    total_errors = 0

    if not os.path.isdir(presentation_dir):
        print(f"ERROR: Presentation directory not found: {presentation_dir}")
        sys.exit(1)
    
    # Test manifests in the presentation directory
    total_errors += test_manifests_in_directory(presentation_dir, config)
    
    # Test root directory manifests (backward compatibility)
    print(f"\nScanning root manifests in {presentation_dir}...")
    for filename in sorted(os.listdir(presentation_dir)):
        if filename.endswith(".json"):
            manifest_path = os.path.join(presentation_dir, filename)
            print(f"\nTesting root manifest: {manifest_path}")
            manifest_errors = 0

            try:
                with open(manifest_path, "r") as f:
                    manifest = json.load(f)
            except json.JSONDecodeError:
                print(f"  FAIL: Invalid JSON in {manifest_path}")
                total_errors += 1
                continue
            
            # Check if it's a v2 manifest
            context = manifest.get("@context", "")
            if "presentation/2" in context:
                manifest_errors = test_manifest_v2(manifest, "public")
            else:
                print(f"  WARNING: Not a v2 manifest in {manifest_path}")
                continue
            
            if manifest_errors == 0:
                print("  SUCCESS: All checks passed.")
            else:
                total_errors += manifest_errors

    return total_errors


def main():
    """Main function to run the smoke tests."""
    try:
        logger.info("--- Running Smoke Tests ---")
        
        # Load and validate configuration
        logger.info("Loading configuration...")
        config = load_config()
        logger.info("Configuration loaded and validated successfully")
        
        # Validate directories
        logger.info("Validating directories...")
        validate_directories(config)
        
        # Run tests
        logger.info("Running manifest tests...")
        errors = test_manifests(config)

        if errors == 0:
            logger.info("--- All tests passed! ---")
            sys.exit(0)
        else:
            logger.error(f"--- Tests finished with {errors} error(s). ---")
            sys.exit(1)
            
    except ConfigValidationError as e:
        logger.error(f"Configuration validation failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error in smoke tests: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()