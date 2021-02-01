from setuptools import setup

setup(
    name='stepik',
    version='0.1',
    py_modules=['stepik'],
    install_requires=[
        'Click',
        'requests',
        'colorama',
        'html2text'
    ],
    entry_points='''
        [console_scripts]
        stepik=stepik:main
    ''',
)
