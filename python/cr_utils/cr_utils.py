__author__ = 'jdr'
from itertools import chain


def flatten(listOfLists):
  """Flatten one level of nesting"""
  return chain.from_iterable(listOfLists)
