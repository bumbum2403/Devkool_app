import typer
import json
import os
from cryptography.fernet import Fernet

app = typer.Typer()

# File to store encrypted API details
API_STORAGE_FILE = "api_store.json"
KEY_FILE = "secret.key"


def generate_key():
    """Generate and store a secret key if not already created"""
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)


def load_key():
    """Load the encryption key"""
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


def load_api_store():
    """Load the stored API data"""
    if os.path.exists(API_STORAGE_FILE):
        with open(API_STORAGE_FILE, "r") as file:
            return json.load(file)
    return {}


def save_api_store(data):
    """Save the encrypted API data"""
    with open(API_STORAGE_FILE, "w") as file:
        json.dump(data, file, indent=4)


@app.command()
def add(api_key: str, endpoint: str):
    """Add an API key and endpoint securely"""
    generate_key()  # Ensure key exists
    api_store = load_api_store()

    encrypted_key = encrypt_data(api_key)
    encrypted_endpoint = encrypt_data(endpoint)

    api_store[encrypted_key] = encrypted_endpoint
    save_api_store(api_store)

    typer.echo("✅ API stored securely!")


@app.command()
def list():
    """List stored API keys and endpoints (decrypted)"""
    generate_key()
    api_store = load_api_store()

    if not api_store:
        typer.echo("No APIs stored yet.")
        return

    typer.echo("🔐 Stored APIs:")
    for enc_key, enc_endpoint in api_store.items():
        try:
            key = decrypt_data(enc_key)
            endpoint = decrypt_data(enc_endpoint)
            typer.echo(f"🔑 {key} → 🌐 {endpoint}")
        except Exception:
            typer.echo("❌ Error decrypting an entry, skipping...")


if __name__ == "__main__":
    app()
