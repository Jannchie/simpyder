# coding=utf-8
from setuptools import setup, find_packages
from os.path import dirname, join
from simpyder.__version__ import __VERSION__
print(find_packages())
with open('./README.md', 'r', encoding="utf-8") as fh:
    long_description = fh.read()
setup(
    name='simpyder',
    version=__VERSION__,
    description=(
        'Distributed multithreading universal crawler'
    ),
    include_package_data=True,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Jannchie',
    author_email='jannchie@gmail.com',
    maintainer='Jannchie',
    maintainer_email='jannchie@gmail.com',
    license='MIT License',
    packages=find_packages(exclude=('demo', 'demo.*')),
    platforms=["all"],
    url='https://github.com/Jannchie/simpyder',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.4',
    install_requires=[
        'requests==2.22.0',
        'lxml==4.3.4',
    ]
)
