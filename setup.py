from setuptools import setup

params = {}
params['scripts'] = ['bin/logwork']

setup(name='logwork',
      version='0.04',
      description='simple work logging with active window monitoring',
      url='',
      author='Diogo Silva',
      author_email='',
      license='',
      packages=['logwork'],
      zip_safe=False,
      **params)
