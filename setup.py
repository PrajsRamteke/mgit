from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="multi-git-manager",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Manage multiple Git accounts on a single system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/multi-git-manager",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Version Control :: Git",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "pyyaml>=6.0",
        "rich>=12.0.0",
        "inquirer>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "mgit=cli:main",
        ],
    },
)