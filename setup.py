from setuptools import setup
import sys
import platform

version='1.1'

requires = ['mlx9064x-driver>=1.1.3',
            ]


if platform.machine().startswith('armv'):
    requires += [
      'opencv-contrib-python>=3',
    ]
else:
    requires += [
      'opencv-contrib-python>=4',
    ]


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='mlx9064x-blob-detection',
    version=version,
    description='Blob detection for MLX90640-41',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='Apache License, Version 2.0',
    entry_points = {'console_scripts': ['mlx9064x-blob-detection = examples.mlx90640_opencv_blob_detection:main']},
    install_requires=requires,
    url = 'https://github.com/melexis-fir/mlx9064x-blob-detection-py',   # Provide either the link to your github or to your website
    download_url = 'https://github.com/melexis-fir/mlx9064x-blob-detection-py/archive/V'+version+'.tar.gz',
    packages=['examples'],
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: Microsoft :: Windows',
	'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Utilities',
    ],
)
