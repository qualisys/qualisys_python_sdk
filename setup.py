from setuptools import setup

version = '2.0.0'

setup(
    name='qtm',
    version=version,
    description='QTM Python SDK',
    url='https://github.com/qualisys/qualisys_python_sdk',
    download_url='https://github.com/qualisys/qualisys_python_sdk/tarball/{}'.
    format(version),
    author='Martin Gejke',
    author_email='support@qualisys.com',
    license='MIT',
    packages=['qtm'],
    classifiers=[
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering', 'Topic :: Utilities'
    ],
    zip_safe=True)
