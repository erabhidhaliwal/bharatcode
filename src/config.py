from setuptools import setup, find_packages

setup(
    name="bharatcode",
    version="1.0.0",
    description="BharatCode: Open-source AI coding agent with multi-model support",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "typer>=0.9.0",
        "rich>=13.0.0",
        "python-dotenv>=1.0.0",
        "requests>=2.28.0",
    ],
    entry_points={
        "console_scripts": [
            "bharat=src.main:main",
        ],
    },
    python_requires=">=3.8",
)
