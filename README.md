# IIIF All-Static Starter

This repository provides a complete, static-only solution for serving IIIF Image API Level 0 and Presentation API v3 content. It is designed to be deployed on simple object storage (like AWS S3, Cloudflare R2, or Backblaze B2) and served via a CDN, eliminating the need for a dedicated IIIF image server.

## The Problem & Our Solution

### The Challenge with High-Resolution Images

1.  **Digitizing Large-Format Materials:** When digitizing maps, manuscripts, or large-scale artworks, the source images are often massive (hundreds of MBs or even GBs).
    *   **Web Performance:** Delivering these large files directly to a web browser results in slow load times and can easily crash the user's browser.
    *   **Bandwidth Costs:** It consumes an enormous amount of bandwidth.
    *   **User Experience:** Viewers typically only need to zoom and pan to see details, not download the entire file at once.

2.  **The Dynamic Solution (Traditional Image Servers):**
    *   **How they work:** Image servers like Cantaloupe, Loris, or IIPImage dynamically process images on-demand (cropping, resizing, etc.).
    *   **The downside:** They require a server to be running 24/7, consuming CPU and RAM. The infrastructure is complex to set up and maintain, leading to high operational costs, especially for non-profit organizations.

3.  **The Metadata Challenge:**
    *   Libraries and museums need to present digital materials with rich structural context (e.g., a multi-page book, a map with annotations).
    *   Without a standard like IIIF, each institution might invent its own proprietary format, leading to a lack of interoperability between collections and viewers.

### The "All-Static" Solution (This Project)

This project offers a simple, cost-effective, and powerful alternative.

1.  **Standardized Image Delivery (IIIF Image API Level 0):**
    *   Source images are **pre-processed** into static tiles and an `info.json` file.
    *   These static assets are served via a Content Delivery Network (CDN).
    *   Users can zoom and pan smoothly, as the viewer only loads the specific tiles needed for the current view.

2.  **Standardized Metadata (IIIF Presentation API v3):**
    *   Metadata and structural information are compiled into a static JSON-LD file called a **manifest**.
    *   Any IIIF-compliant viewer (like Mirador or the Universal Viewer) can instantly read this manifest to render a rich, interactive user experience.

3.  **No Dynamic Image Server Required:**
    *   By pre-generating everything, we eliminate the need for a 24/7 server.
    *   Deployment is as simple as uploading a folder of static files to an object storage provider (like Cloudflare R2, Backblaze B2, or AWS S3).
    *   This results in **extremely low costs**, making it a perfect fit for cultural heritage institutions, researchers, and non-profits.


## Features

-   **IIIF Image API Level 0:** Generates pre-cut image tiles and an `info.json` file for each source image.
-   **IIIF Presentation API v3:** Creates IIIF manifests from a simple CSV metadata file.
-   **Static & Serverless:** No runtime dependencies, making it cheap to host and easy to maintain.
-   **Automated Workflow:** Uses a `Makefile` to streamline the build process.
-   **Customizable:** Configuration is managed through a simple `config.yaml` file.

## Project Structure

```
.
├─ README.md
├─ INSTALL.md
├─ config/config.yaml
├─ data/masters/            # Source images go here
├─ data/metadata.csv        # Metadata for manifests
├─ public/                  # Output directory (deploy this)
│   └─ iiif/
│       ├─ 2/               # Image API tiles + info.json
│       └─ presentation/    # Presentation API manifests
├─ src/                     # Python scripts
│   ├─ tile_level0.py
│   ├─ build_manifest.py
│   └─ smoke_test.py
├─ Makefile
├─ requirements.txt
└─ venv/                    # Python virtual environment
```

## Getting Started

For detailed setup instructions, please see [INSTALL.md](./INSTALL.md).

## Onboarding Workflow

The diagram below illustrates the end-to-end workflow, from adding your data to deploying the static IIIF assets.

```
                                     +-------------------------+
                                     |   Your Data             |
                                     |-------------------------|
                                     | 🖼️ data/masters/*.jpg   |
                                     | 📄 data/metadata.csv    |
                                     +-----------+-------------+
                                                 |
                                                 | (You add/edit these)
                                                 v
+---------------------------------+    +-------------------------+
|   IIIF All-Static Starter       |    |   Makefile Commands     |
|---------------------------------|    |-------------------------|
| 🐍 src/tile_level0.py           |    | 🔨 make all             |
| 🐍 src/build_manifest.py        |    | 🖼️ make tiles           |
| 🐍 src/smoke_test.py            |    | 📄 make manifests       |
| ⚙️ config/config.yaml          |    | 🧪 make test            |
+---------------------------------+    | 🚀 make serve           |
               ^                       | 🧹 make clean           |
               |                       +-----------+-------------+
               | (Reads config)                    |
               |                                   | (You run these)
               +-----------------------------------+
                                                 |
                                                 v
                                     +-------------------------+
                                     |   Generated Output      |
                                     |-------------------------|
                                     | 🌍 public/              |
                                     |    ├── iiif/2/ (tiles)  |
                                     |    └── p/ (manifests)   |
                                     +-----------+-------------+
                                                 |
                                                 | (Deploy this folder)
                                                 v
                                     +-------------------------+
                                     |   Deployment Target     |
                                     |-------------------------|
                                     | ☁️ Cloudflare R2         |
                                     | ☁️ AWS S3 / CloudFront  |
                                     | ☁️ Backblaze B2         |
                                     +-------------------------+
```

### Quick Start

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Add source images:**
    Place your high-resolution source images in the `data/masters/` directory.

3.  **Update metadata:**
    Edit `data/metadata.csv` to describe your images and group them into objects.

4.  **Build everything:**
    ```bash
    make all
    ```

## Makefile Commands

This project uses a `Makefile` to automate common tasks.

-   `make all`
    Builds everything: runs `tiles` and then `manifests`.

-   `make tiles`
    Generates image tiles and `info.json` files from the images in `data/masters/`.

-   `make manifests`
    Creates IIIF Presentation v3 manifests from `data/metadata.csv`.

-   `make test`
    Runs smoke tests to validate the generated output.

-   `make serve`
    Starts a local web server to preview the `public` directory at `http://localhost:8080`.

-   `make clean`
    Removes all generated files in the `public` directory.

## How It Works

1.  **Image Tiling (`make tiles`):**
    The `src/tile_level0.py` script reads each image from `data/masters/`, creates a corresponding `info.json` with basic details, and generates a pyramid of static image tiles according to the settings in `config/config.yaml`.

2.  **Manifest Generation (`make manifests`):**
    The `src/build_manifest.py` script reads `data/metadata.csv`, groups images into their respective objects, and constructs a IIIF Presentation v3 manifest for each object. It links to the `info.json` files created in the previous step.

## Deployment

To deploy, simply upload the contents of the `public` directory to your object storage provider and configure it for public access through a CDN. Ensure that the `iiif_base_url` in `config.yaml` matches your public-facing URL.
