# Devkool: AI-Powered API Management CLI

Devkool is a command-line interface (CLI) tool designed to help developers efficiently manage, test, and interact with APIs.  It leverages AI for enhanced test case generation and provides features for tracking untracked APIs in your codebase.  Devkool aims to streamline the API development workflow and improve developer productivity.

## Features

*   Secure API Storage:  API keys and endpoints are securely stored using encryption.
*   AI-Powered Test Case Generation: Generates test case descriptions from API specifications (OpenAPI/Swagger).
*   Untracked API Detection: Scans your codebase to identify API endpoints that are being used but are not yet tracked by Devkool.
*   CLI Interface:  Easy-to-use command-line interface for all functionalities.

## Installation

1.  Clone the Repository:

    ```bash
    git clone [https://github.com/](https://github.com/)<your_username>/devkool.git  # Replace with your repo URL
    cd devkool
    ```

2.  Create a Virtual Environment (Recommended):

    ```bash
    python3 -m venv venv  # Create a virtual environment
    source venv/bin/activate  # Activate the environment (Linux/macOS)
    venv\Scripts\activate  # Activate the environment (Windows)
    ```

3.  Install Devkool:

    ```bash
    pip install -e .
    ```

## Configuration

### Encryption Key

Devkool uses encryption to secure stored API keys and endpoints.  It's crucial to set a strong encryption key.

1.  Generate a Key:

    *   Linux/macOS:

        ```bash
        export DEVKOOL_KEY=$(python3 -c "import base64; import os; print(base64.b64encode(os.urandom(32)).decode('utf-8'))")
        ```

    *   Windows (PowerShell):

        ```powershell
        $env:DEVKOOL_KEY = [Convert]::ToBase64String((New-Object System.Security.Cryptography.RNGCryptoServiceProvider).GetBytes(32))
        ```

2.  Set the Environment Variable:

    *   Linux/macOS: Add the `export DEVKOOL_KEY=...` command (the one from step 1) to your shell's configuration file (e.g., `~/.bashrc`, `~/.zshrc`, `~/.profile`).  This will make the environment variable persistent across terminal sessions. Then source the configuration file using `source ~/.zshrc` or restart your terminal.
    *   Windows:
        *   Search for "Environment Variables" in the Windows search bar.
        *   Click "Edit the system environment variables."
        *   In the System Properties window, click "Environment Variables..."
        *   Create a new system or user variable named `DEVKOOL_KEY` and paste the generated key as the value.

## Usage

### Adding an API

```bash
devkool add <api_key> <endpoint>


