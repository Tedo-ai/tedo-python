from setuptools import setup, find_packages

setup(
    name="tedo",
    version="0.2.0",
    description="Official Python SDK for the Tedo API",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.28",
    ],
)
