from networkx import MultiDiGraph
from bfs import bfs, all_paths
from collections import defaultdict
from cr_utils import Dumpable, flatten
from d3.d3_mixin import *

class Link(Dumpable, D3Edge):
  """docstring for Link"""

  def __init__(self, net=None, name=None):
    super(Link, self).__init__()
    self.up_junc = None
    self.down_junc = None
    self.net = net
    self.name = str(name)
    try:
      props = net.node[self]
    except:
      net.add_node(self)
      props = net.node[self]
    props['name'] = self.name
    self.up_junc = Source(self)
    self.down_junc = Sink(self)

  def neighbors(self):
    return self.down_junc.link_neighbors()

  def set_up_junc(self, j):
    """docstring for set_up_junc"""
    if not self.is_source():
      raise Exception("junction already set")
    self.up_junc = j

  def set_down_junc(self, j):
    """docstring for set_up_junc"""
    if not self.is_sink():
      raise Exception("junction already set")
    self.down_junc = j

  def travel_time(self):
    raise NotImplementedError("implement dummy!")

  def jsonify(self):
    """docstring for jsonify"""
    return {
      'name': self.name
    }

  @classmethod
  def load_with_json_data(cls, data, **kwargs):
    new_kwargs = {'net': kwargs['net'], 'name': data['name']}
    new_kwargs.update(cls.additional_kwargs(data))
    return cls(**new_kwargs)

  @classmethod
  def additional_kwargs(cls, data):
    return {}

  def upstream_links(self):
    return self.net.in_edges(self.down_junc)

  def downstream_links(self):
    return self.net.out_edges(self.up_junc)

  def is_sink(self):
    return isinstance(self.down_junc, Sink) or self.down_junc is None

  def is_source(self):
    return isinstance(self.up_junc, Source) or self.up_junc is None

  def __repr__(self):
    if self.name is None:
      return super(Link, self).__repr__()
    return self.name

  def __str__(self):
    return self.__repr__()

  def routes(self):
    """docstring for routes"""
    return [route for routes in self.net.od_routes.itervalues() for route in routes if route.has_link(self)]

  def d3_attrs(self):
    return self.jsonify()

  def d3_source(self):
    return self.up_junc

  def d3_target(self):
    return self.down_junc

  def d3_value(self):
    return 1.0


class Junction(D3Node):
  """docstring for Junction"""

  def __init__(self, in_links, out_links):
    super(Junction, self).__init__()
    self.in_links = in_links
    self.out_links = out_links
    for il in in_links:
      il.set_down_junc(self)
    for ol in out_links:
      ol.set_up_junc(self)
    self.net = self.get_net()

  def d3_node_name(self):
    # verbose
    # return '{0}::{1}'.format(self.in_links,self.out_links)
    return ''

  def edges(self):
    """docstring for edges"""
    return [(i, o) for i in self.in_links for o in self.out_links]

  def jsonify(self):
    """docstring for jsonify"""
    return ([link.name for link in self.in_links],
            [link.name for link in self.out_links])

  def link_neighbors(self):
    return self.out_links

  def junction_neighbors(self):
    return self.net.neighbors(self)

  def neighbors(self):
    return self.junction_neighbors()

  def get_net(self):
    for link in self.links():
      return link.net

  def links(self):
    return set(self.in_links + self.out_links)

class Source(Junction):

  def __init__(self, link):
    super(Source, self).__init__([],[link])

class Sink(Junction):

  def __init__(self, link):
    super(Sink, self).__init__([link], [])


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

  def travel_time(self):
    return sum(link.travel_time() for link in self.links)


class CRNetwork(MultiDiGraph, Dumpable, D3Mixin):
  """docstring for CRNetwork"""

  link_class = Link

  def __init__(self):
    super(CRNetwork, self).__init__()
    self.links = set()
    self.CACHE = True

  def add_junction(self, junction):
    """docstring for add_junction"""
    self.links.update(junction.links())

  def route_by_names(self, route):
    all_routes = self.all_routes()
    matches = [r for r in all_routes if r.matches(route)]
    return matches[0]

  def link_by_name(self, name):
    return (l for l in self.get_links() if l.name == name).next()

  def all_routes(self):
    self.cache_props()
    return [r for rs in self.od_routes.itervalues() for r in rs]

  def get_links(self):
    """docstring for links"""
    return self.links

  def out_links(self, junction):
    return junction.out_links

  def _sources(self):
    """docstring for _sources"""
    return set([link for link in self.get_links() if link.is_source()])

  def _sinks(self):
    """docstring for _sources"""
    return set([link for link in self.get_links() if link.is_sink()])

  def edgify(self, link):
    self.add_edge(
      link.up_junc, link.down_junc,attr_dict={'link': link}
    )

  def cache_props(self):
    """docstring for cache_props"""
    if not self.CACHE:
      return
    self.clear()
    [self.edgify(link) for link in self.links]
    self.sources = self._sources()
    self.sinks = self._sinks()
    self.junctions = set(flatten([link.up_junc, link.down_junc] for link in self.get_links()))
    self.od_routes = self.calc_od_routes()
    self.CACHE = False

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
    self.cache_props()
    return {
      'links': [link.jsonify() for link in self.get_links()],
      'junctions': [junction.jsonify()
                    for junction in self.junctions
                    if not isinstance(junction, Source) and
                       not isinstance(junction, Sink)
      ]
    }


  @classmethod
  def load_with_json_data(cls, data):
    net = cls()
    links = dict(
      (link['name'],
       cls.link_class.load_with_json_data(link, net = net))
        for link in data['links']
    )
    junctions = [
    Junction([links[name] for name in junc[0]],
      [links[name] for name in junc[1]])
    for junc in data['junctions']
    ]
    for junction in junctions:
      net.add_junction(junction)
    return net

  def d3_edges(self):
    return self.get_links()