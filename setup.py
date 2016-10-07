from setuptools import setup
import platform

dependencies = [
    'twisted>=16.4.1',
]

extras = {
        ":python_version<'3.4'": ["enum34"],
        ":sys_platform=='win32'": ['pypiwin32']
        }

version = '1.0.1'

setup(name='qtm',
      version=version,
      description='QTM Python SDK',
      url='https://github.com/qualisys/qualisys_python_sdk',
      download_url='https://github.com/qualisys/qualisys_python_sdk/tarball/{}'.format(version),
      author='Martin Gejke',
      author_email='support@qualisys.com',
      license='MIT',
      packages=['qtm'],
      install_requires=dependencies,
      extras_require=extras,
      classifiers=[
          'Operating System :: OS Independent',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Topic :: Scientific/Engineering',
          'Topic :: Utilities'
      ],
      zip_safe=True)
