from setuptools import setup, find_packages

setup(
    name="devkool",
    version="0.2.0",  # Update version
    packages=find_packages(),
    install_requires=[
        "typer",
        "cryptography",
        "transformers",
        "requests",  # Add requests dependency
        "httpx" #add httpx dependency
        # ... other dependencies
    ],
    entry_points={
        "console_scripts": [
            "devkool = devkool.main:app",
        ],
    },
)