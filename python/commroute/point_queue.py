import cvxpy
from cvxpy.functions.quad_over_lin import quad_over_lin
import math
from cr_utils.Dumpable import Dumpable
from traffic import TrafficLink, TrafficState
from demand import FlowNetwork, RouteDemand
from cvxpy import square

__author__ = 'jdr'

from cr_network import Link, Junction

class FlowLatency(Dumpable):
  """docstring for Demand"""
  types = None

  def jsonify(self):
    return {
      'type': self.tag()
    }

  def travel_time(self, link, flow):
    # this should be a convex function to work within cvxpy !!!!
    raise NotImplementedError("abstract")

  @classmethod
  def tag(cls):
    return 'abstract'

  @classmethod
  def load_with_json_data(cls, data, **kwargs):
    return cls.types[data['type']].load_latency(data)

  @classmethod
  def load_latency(cls, data):
    raise NotImplementedError("abstract")

class AffineLatency(FlowLatency):

  def __init__(self, a, b):
    self.a = a
    self.b = b

  @classmethod
  def tag(cls):
    return 'affine'

  def travel_time(self, link, flow):
    return flow*self.a + self.b

  def flow_x_travel_time(self, link, flow):
    return square(flow)*self.a + self.b*flow

  @classmethod
  def load_latency(cls, data):
    return cls(
      a = data['a'],
      b = data['b']
    )

  def jsonify(self):
    json = super(AffineLatency, self).jsonify()
    json.update({
      'a': self.a,
      'b': self.b
    })
    return json

class MM1Latency(FlowLatency):

  def __init__(self, rho, mu):
    super(FlowLatency, self).__init__()
    self.rho = rho
    self.mu = mu

  @classmethod
  def tag(cls):
    return 'mm1'

  def travel_time(self, link, flow):
    return self.rho * quad_over_lin(1.0, self.mu - flow)

  def flow_x_travel_time(self, link, flow):
    return self.rho * (self.mu * quad_over_lin(1.0, self.mu - flow) - 1.0)

  @classmethod
  def load_latency(cls, data):
    return cls(
      rho = data['rho'],
      mu = data['mu']
    )

  def jsonify(self):
    json = super(MM1Latency, self).jsonify()
    json.update({
      'rho': self.rho,
      'mu': self.mu
    })
    return json

FlowLatency.types = dict(
  (cls.tag(), cls)
  for cls in (AffineLatency, FlowLatency)
)

class PQState(TrafficState):

  def __init__(self, flow):
    super(PQState, self).__init__()
    self.flow = flow

class FlowLink(TrafficLink):

  def __init__(self, latency, q_max, flow = 0.0, *args, **kwargs):
    super(FlowLink, self).__init__(*args, **kwargs)
    self.q_max = q_max
    self.latency = latency
    self.state = PQState(flow)

  def get_state(self):
    return self.state

  def flow_latency(self, flow):
    return self.latency.travel_time(self, flow)

  def flow_flow_latency(self, flow):
    return self.latency.flow_x_travel_time(self, flow)

  def travel_time(self, state=None):
    if state is None:
      state = self.get_state()
    return self.latency.travel_time(self, state.flow)

  def total_travel_time(self, state=None):
    if state is None:
      state = self.get_state()
    return state.flow * self.latency.travel_time(self, state.flow)

  def jsonify(self):
    json = super(FlowLink, self).jsonify()
    json['q_max'] = self.q_max
    json['latency'] = self.latency.jsonify()
    json['flow'] = self.state.flow
    return json

  @classmethod
  def additional_kwargs(cls, data):
    return {
      'q_max': data['q_max'],
      'latency': FlowLatency.load_with_json_data(data['latency']),
      'flow': data['flow']
    }

class FlowLinkNetwork(FlowNetwork):
  link_class = FlowLink


def main():
  net = FlowLinkNetwork()
  source = FlowLink(
    name='source',
    q_max=5.0,
    latency=AffineLatency(
      a=2.0,
      b=3.0
    )
  )
  sink = FlowLink(
    name='sink',
    q_max=4.0,
    latency=AffineLatency(
      a=4.0,
      b=5.0
    )
  )
  junction = Junction([source],[sink])
  net.add_junction(junction)
  net.demands.append(RouteDemand(flow=1.5, route=net.route_by_names(['source','sink'])))
  net.dump('../networks/flownet.json')

  del net
  net = FlowLinkNetwork.load('../networks/flownet.json')
  print net.demands
  print net.get_links()
  for link in net.get_links():
    print link.flow_latency(3.4)

if __name__ == '__main__':
  main()