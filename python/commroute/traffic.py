from commroute.cr_network import CRNetwork

__author__ = 'jdr'
from cr_network import Link

class TrafficState(object):
  """base state"""
  pass


class TrafficLink(Link):

  def get_state(self):
    raise NotImplementedError("abstract")

  def travel_time(self, state=None):
    raise NotImplementedError("abstract")

  def total_travel_time(self, state=None):
    raise NotImplementedError("abstract")


class TrafficNetwork(CRNetwork):

  link_class = TrafficLink

  def total_travel_time(self):
    return sum(
      link.total_travel_time()
      for link in self.get_links()
    )

  def route_travel_time(self, route):
    return sum(
      link.travel_time()
      for link in route.links
    )
