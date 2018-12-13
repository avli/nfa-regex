from setuptools import setup, find_packages

with open('requirements.txt') as f:
    install_requires = f.read().split('\n')

setup(
    name="regex",
    version="0.1",
    packages=find_packages(where='src'),
    package_dir={"": "src"},
    entry_points={
        'console_scripts': [
            'regex = regex.cli:main',
        ]
    },
    install_requires=install_requires
)
