from setuptools import setup, find_packages

setup(
    name="contract-compliance-checker",
    version="1.0.0",
    description="Multi-Agent AI Contract Compliance & Legal Risk Auditor",
    author="rdaniel1206",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "pdf": ["pypdf>=3.0.0"],
        "docx": ["python-docx>=0.8.11"],
        "dev": ["pytest>=7.0.0"]
    },
    entry_points={
        "console_scripts": [
            "contract-checker=app:interactive_cli",
            "contract-web=web_app:run_server"
        ]
    }
)
