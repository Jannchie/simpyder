
from setuptools import setup, find_packages

setup(
    name='spipy',
    version='0.0.1',
    description=(
        '分布式多线程通用爬虫'
    ),
    long_description=open('README.md').read(),
    author='Jannchie',
    author_email='jannchie@gmail.com',
    maintainer='Jannchie',
    maintainer_email='jannchie@gmail.com',
    license='MIT License',
    packages=find_packages(),
    platforms=["all"],
    url='https://github.com/Jannchie/spipy',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries'
    ],
)
