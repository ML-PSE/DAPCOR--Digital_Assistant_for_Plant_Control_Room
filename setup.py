from setuptools import find_packages, setup
import os

def parse_requirements(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    with open(filename, "r") as f:
        return [line.strip() for line in f if line and not line.startswith("#")]

with open("README.md", "r", encoding="utf-8", errors="ignore") as fh:
    long_description = fh.read()

version = {}
with open("DAPCOR/_version.py", encoding="utf-8") as fp:
    exec(fp.read(), version)


setup(
    name="DAPCOR",
    version=version["__version__"],
    description="Build and run an AI-powered Virtual Assistant.",
    author="Ankur Kumar",
    author_email="ProcessIndustryAI@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ML-PSE/DAPCOR--Digital_Assistant_for_Plant_Control_Room",
    packages=find_packages(),
    install_requires=parse_requirements("requirements.txt"),
    python_requires=">=3.9",
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)
