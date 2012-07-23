from traffic import TrafficLink, TrafficState
from cr_utils.Dumpable import Dumpable
from cr_network import Link
from demand import FlowNetwork

class FundamentalDiagram(Dumpable):
  """docstring for FundamentalDiagram"""

  def __init__(self, v, w, rho_max, q_max):
    super(FundamentalDiagram, self).__init__()
    self.v = float(v)
    self.w = float(w)
    self.rho_max = float(rho_max)
    self.q_max = float(q_max)

  @classmethod
  def triangular(cls, v, q_max, rho_max):
    rho_c = float(q_max) / v
    w = float(q_max) / (rho_max - rho_c)
    return cls(
      v,
      w,
      rho_max,
      q_max
    )

  def rho_crit(self):
    return self.q_max / self.v

  def jsonify(self):
    """docstring for jsonify"""
    return {
      'v': self.v,
      'w': self.w,
      'rho_max': self.rho_max,
      'q_max': self.q_max
    }

  def rho_cong(self, flow):
    return self.rho_max - float(flow)/self.w

  def flow_cong(self, rho):
    return self.w * (self.rho_max - rho)

  def rho_ff(self, flow):
    return float(flow) / self.v

  def flow_ff(self, rho):
    return self.v * rho

  def flow(self, rho):
    return min(self.q_max, self.flow_cong(rho), self.flow_ff(rho))

  @classmethod
  def load_with_json_data(cls, data):
    v=data['v']
    w=data['w']
    rho_max=data['rho_max']
    q_max=data.get('q_max', v*w*rho_max / (v + w))
    return cls(
      v=v,w=w,rho_max=rho_max,q_max=q_max
      )

class CTMState(TrafficState):

    def __init__(self, flow, density):
        super(CTMState, self).__init__()
        self.flow = flow
        self.density = density

    def __str__(self):
        return 'flow: {0}, dens: {1}'.format(self.flow, self.density)


class CTMLink(TrafficLink):
  """docstring for CTMLink"""

  def __init__(self, l, fd, flow=0.0, density=0.0, *args, **kwargs):
    """

    @param l: length of link
    @param fd: fundamental diagram
    @type fd: FundamentalDiagram
    @param flow: flow state on link
    """
    super(CTMLink, self).__init__(*args, **kwargs)
    self.l = l
    self.fd = fd
    self.state = CTMState(flow, density)

  def jsonify(self):
    json = super(CTMLink, self).jsonify()
    json.update({
      'l': self.l,
      'fd': self.fd.jsonify(),
      'flow': self.state.flow,
      'rho': self.state.density
    })
    return json


  def d3_value(self):
    return self.l
    
  def congestion_level(self):
    rho_l = self.state.flow / self.fd.v
    rho_h = self.fd.rho_max - self.state.flow / self.fd.w
    rho = self.state.density
    return (rho - rho_l) / (rho_h - rho_l)

  @classmethod
  def additional_kwargs(cls, data):
    return dict(
      l=data['l'],
      density=data.get('rho', 0.0),
      flow=data.get('flow',0.0),
      fd=FundamentalDiagram.load_with_json_data(data['fd'])
    )

  def travel_time(self, state=None):
    if state is None:
      state = self.get_state()
    if state.density <= 10e-8 or state.flow <= 10e-8:
      return self.l / self.fd.v
    return self.l * state.density / state.flow

  def total_travel_time(self, state=None):
    if state is None:
      state = self.get_state()
    return self.l * state.density

  def get_state(self):
    return self.state


class CTMNetwork(FlowNetwork):
  link_class = CTMLink
  
  def max_flow(self, route):
    return min(link.fd.q_max for link in route.links)
    
  def ff_travel_time(self, route):
    return sum(link.l/link.fd.v for link in route.links)
    
  def route_travel_time(self, route):
    return sum(link.travel_time() for link in route.links)
  