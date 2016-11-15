from setuptools import setup

__name__ = 'illuminate'
__version__ = '0.3.0'

setup(
    name=__name__,
    version=__version__,
    url='https://github.com/donowsolutions/%s' % __name__,
    author='Jonathan Elliott Blum',
    author_email='jon@donowsolutions.com',
    description='Illuminate Education API wrapper',
    license='MIT',
    packages=['illuminate'],
    install_requires=[
        'requests-futures >=0.9.7',
        'requests-oauthlib >= 0.7.0'
    ],
    keywords=['illuminate', 'api', 'wrapper'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Education'
    ],
)
