from setuptools import setup, find_packages


setup(
    name='pytest-redmine',
    version='1.0',
    description='A Redmine plugin for pytest',
    author='Simon Gomizelj',
    author_email='sgomizelj@sangoma.com',
    maintainer='Simon Gomizelj',
    maintainer_email="sgomizelj@sangoma.com",
    url='https://github.com/sangoma/pytest-redmine',
    packages=find_packages(),
    classifiers=['Development Status :: 3 - Alpha',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: MIT License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: Implementation :: CPython',
                 'Programming Language :: Python :: Implementation :: PyPy',
                 'Topic :: Software Development :: Testing',
                 'Topic :: Utilities'],
    install_requires=[
        'pytest>=2.6.0',
        'python-redmine>=2.0'
    ],
    entry_points={
        'pytest11': ['pytest_redmine = pytest_redmine.plugin']
    }
)
