# Project Installation

This guide provides instructions on how to set up the project environment for development and execution.

## Prerequisites

- Python 3.11 or later

## Setup Instructions

1.  **Clone the repository (if you haven't already):**

    ```bash
    git clone <repository-url>
    cd iiif-all-static-starter
    ```

2.  **Create a Python virtual environment:**

    This project uses a virtual environment to manage dependencies and isolate it from other Python projects. The following command will create a directory named `venv` in the project root.

    ```bash
    python3 -m venv venv
    ```

3.  **Activate the virtual environment:**

    Before installing dependencies or running the scripts, you need to activate the virtual environment.

    -   On **macOS and Linux**:

        ```bash
        source venv/bin/activate
        ```

    -   On **Windows**:

        ```bash
        .\venv\Scripts\activate
        ```

    Once activated, your shell prompt will be prefixed with `(venv)`.

4.  **Install dependencies:**

    Install the required Python packages using the `requirements.txt` file.

    ```bash
    pip install -r requirements.txt
    ```

5.  **Ready to Go!**

    The environment is now set up. You can proceed to run the build scripts as described in the main `README.md`.

## Running Tests

To ensure that the generated IIIF resources are valid and all links are correct, you can run the smoke tests using Make:

```bash
make test
```

This command will first build the image tiles and manifests (if they don't exist) and then run the `smoke_test.py` script to verify the output.