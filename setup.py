import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

with (HERE / "requirements.txt").open() as f:
    requirements = f.read().splitlines()

setup(
    name="pygeonhole-cli",
    version="0.1.0",
    description="python cli program to organize files",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/betterthan-yesterday/file-organizer",
    author="betterthan-yesterday",
    author_email="polwilliam0@gmail.com",
    # license="MIT",
    entry_points={
        'console_scripts': [
            'pygeonhole-cli = pygeonhole.__main__:main',
        ],
    },
    python_requires='>=3.8',
    # classifiers=[
    #     "License :: OSI Approved :: MIT License",
    #     "Programming Language :: Python :: 3",
    # ],
    packages=["pygeonhole"],
    include_package_data=True,
    install_requires=requirements,
)