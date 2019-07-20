from setuptools import setup

def readme():
    with open('README') as f:
        return f.read()

setup(name='seiran',
      version='1.3.0',
      description='Local bookmarks manager',
      long_description="Save bookmarks to a local SQLite database",
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
