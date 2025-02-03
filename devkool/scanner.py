import ast
import os
import re
from urllib.parse import urlparse
from cryptography.fernet import Fernet

def find_untracked_apis(project_dir, api_store):
    """Scan the codebase for untracked API endpoints."""
    untracked_apis = set()

    for root, _, files in os.walk(project_dir):
        for file in files:
            if file.endswith(".py"):  # Only scan Python files
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r") as f:
                        code = f.read()
                        tree = ast.parse(code)
                        untracked_apis.update(extract_api_endpoints(tree, api_store))
                except Exception as e:
                    print(f"Error scanning {file_path}: {e}")  # Handle errors gracefully

    return list(untracked_apis)

def extract_api_endpoints(tree, api_store):
    """Extract API endpoints from the AST."""
    extracted_apis = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Check for common API call patterns (requests, httpx, etc.)
            if is_api_call(node):
                try:
                    url = extract_url_from_call(node)
                    if url:
                        parsed_url = urlparse(url)  #to handle relative paths
                        if parsed_url.scheme and parsed_url.netloc: #check if it is an absolute url
                          if not is_api_tracked(url, api_store):
                              extracted_apis.add(url)
                except Exception as e:
                    print(f"Error extracting URL: {e}")
                    continue #continue to the next if there is an error.

    return extracted_apis


def is_api_call(node):
    """Check if the ast.Call node is likely an API call."""
    # Add more patterns as needed (e.g., other libraries, custom wrappers)
    call_names = ["get", "post", "put", "delete", "patch", "options", "head"]
    if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
        return node.func.attr in call_names and node.func.value.id in ["requests", "httpx"] #check if it is requests or httpx
    elif isinstance(node.func, ast.Name):
        return node.func.id in call_names #if it is a direct call, without the module name
    return False

def extract_url_from_call(node):
    """Extract the URL from the ast.Call node."""
    # Handle different ways URL might be passed (e.g., positional arg, keyword arg)
    if isinstance(node.args[0], ast.Constant):
        return node.args[0].value
    elif isinstance(node.keywords):
        for kw in node.keywords:
            if kw.arg == "url" and isinstance(kw.value, ast.Constant):
                return kw.value.value
    return None #if url is not found


def is_api_tracked(url, api_store):
    """Check if the API endpoint is already tracked."""
    for _, details in api_store.items():
        if decrypt_data(details["endpoint"]) == url:
            return True
    return False

# ... (Encryption/decryption functions from main.py - move them here)


def generate_key():
    """Generate and store a secret key if not already created"""
    KEY_FILE = "secret.key"
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)


def load_key():
    """Load the encryption key"""
    KEY_FILE = "secret.key"
    return open(KEY_FILE, "rb").read()


def encrypt_data(data):
    """Encrypt data using AES"""
    key = load_key()
    cipher = Fernet(key)
    return cipher.encrypt(data.encode()).decode()


def decrypt_data(data):
    """Decrypt data using AES"""
    key = load_key()
    cipher = Fernet(key)
    return cipher.decrypt(data.encode()).decode()