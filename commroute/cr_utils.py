__author__ = 'jdr'
from simplejson import dump, load
from itertools import chain

class Dumpable(object):
  def dump(self, fn):
    """docstring for dump"""
    with open(fn, 'w') as fn:
      dump(self.jsonify(), fn, indent=2)

  def jsonify(self):
    raise NotImplementedError('need to jsonify!')

  @classmethod
  def load(cls, fn, **kwargs):
    """
    load the object you want
    @param cls:
    @type cls: cls
    @param fn:
    @param kwargs:
    @return:
    """
    with open(fn, 'r') as fn:
      data = load(fn)
    return cls.load_with_json_data(data, **kwargs)

  @classmethod
  def load_with_json_data(cls, data, **kwargs):
    """

    @param cls:
    @type cls: cls
    @param data:
    @param kwargs:
    @return:
    """
    raise NotImplementedError('need to load object!')


def flatten(listOfLists):
  """Flatten one level of nesting"""
  return chain.from_iterable(listOfLists)
