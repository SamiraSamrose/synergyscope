# File: backend/setup.py
# Purpose: Package setup configuration

"""
SynergyScope Backend Setup
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="synergyscope",
    version="1.0.0",
    author="SynergyScope Team",
    description="AI Agents for Team Adaptation and Meta Evolution",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/synergyscope",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.5.0",
        "boto3>=1.34.10",
        "torch>=2.1.0",
        "torch-geometric>=2.4.0",
        "scikit-learn>=1.3.2",
        "numpy>=1.24.3",
        "pandas>=2.1.3",
    ],
)