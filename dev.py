from setuptools import setup, find_packages

setup(
    name="dishu-cli",
    version="1.0.0",
    description="DishuAi: Advanced AI coding agent for building real-world software.",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "typer>=0.9.0",
        "rich>=13.0.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "dishu=dishu.cli:app",
        ],
    },
    python_requires=">=3.8",
)
