from setuptools import setup, find_packages


requirements = [
    "sphinx",
    "requests",
    ]

classifiers = [
    "Development Status :: 3 - Alpha",
    "License :: OSI Approved :: BSD License",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.3",
    "Topic :: Software Development :: Documentation",
    "Topic :: Documentation"
    ]

setup(
    name='sphinxcontrib-menesbuilder',
    version="0.2",
    description='menesbuilder is a Sphinx extension for menes PDF generates web application',
    long_description=open("README.rst").read(),
    classifiers=classifiers,
    keywords=['sphinx', 'pdf'],
    author='WAKAYAMA shirou',
    author_email='shirou.faw at gmail.com',
    zip_safe=False,
    url='http://menes-pdf.info',
    download_url='http://pypi.python.org/pypi/sphinxcontrib-menesbuilder',
    license='BSD License',
    packages=find_packages(),
    install_requires=requirements,
    namespace_packages=['sphinxcontrib'],
    include_package_data=True
    )

