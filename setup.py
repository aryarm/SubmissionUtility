from setuptools import setup

setup(
    name='stepik',
    version='0.1.0',
    py_modules=['stepik'],
    install_requires=[
        'click',
        'requests',
        'colorama',
        'html2text'
    ],
    entry_points={
        'console_scripts': [
            stepik=stepik.stepik:main
        ]
    }
)
