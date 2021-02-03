from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='stepik-cli',
    version='0.4.0',
    description="A Stepik CLI for students",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aryarm/stepik-cli",
    install_requires=[
        'click>=3.0',
        'requests',
        'colorama',
        'html2text'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(include=['stepik', 'stepik.client', 'stepik.models']),
    entry_points={
        'console_scripts': ['stepik=stepik.__main__:main']
    },
)
