from commroute.cr_utils.Dumpable import Dumpable
from cr_network import CRNetwork

__author__ = 'jdr'


class Demand(Dumpable):
  """docstring for Demand"""
  types = dict()

  def __init__(self, net, flow):
    super(Demand, self).__init__()
    self.net = net
    self.flow = flow

  def jsonify(self):
    return {
      'flow': self.flow,
      'type': self.tag()
    }

  @classmethod
  def tag(cls):
    return 'basic'

  @classmethod
  def load_with_json_data(cls, data, **kwargs):
    return cls.types[data['type']].load_demand(data, kwargs['net'])

  @classmethod
  def load_demand(cls, data, net):
    return cls(
      net=net,
      flow=data['flow']
    )

  @classmethod
  def add_type(cls, new_cls):
    cls.types[new_cls.tag()] = new_cls


class RouteDemand(Demand):
  """docstring for RouteDemand"""

  @classmethod
  def tag(cls):
    return 'route'

  def __init__(self, route, flow):
    self.route = route
    super(RouteDemand, self).__init__(route.net, flow)

  def jsonify(self):
    json = super(RouteDemand, self).jsonify()
    json.update({
      'route': self.route.jsonify(),
      })
    return json

  @classmethod
  def load_demand(cls, data, net):
    return cls(
      flow=data['flow'],
      route=net.route_by_names(data['route'])
    )


class ODDemand(Demand):
  """docstring for RouteDemand"""

  def __init__(self, source, sink, flow):
    super(ODDemand, self).__init__(source.net, flow)
    self.source = source
    self.sink = sink

  def jsonify(self):
    json = super(ODDemand, self).jsonify()
    json.update({
      'sink': self.sink.name,
      'source': self.source.name,
      })
    return json

  @classmethod
  def tag(cls):
    return 'od'

  @classmethod
  def load_demand(cls, data, net):
    return cls(
      flow=data['flow'],
      source=net.link_by_name(data['source']),
      sink=net.link_by_name(data['sink'])
    )


class LinkDemand(Demand):
  """docstring for LinkDemand"""

  def __init__(self, link, flow):
    super(LinkDemand, self).__init__(link.net, flow)
    self.link = link

  def jsonify(self):
    json = super(LinkDemand, self).jsonify()
    json.update({
      'link': self.link.name,
      })
    return json

  @classmethod
  def tag(cls):
    return 'link'

  @classmethod
  def load_demand(cls, data, net):
    return cls(
      flow=data['flow'],
      link=net.link_by_name(data['link'])
    )

for new_cls in (Demand, ODDemand, LinkDemand, RouteDemand):
  Demand.add_type(new_cls)

class DemandMixin(object):

  def __init__(self):
    self.demands = []

  def load_demands(self, data):
    demands = data.get('demands', [])
    self.demands.extend([Demand.load_with_json_data(demand, net = self) for demand in demands])

  def dump_demands(self, json):
    json['demands'] = [demand.jsonify() for demand in self.demands]
    return json


class FlowNetwork(CRNetwork, DemandMixin):

  def __init__(self):
    super(FlowNetwork, self).__init__()
    DemandMixin.__init__(self)

  @classmethod
  def load_with_json_data(cls, data, **kwargs):
    net = super(FlowNetwork,cls).load_with_json_data(data, **kwargs)
    net.load_demands(data)
    return net

  def jsonify(self):
    json = super(FlowNetwork, self).jsonify()
    self.dump_demands(json)
    return json

