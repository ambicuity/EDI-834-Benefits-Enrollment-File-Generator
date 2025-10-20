from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="edi834-generator",
    version="1.0.0",
    author="Ritesh Rana",
    description="EDI 834 Benefits Enrollment File Generator - Convert CSV enrollment data to ANSI X12 834 format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ambicuity/EDI-834-Benefits-Enrollment-File-Generator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Office/Business",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "edi834-cli=edi834.cli:main",
        ],
    },
    package_data={
        "edi834": ["config/*.yaml"],
    },
    include_package_data=True,
)
