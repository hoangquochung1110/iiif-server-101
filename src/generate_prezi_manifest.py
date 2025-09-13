"""Generate an IIIF Presentation API v2 manifest using ``iiif-prezi``.

The script scans a directory of local images and writes a manifest that
references the originals at a remote base URL (e.g. a Cloudflare R2 bucket).
"""

from pathlib import Path
import argparse

from PIL import Image
from iiif_prezi.factory import ManifestFactory


def generate_manifest(image_dir: Path, base_url: str, label: str, output: Path) -> None:
    """Build a manifest for all images in ``image_dir``.

    ``base_url`` should point to the directory that contains the original
    images (e.g. ``https://example.com/master``).
    """
    factory = ManifestFactory()
    # iiif-prezi requires a base Presentation URI before creating resources
    factory.set_base_prezi_uri(base_url)
    manifest = factory.manifest(ident="manifest", label=label)
    seq = manifest.sequence(ident="sequence-0")

    for path in sorted(image_dir.iterdir()):
        if not path.suffix.lower() in {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".gif", ".webp"}:
            continue

        with Image.open(path) as img:
            width, height = img.size

        canvas = seq.canvas(ident=path.stem, label=path.name)
        canvas.set_hw(height, width)

        anno = canvas.annotation()
        img_url = f"{base_url.rstrip('/')}/{path.name}"
        img_res = anno.image(ident=img_url, iiif=False)
        img_res.set_hw(height, width)

    output.write_text(manifest.toString(compact=False), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate IIIF v2 manifest with iiif-prezi")
    parser.add_argument("--image-dir", type=Path, default=Path("data/masters"),
                        help="Directory containing local images")
    parser.add_argument("--base-url", required=True,
                        help="Base URL where the original images are hosted")
    parser.add_argument("--label", default="R2 Manifest", help="Label for the manifest")
    parser.add_argument("--output", type=Path, default=Path("manifest.json"),
                        help="Path to output manifest JSON")
    args = parser.parse_args()
    generate_manifest(args.image_dir, args.base_url, args.label, args.output)


if __name__ == "__main__":
    main()
