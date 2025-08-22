import json
import os
import sys
from urllib.parse import urlparse

import yaml

# Smoke test to check the validity of generated IIIF resources.


def load_config():
    """Loads configuration from config.yaml."""
    config_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "config", "config.yaml"
    )
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"ERROR: Configuration file not found at {config_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"ERROR: Could not parse configuration file: {e}")
        sys.exit(1)


def check_file_exists(base_dir, url):
    """Checks if a file referenced by a URL exists on the local filesystem."""
    parsed_url = urlparse(url)
    # Assumes the path starts with /iiif/
    relative_path = parsed_url.path.lstrip("/")
    local_path = os.path.join(base_dir, relative_path)
    if not os.path.exists(local_path):
        print(f"  FAIL: File not found at {local_path} (from URL: {url})")
        return False
    print(f"  OK: Found {local_path}")
    return True


def test_manifests(config):
    """
    Tests all generated manifests in the presentation directory.
    - Checks if manifest files are valid JSON.
    - Checks if linked info.json and thumbnail files exist.
    """
    presentation_dir = os.path.join("public", "iiif", "presentation")
    public_dir = "public"
    iiif_base_url = config.get("iiif_base_url", "")
    total_errors = 0

    if not os.path.isdir(presentation_dir):
        print(f"ERROR: Presentation directory not found: {presentation_dir}")
        sys.exit(1)

    print(f"Scanning manifests in {presentation_dir}...")

    for filename in sorted(os.listdir(presentation_dir)):
        if filename.endswith(".json"):
            manifest_path = os.path.join(presentation_dir, filename)
            print(f"\nTesting manifest: {manifest_path}")
            manifest_errors = 0

            try:
                with open(manifest_path, "r") as f:
                    manifest = json.load(f)
            except json.JSONDecodeError:
                print(f"  FAIL: Invalid JSON in {manifest_path}")
                total_errors += 1
                continue

            # Check thumbnail
            if "thumbnail" in manifest and manifest["thumbnail"]:
                thumbnail_url = manifest["thumbnail"][0]["id"]
                if not check_file_exists(public_dir, thumbnail_url):
                    manifest_errors += 1

            # Check canvases and their images
            if "items" in manifest:
                for canvas in manifest["items"]:
                    if "items" in canvas and "items" in canvas["items"][0]:
                        image_service = canvas["items"][0]["items"][0]["body"]
                        if "service" in image_service:
                            info_url = image_service["service"][0]["id"]
                            # The ID in the service block is the folder, so append info.json
                            if not info_url.endswith("info.json"):
                                info_url = os.path.join(info_url, "info.json")

                            if not check_file_exists(public_dir, info_url):
                                manifest_errors += 1

            if manifest_errors == 0:
                print("  SUCCESS: All checks passed.")
            else:
                total_errors += manifest_errors

    return total_errors


def main():
    """Main function to run the smoke tests."""
    print("--- Running Smoke Tests ---")
    config = load_config()
    errors = test_manifests(config)

    if errors == 0:
        print("\n--- All tests passed! ---")
        sys.exit(0)
    else:
        print(f"\n--- Tests finished with {errors} error(s). ---")
        sys.exit(1)


if __name__ == "__main__":
    main()