#!/usr/bin/env python3
"""
Setup script for EMBL-EBI Proteins API MCP Server
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="embl-ebi-proteins-mcp",
    version="1.0.0",
    author="EMBL-EBI MCP Team",
    author_email="support@ebi.ac.uk",
    description="Claude-compatible MCP server for EMBL-EBI Proteins REST API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/embl-ebi-proteins-mcp",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "embl-ebi-mcp=embl_ebi_proteins_mcp.main:main",
        ],
    },
    keywords="mcp, claude, embl-ebi, uniprot, proteins, bioinformatics",
    project_urls={
        "Bug Reports": "https://github.com/your-org/embl-ebi-proteins-mcp/issues",
        "Source": "https://github.com/your-org/embl-ebi-proteins-mcp",
        "Documentation": "https://www.ebi.ac.uk/proteins/api/doc/",
    },
)