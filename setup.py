from setuptools import setup, find_packages
import os

version = '0.1-dev'

long_description = (
    open('README.md').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('docs/CONTRIBUTORS.txt').read()
    + '\n' +
    open('docs/CHANGES.txt').read()
    + '\n')

setup(name='collective.z3cform.referenceupload',
      version=version,
      description="Reference upload widget",
      long_description=long_description,
      classifiers=[
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Framework :: Plone :: 4.1",
          "Framework :: Plone :: 4.2",
          "Framework :: Plone :: 4.3",
          "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      author='Radoslaw Jankiewicz',
      author_email='radek@enfoldsystems.com',
      url='https://github.com/collective/collective.z3cform.referenceupload',
      license='GPLv2',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['collective', 'collective.z3cform'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'archetypes.referencebrowserwidget',
          'plone.app.relationfield',
          'plone.directives',
          'plone.formwidget.contenttree',
          'z3c.form',
          'z3c.formwidget.query',
          'z3c.relationfield',
      ],
      extras_require={
          'test': [
              'plone.app.testing',
          ],
      },
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
