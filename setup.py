from setuptools import setup
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='seiran',
      version='1.3.3',
      description='Local bookmarks manager',
      long_description=long_description,
      long_description_content_type='text/markdown',
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Internet',
      ],
      keywords='bookmarks',
      url='http://github.com/gargargarrick/seiran',
      author='Garrick',
      author_email='earthisthering@posteo.de',
      license='GPLv3+',
      packages=['seiran'],
      install_requires=[
          'appdirs'
      ],
      entry_points={'console_scripts':['seiran=seiran.seiran:main']},
      include_package_data=True,
      zip_safe=False)
