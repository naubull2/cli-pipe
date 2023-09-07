from setuptools import setup

setup(
    name='cli-pipe',
    version='1.0.0',
    py_modules=['main'],
    install_requires=[
        'addict>=2.4.0',
        'click>=8.1.7',
        'pathos>=0.3.1',
        'tqdm>=4.65.0'
    ],
    entry_points={
        'console_scripts': [
            'cmd = my_package.main:cli',
        ],
    },
)
