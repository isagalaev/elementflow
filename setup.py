from setuptools import setup, find_packages

setup(
    name = 'elementflow',
    version = '0.5',
    author = 'Ivan Sagalaev',
    author_email = 'maniac@softwaremaniacs.org',
    url = 'https://github.com/isagalaev/elementflow',
    license = 'BSD',
    description = 'Python library for generating XML as a stream without building a tree in memory.',
    long_description = open('README.md').read(),

    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    install_requires = ['six'],
    py_modules = ['elementflow'],
)
