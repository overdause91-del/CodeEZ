from setuptools import setup, find_packages

setup(
    name="codeez",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "anthropic>=0.30.0",
        "google-genai>=1.0.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "codeez=codeez.main:main",
        ],
    },
)
