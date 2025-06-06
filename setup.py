from setuptools import setup, find_packages

setup(
    name="para-bank-ui-automation",
    version="0.1.0",
    packages=find_packages(include=["src", "src.*", "tests", "tests.*"]),
    package_dir={"": "."},
    install_requires=[
        "pytest",
        "pytest-html",
        "pytest-playwright",
        "playwright",
        "python-dotenv",
    ],
    python_requires=">=3.10",
) 