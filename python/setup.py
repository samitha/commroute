from distutils.core import setup

setup(
  name='commroute',
  version='0.1',
  packages=['commroute', 'commroute.cr_utils','commroute.d3_plot'],
  url='http://github.com/jackdreilly/commroute',
  license='BSD',
  author='jdr',
  author_email='jackdreilly@me.com',
  description='routing compliant users on network',
  requires=[
    'cvxopt(==1.1.5)',
    'cvxpy(==0.0.1)',
    'networkx'
  ]
)
