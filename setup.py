from setuptools import setup

setup(
    name='submitter',
    version='0.3',
    py_modules=['submitter'],
    install_requires=[
        'Click',
        'requests',
        'colorama',
        'html2text'
    ],
    entry_points='''
        [console_scripts]
        submitter=submitter:main
    ''',
)
