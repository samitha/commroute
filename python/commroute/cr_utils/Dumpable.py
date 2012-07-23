from exceptions import NotImplementedError
from json import dump, load

__author__ = 'jdr'

class Dumpable(object):
  def dump(self, fn):
    """
    Serialize your data from `self.jsonify()` and store in the file `fn`
    @param fn: file name to be dumped to
    @type fn: str
    """
    with open(fn, 'w') as fn:
      dump(self.jsonify(), fn, indent=2)

  def jsonify(self):
    """
    the method that turns the object into an object that can be serialized via `simplejson.dump` method
    @return: object that can be serialized
    """
    raise NotImplementedError('need to jsonify!')

  @classmethod
  def load(cls, fn, **kwargs):
    """
    Load an object deserialized in the file `fn` of the same type as `cls`
    @param cls: the class that will be created
    @param fn: file name to load from
    @type fn: str
    @param kwargs: extra arguments to help with loading (to handle unforeseen deserialization needs)
    @return: the new object
    """
    do_cloud = kwargs.pop('cloud', False)
    if do_cloud:
      import cloud
      data = load(cloud.files.getf(fn))
    else:
      with open(fn, 'r') as fn:
        data = load(fn)
    return cls.load_with_json_data(data, **kwargs)

  @classmethod
  def load_with_json_data(cls, data, **kwargs):
    """
    The method that should be overridden for deserialization, needs to be overridden
    @param cls: the class that will be created
    @param data: deserialized json type (map, list, string...)
    @param kwargs: extra arguments to help with loading (to handle unforeseen deserialization needs)
    @return: the new object
    @rtype: `cls`
    """
    raise NotImplementedError('need to load object!')