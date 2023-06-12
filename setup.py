from setuptools import setup

version = "3.0.0"

setup(
    name="qtm-rt",
    version=version,
    description="QTM Python SDK",
    long_description="For older versions, see \"qtm\" package.",
    url="https://github.com/qualisys/qualisys_python_sdk",
    download_url="https://github.com/qualisys/qualisys_python_sdk/tarball/{}".format(
        version
    ),
    author="Martin Gejke",
    author_email="support@qualisys.com",
    license="MIT",
    packages=["qtm_rt"],
    package_data={"qtm_rt": ["data/demo.qtm"]},
    classifiers=[
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering",
        "Topic :: Utilities",
    ],
    python_requires=">=3.5.3",
    zip_safe=True,
)
