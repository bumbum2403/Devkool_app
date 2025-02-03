from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:  # Read README for long description
    long_description = f.read()

setup(
    name="devkool",
    version="0.1.1",  # Update version on next release
    description="AI-Powered API Management CLI",  # Short description
    long_description=long_description,  # Long description from README
    long_description_content_type="text/markdown",  # Important for Markdown README
    author="Shubham Dwivedi",  # Replace with your name
    author_email="sd.shubham2403@gmail.com",  
    url="https://github.com/bumbum2403/Devkool_app",  
    packages=find_packages(),
    install_requires=[
        "typer",
        "cryptography",
        "transformers",
        "requests",
        "httpx",
        "requests-toolbelt" #add this as well
        # ... other dependencies
    ],
    entry_points={
        "console_scripts": [
            "devkool = devkool.main:app",
        ],
    },
    classifiers=[  # for PyPi categorisations
        "Development Status :: 3 - Alpha",  # Or "4 - Beta", "5 - Production/Stable" as you progress
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License", 
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",  # Add other supported versions
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11"
    ],
    keywords="api, management, testing, ai, cli, developer tools",  
)