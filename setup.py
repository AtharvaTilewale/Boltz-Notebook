from setuptools import setup, find_packages

setup(
    name="logger",  # package name
    version="0.1.0",
    packages=find_packages(),
    install_requires=["requests"],  # dependencies
    author="Atharva Tilewale",
    description="Simple Google Sheets logger for Colab notebooks",
    url="https://github.com/AtharvaTilewale/Boltz-Notebook",
    python_requires=">=3.6",
)
