from traffic import TrafficNetwork
from cr_utils.Dumpable import Dumpable

__author__ = 'jdr'


class Demand(Dumpable):
  """Base class for defining demands, which are really just flows"""
  types = dict()

  def __init__(self, flow):
    super(Demand, self).__init__()
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
      flow=data['flow']
    )

  @classmethod
  def add_type(cls, new_cls):
    cls.types[new_cls.tag()] = new_cls


class RouteDemand(Demand):
  """A Demand specified over a route"""

  @classmethod
  def tag(cls):
    return 'route'

  def __init__(self, route, *args, **kwargs):
    super(RouteDemand, self).__init__(*args, **kwargs)
    self.route = route

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
  """
  A demand specified over a source and sink pair,
  which gives optimization more freedom that route-based demands
  """

  def __init__(self, source, sink, *args, **kwargs):
    super(ODDemand, self).__init__(*args, **kwargs)
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
  """Demand specified over link, like a static sensor"""

  def __init__(self, link, *args, **kwargs):
    super(LinkDemand, self).__init__(*args, **kwargs)
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

class DynamicDemand(Demand):

    def __init__(self, t, *args, **kwargs):
        super(DynamicDemand, self).__init__(*args, **kwargs)
        self.t = t

    def jsonify(self):
        json = super(DynamicDemand, self).jsonify()
        json['t'] = self.t
        return json

class SourceDemand(DynamicDemand):

    def __init__(self, source, *args, **kwargs):
        super(SourceDemand, self).__init__(*args, **kwargs)
        self.source = source

    @classmethod
    def tag(cls):
        return 'dynamic source'

    @classmethod
    def load_demand(cls, data, net):
        return cls(
            flow=data['flow'],
            t = data['t'],
            source = net.link_by_name(data['source'])
        )

    def jsonify(self):
        json = super(DynamicDemand, self).jsonify()
        json['source'] = self.source.name
        return json

class DRouteDemand(DynamicDemand):

    def __init__(self, route, *args, **kwargs):
        super(DRouteDemand, self).__init__(*args, **kwargs)
        self.route = route

    @classmethod
    def tag(cls):
        return 'dynamic route'

    @classmethod
    def load_demand(cls, data, net):
        return cls(
            flow=data['flow'],
            t = data['t'],
            route = net.route_by_names(data['route'])
        )

    def jsonify(self):
        json = super(DynamicDemand, self).jsonify()
        json['route'] = self.route.name()
        return json


for new_cls in (Demand, ODDemand, LinkDemand, RouteDemand, SourceDemand, DRouteDemand):
  Demand.add_type(new_cls)

class DemandMixin(object):
  """
  Convenience mixin to provide "load demands" and "dump demands" methods,
  and also creates `self.demands` attribute
  """

  def __init__(self):
    super(DemandMixin, self).__init__()
    self.demands = []

  def load_demands(self, data):
    demands = data.get('demands', [])
    self.demands.extend([Demand.load_with_json_data(demand, net = self) for demand in demands])

  def dump_demands(self, json):
    json['demands'] = [demand.jsonify() for demand in self.demands]
    return json

  def get_demands(self):
    return self.demands


class FlowNetwork(DemandMixin, TrafficNetwork):
  """
  Better base class for creating networks, since demand is usually necessary
  """

  @classmethod
  def load_with_json_data(cls, data, **kwargs):
    net = super(FlowNetwork,cls).load_with_json_data(data, **kwargs)
    net.load_demands(data)
    return net

  def jsonify(self):
    json = super(FlowNetwork, self).jsonify()
    self.dump_demands(json)
    return json