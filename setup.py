#/usr/lib/python3
import setuptools

long_dsc = ''
with open('README.md', 'r') as file_obj:
    long_dsc = file_obj.read()

setuptools.setup(
    name='python3-alpaka',
    version='0.1',
    author='Rocky Craig, Zach Volchak',
    author_email='zakhar.volchak@hpe.com',
    description='A Python3 netlink handler.',
    long_description=long_dsc,
    long_description_content_type='text/markdown',
    url='https://github.hpe.com/atsugami-kun/alpaka',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: POSIX :: Linux',
    ],
)