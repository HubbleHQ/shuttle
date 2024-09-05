import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hubble_shuttle",
    version="0.5.0",
    author="HubbleHQ",
    author_email="dev@hubblehq.com",
    description="Hubble's Shuttle",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HubbleHQ/shuttle",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
