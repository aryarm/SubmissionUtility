from setuptools import find_packages, setup

setup(
    name='stepik',
    version='0.2.0',
    py_modules=['stepik'],
    install_requires=[
        'click',
        'requests',
        'colorama',
        'html2text'
    ],
    packages=find_packages(include=['stepik', 'stepik.client', 'stepik.models']),
    entry_points={
        'console_scripts': ['stepik=stepik.__main__:main']
    },
)
