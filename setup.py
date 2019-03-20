from setuptools import setup, find_packages

with open("README.md") as f:
    long_description = f.read()

setup(
    author="minamorl",
    author_email="minamorl@minamorl.com",
    name="trishula",
    url="https://github.com/minamorl/trishula",
    description="The modern PEG parser combinator for python",
    long_description=long_description,
    long_description_content_type='text/markdown',
    version="0.0.9",
    packages=find_packages(),
)
