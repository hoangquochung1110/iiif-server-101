# Makefile for IIIF All-Static Starter

# Use the python interpreter from the virtual environment
PYTHON = venv/bin/python

# Phony targets don't represent files
.PHONY: all tiles manifests serve clean test install-deps generate-metadata

# Target to generate metadata.csv from images
generate-metadata:
	@echo "Generating metadata.csv from images in data/masters/..."
	@$(PYTHON) src/generate_metadata.py

# Default target
all: generate-metadata tiles manifests

# Target to generate image tiles
tiles:
	@echo "Generating IIIF image tiles..."
	@$(PYTHON) src/tile_level2_static.py	

# Target to generate IIIF manifests (v2 only)
manifests: tiles
	@echo "Generating IIIF v2 manifests..."
	@$(PYTHON) src/build_manifest.py

# Target to serve the public directory
serve:
	@echo "Starting local server at http://localhost:8080/"
	@$(PYTHON) -m http.server -d public 8080

# Target to clean generated files
clean:
	@echo "Cleaning generated IIIF files..."
	@rm -rf public/iiif/2/*
	@rm -rf public/iiif/presentation/*

# Target to run smoke tests
test: manifests
	@echo "Running smoke tests..."
	@$(PYTHON) src/smoke_test.py

# Target to install dependencies
install-deps:
	@echo "Installing Python dependencies..."
	@pip install -r requirements.txt