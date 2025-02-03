import typer
import json
import requests
import os
from transformers import pipeline
import uuid  # For generating unique IDs
from cryptography.fernet import Fernet
from transformers import pipeline
import re  # For input validation
import logging  # For better logging
from devkool import scanner
app = typer.Typer()
import time
# File to store encrypted API details
API_STORAGE_FILE = "api_store.json"
KEY_FILE = "secret.key" 
LOG_FILE = "devkool.log"

# Configure logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
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
    try:
        if os.path.exists(API_STORAGE_FILE):
            with open(API_STORAGE_FILE, "r") as file:
                return json.load(file)
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON: {e}")
        return {}  # Return empty dict on error


def save_api_store(data):
    try:
        with open(API_STORAGE_FILE, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        logging.error(f"Error saving API store: {e}")


def is_valid_url(url):
    # Improved URL validation using regex
    regex = re.compile(
        r"^(?:http(s)://)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$", re.IGNORECASE
    )
    return re.match(regex, url) is not None



@app.command()
def track():
    """Scan the codebase for untracked API endpoints."""
    try:
        api_store = load_api_store()  # Load tracked APIs
        untracked_apis = scanner.find_untracked_apis("./", api_store) # "." means scan the current project directory
        if untracked_apis:
            typer.echo("⚠️ Untracked APIs found:")
            for api in untracked_apis:
                typer.echo(f"  - {api}")
            typer.echo("💡 Suggestion: Use 'devkool add <api_key> <endpoint>' to track these APIs.")
        else:
            typer.echo("✅ No untracked APIs found.")
    except Exception as e:
        typer.echo(f"❌ Error during tracking: {e}")
        logging.exception(f"Error during tracking: {e}")



def categorize_api(endpoint):
    try:
        classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        candidate_labels = ["Authentication", "Payments", "Social Media", "Weather", "Finance", "E-commerce", "Healthcare", "Database", "Storage", "Messaging", "AI/ML"] #added more labels
        result = classifier(endpoint, candidate_labels)
        category = result["labels"][0]
        confidence = result["scores"][0]

        if confidence < 0.5: # Set a confidence threshold
            category = "Uncategorized"
            logging.warning(f"Low confidence ({confidence}) for categorization of {endpoint}. Assigned to 'Uncategorized'.")
        return category
    except Exception as e:
        logging.error(f"Error during categorization: {e}")
        return "Uncategorized" # Default if error


@app.command()
def add(api_key: str, endpoint: str):
    generate_key()
    api_store = load_api_store()

    if not is_valid_url(endpoint):
        typer.echo("❌ Invalid URL format!")
        return

    try:
        api_id = str(uuid.uuid4())  # Generate a unique ID
        encrypted_key = encrypt_data(api_key)
        encrypted_endpoint = encrypt_data(endpoint)
        category = categorize_api(endpoint)

        api_store[api_id] = {"api_key": encrypted_key, "endpoint": encrypted_endpoint, "category": category}
        save_api_store(api_store)

        typer.echo(f"✅ API stored securely! ID: {api_id}, Category: {category}")
        logging.info(f"API added: ID: {api_id}, Endpoint: {endpoint}, Category: {category}")
    except Exception as e:
        typer.echo(f"❌ Error adding API: {e}")
        logging.exception(f"Error adding API: {e}") # Log the full traceback


@app.command()
def list():
    generate_key()
    api_store = load_api_store()

    if not api_store:
        typer.echo("No APIs stored yet.")
        return

    typer.echo("🔐 Stored APIs:")
    for api_id, details in api_store.items():
        try:
            key = decrypt_data(details["api_key"])
            endpoint = decrypt_data(details["endpoint"])
            category = details["category"]
            typer.echo(f"🔑 {key} → 🌐 {endpoint} (ID: {api_id}) 🏷️ Category: {category}")
        except Exception as e:
            typer.echo(f"❌ Error decrypting an entry: {e}")
            logging.error(f"Error decrypting API data for ID {api_id}: {e}")

@app.command()
def update(api_id: str, new_api_key: str = None, new_endpoint: str = None):
    generate_key()
    api_store = load_api_store()

    if api_id not in api_store:
        typer.echo("❌ API ID not found!")
        return

    try:
        data = api_store[api_id]

        if new_api_key:
            encrypted_new_key = encrypt_data(new_api_key)
        else:
            encrypted_new_key = data["api_key"]

        if new_endpoint:
            if not is_valid_url(new_endpoint):
                typer.echo("❌ Invalid URL format for new endpoint!")
                return
            encrypted_new_endpoint = encrypt_data(new_endpoint)
            category = categorize_api(new_endpoint)  # Recategorize if endpoint changes
        else:
            encrypted_new_endpoint = data["endpoint"]
            category = data["category"]

        api_store[api_id] = {"api_key": encrypted_new_key, "endpoint": encrypted_new_endpoint, "category": category}
        save_api_store(api_store)

        typer.echo("✅ API updated successfully!")
        logging.info(f"API updated: ID: {api_id}")
    except Exception as e:
        typer.echo(f"❌ Error updating API: {e}")
        logging.exception(f"Error updating API for ID {api_id}: {e}")

@app.command()
def delete(api_id: str):
    generate_key()
    api_store = load_api_store()

    if api_id in api_store:
        try:
            del api_store[api_id]
            save_api_store(api_store)
            typer.echo("✅ API deleted successfully!")
            logging.info(f"API deleted: ID: {api_id}")
        except Exception as e:
            typer.echo(f"❌ Error deleting API: {e}")
            logging.exception(f"Error deleting API for ID {api_id}: {e}")
    else:
        typer.echo("❌ API ID not found!")




def generate_test_cases(api_spec, endpoint, api_key):
    test_cases = []
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    for path, methods in api_spec["paths"].items():
        for method, details in methods.items():
            description = details.get("summary", "No description provided in API spec") #handle missing summary
            if description == "No description provided in API spec":
                description = "No Description Provided" #default description
            candidate_labels = ["Positive", "Negative", "Boundary", "Error", "Security", "Performance"]
            result = classifier(description, candidate_labels)
            test_type = result["labels"][0]

            test_case = {
                "endpoint": endpoint + path,
                "method": method.upper(),
                "description": f"[{test_type}] {description}",
                "headers": {"": api_key}, #correct header for rapid api
            }
            if method == "post" or method == "put":
                test_case["request_body"] = {}
            test_cases.append(test_case)
    return test_cases


@app.command()
def test(api_id: str, api_spec_path: str):
    """Generate and run tests for an API."""
    try:
        api_store = load_api_store()
        if api_id not in api_store:
            typer.echo("❌ API ID not found!")
            return

        api_details = api_store[api_id]
        endpoint = scanner.decrypt_data(api_details["endpoint"])
        api_key = scanner.decrypt_data(api_details["api_key"])

        # Load API spec
        with open(api_spec_path, "r") as f:
            api_spec = json.load(f)

        test_cases = generate_test_cases(api_spec, endpoint, api_key)

        for test_case in test_cases:
            print(test_case["description"])

            # Execute the test case (using requests or httpx)
            try:
                if test_case["method"] == "GET":
                    response = requests.get(test_case["endpoint"], headers=test_case["headers"])
                elif test_case["method"] == "POST":
                    response = requests.post(test_case["endpoint"], headers=test_case["headers"], json=test_case.get("request_body")) #added request body if any
                elif test_case["method"] == "PUT":
                    response = requests.put(test_case["endpoint"], headers=test_case["headers"], json=test_case.get("request_body"))
                elif test_case["method"] == "DELETE":
                    response = requests.delete(test_case["endpoint"], headers=test_case["headers"])
                # Add other HTTP methods as needed

                response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

                print(f"  ✅ Status Code: {response.status_code}")
                # You can add more assertions here to check the response body, headers, etc.

            except requests.exceptions.RequestException as e:
                print(f"  ❌ Request Error: {e}")
            except Exception as e:
                print(f"  ❌ Test Error: {e}")

            time.sleep(2)


    except FileNotFoundError:
        typer.echo(f"❌ API specification file not found: {api_spec_path}")
    except json.JSONDecodeError:
        typer.echo(f"❌ Invalid JSON format in API specification file: {api_spec_path}")
    except Exception as e:
        typer.echo(f"❌ Error during testing: {e}")
        logging.exception(f"Error during testing: {e}")



if __name__ == "__main__":
    # Check for the encryption key in the environment variables
    if "DEVKOOL_KEY" not in os.environ:
        if not os.path.exists(KEY_FILE):  # Only generate if NOT in env vars
            generate_key()
        logging.warning("Encryption key is not set in environment variables.  Using the key file. This is not recommended for production.")
    app()
