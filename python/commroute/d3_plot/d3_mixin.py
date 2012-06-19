from cr_utils.cr_utils import flatten

__author__ = 'jdr'

root_dir = 'd3'

class D3Mixin:

  def d3ize(self):
    from simplejson import dump

    edges = self.d3_edges()
    lkup = list(set(flatten([edge.d3_source(), edge.d3_target()] for edge in edges)))
    nodes = [
      {
        'name': node.d3_node_name()
      }
      for node in lkup
    ]
    edges = [
      {
      'source': lkup.index(edge.d3_source()),
      'target': lkup.index(edge.d3_target()),
      'attrs': edge.d3_attrs(),
      'value': edge.d3_value()
      }
    for edge in edges
    ]
    data = {
      'nodes': nodes,
      'links': edges
    }
    with open('{0}/html/graph.json'.format(root_dir),'w') as fn:
      dump(data, fn, indent=2)

  def d3_edges(self):
    raise NotImplementedError('abstract')


class D3Edge(object):

  def d3_source(self):
    raise NotImplementedError('abstract')

  def d3_target(self):
    raise NotImplementedError('abstract')

  def d3_attrs(self):
    raise NotImplementedError('abstract')

  def d3_value(self):
    raise NotImplementedError('abstract')

class D3Node(object):

  def d3_node_name(self):
    return 'hi'