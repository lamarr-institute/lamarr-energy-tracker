from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lamarr-energy-tracker",
    version="0.1.1",
    author="Resource-aware ML Research Team @ Lamarr Institute",
    author_email="sebastian.buschjaeger@tu-dortmund.de",
    description="A CodeCarbon wrapper for tracking and reporting energy consumption of ML experiments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lamarr-institute/lamarr-energy-tracker",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "codecarbon==3.0.8",
        "argparse"
    ],
    extras_require={
        "test": [
            "pytest>=7.0.0",
            "pandas>=1.0.0",
        ],
    },
)