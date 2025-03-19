from setuptools import setup, find_packages

setup(
    name="fb_scrapper",
    version="0.0.1",
    author="IQLynxAI",
    author_email="iqlynx.ai@gmail.com",
    description="A Python library for web scraping",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/IQLynxAI/fb-scrapper-lib.git",
    packages=find_packages(),
    install_requires=[
        "selectolax",
        "curl_cffi"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    keywords="facebook page scraper, scrape facebook page info, facebook data scraper, facebook page info extractor, python facebook scraper",
)
