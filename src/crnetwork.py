from networkx import DiGraph
from networkx.readwrite import d3_js
from bfs import bfs, all_paths
from collections import defaultdict
from cr_utils import Dumpable

class Link(object):
  """docstring for Link"""

  def __init__(self, net=None, name=None):
    super(Link, self).__init__()
    self.net = net
    self.name = str(name)
    try:
      props = net.node[self]
    except:
      net.add_node(self)
      props = net.node[self]
    props['name'] = self.name
    self.up_junc = None
    self.down_junc = None

  def neighbors(self):
    return self.net.neighbors(self)

  def set_up_junc(self, j):
    """docstring for set_up_junc"""
    if self.up_junc is not None:
      raise Exception("junction already set")
    self.up_junc = j

  def set_down_junc(self, j):
    """docstring for set_up_junc"""
    if self.down_junc is not None:
      raise Exception("junction already set")
    self.down_junc = j

  def jsonify(self):
    """docstring for jsonify"""
    return {
      'name': self.name
    }


  def upstream_links(self):
    return self.net.in_edges(self)

  def downstream_links(self):
    return self.net.out_edges(self)

  def is_sink(self):
    return len(self.downstream_links()) == 0

  def is_source(self):
    return len(self.upstream_links()) == 0

  def __repr__(self):
    if self.name is None:
      return super(Link, self).__repr__()
    return self.name

  def __str__(self):
    return self.__repr__()

  def routes(self):
    """docstring for routes"""
    return [route for routes in self.net.od_routes.itervalues() for route in routes if route.has_link(self)]


class Junction(object):
  """docstring for Junction"""

  def __init__(self, in_links, out_links):
    super(Junction, self).__init__()
    self.in_links = in_links
    self.out_links = out_links
    for il in in_links:
      il.set_down_junc(self)
    for ol in out_links:
      ol.set_up_junc(self)

  def edges(self):
    """docstring for edges"""
    return [(i, o) for i in self.in_links for o in self.out_links]

  def jsonify(self):
    """docstring for jsonify"""
    return ([link.name for link in self.in_links],
            [link.name for link in self.out_links])


class Route(object):
  """docstring for Route"""

  def __init__(self, net, *links):
    super(Route, self).__init__()
    self.net = net
    if len(links) is 1 and isinstance(links[0], list):
      self.links = links[0]
    else:
      self.links = links

  def matches(self, links):
    return self.links == links or [link.name for link in self.links] == links

  def has_link(self, link):
    return link in self.links

  def __repr__(self):
    return str(self.links)

  def __str__(self):
    return self.__repr__()

  def jsonify(self):
    return [link.name for link in self.links]


class CRNetwork(DiGraph, Dumpable):
  """docstring for CRNetwork"""

  def __init__(self):
    super(CRNetwork, self).__init__()
    self.junctions = set()

  def add_junction(self, junction):
    """docstring for add_junction"""
    self.junctions.add(junction)
    self.add_edges_from(junction.edges())

  def route_by_names(self, route):
    return [r for r in self.all_routes() if r.matches(route)][0]

  def link_by_name(self, name):
    return [l for l in self.links() if l.name == name][0]

  def all_routes(self):
    return [r for rs in self.od_routes.itervalues() for r in rs]

  def links(self):
    """docstring for links"""
    return self.nodes()

  def _sources(self):
    """docstring for _sources"""
    return set([link for link in self.links() if link.is_source()])

  def _sinks(self):
    """docstring for _sources"""
    return set([link for link in self.links() if link.is_sink()])

  def cache_props(self):
    """docstring for cache_props"""
    self.sources = self._sources()
    self.sinks = self._sinks()
    self.od_routes = self.calc_od_routes()

  def calc_od_routes(self):
    """docstring for calc_od_routes"""
    routes = defaultdict(list)
    for source in self.sources:
      dests = self.all_paths(source)
      for sink in self.sinks:
        routes[source, sink] = [Route(self, *(path + [sink])) for path in dests[sink]]
    return routes


  def bfs(self, source):
    """docstring for bfs"""
    return bfs(source)

  def all_paths(self, source):
    """docstring for bfs"""
    return all_paths(source)

  def jsonify(self):
    """docstring for jsonify"""
    return {
      'links': [link.jsonify() for link in self.links()],
      'junctions': [junction.jsonify() for junction in self.junctions]
    }

  def d3ize(self):
    d3_js.export_d3_js(self, group='name')

  def inverted_graph(self):
    new_net = CRNetwork()
    sources = [Junction([], [source]) for source in self.sources]
    sinks = [Junction([sink], []) for sink in self.sinks]
    l_sources = []
    for source in sources:
      link = Link(net=new_net,
                  name='in: [], out: {0}'.format(source.out_links))
      link.junction = source
      l_sources.append(link)

    l_sinks = []
    for sink in sinks:
      link = Link(net=new_net,
                  name='in: {0}, out: []'.format(sink.in_links))
      link.junction = sink
      l_sinks.append(link)
    source_edges = [(source, source.junction.out_links[0]) for source in l_sources]
    sink_edges = [(sink, sink.junction.in_links[0]) for sink in l_sinks]
    for junc in self.junctions:
      l_junc = Link(net=new_net,
                    name='in: {0}, out: {1}'.format(junc.in_links, junc.out_links))
      junc.l_junc = l_junc
    junc_edges = []
    for link in self.links():
      try:
        junc_edges.append((link.up_junc.l_junc, link.down_junc.l_junc))
      except:
        continue
    new_net.add_edges_from(junc_edges + source_edges + sink_edges)
    return new_net


def main():
  """docstring for main"""
  net = CRNetwork()
  links = [Link(net) for _ in range(3)]
  junction = Junction([links[0]], [links[1], links[2]])
  net.add_junction(junction)
  print [link.neighbors() for link in links]
  print [link.upstream_links() for link in links]
  print [link.downstream_links() for link in links]
  print [link.is_sink() for link in links]
  print [link.is_source() for link in links]


if __name__ == '__main__':
  main()