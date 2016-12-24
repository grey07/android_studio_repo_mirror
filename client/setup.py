#!/usr/bin/env python

from distutils.core import setup

setup(name='Android Studio Repository Mirror',
      version='1.0',
      description='This is the offline componenet capable of mirroring android studio repos.',
      author='grey',
      url='https://github.com/grey07/android_studio_repo_mirror',
      packages=['cherrypy >= 8.1.3', 'pyopenssl'],
     )
