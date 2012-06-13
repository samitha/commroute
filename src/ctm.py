from cr_utils import Dumpable
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

  def jsonify(self):
    """docstring for jsonify"""
    return {
      'v': self.v,
      'w': self.w,
      'rho_max': self.rho_max,
      'q_max': self.q_max
    }

  @classmethod
  def load_with_json_data(cls, data):
    return cls(
      v=data['v'],
      w=data['w'],
      q_max=data['q_max'],
      rho_max=data['rho_max']
    )


class CTMLink(Link):
  """docstring for CTMLink"""

  def __init__(self, l, fd, flow=0.0, *args, **kwargs):
    super(CTMLink, self).__init__(*args, **kwargs)
    self.l = l
    self.fd = fd
    self.flow = flow

  def jsonify(self):
    json = super(CTMLink, self).jsonify()
    json.update({
      'l': self.l,
      'fd': self.fd.jsonify(),
      'flow': self.flow
    })
    return json


  def d3_value(self):
    return self.l


class DensityCTMLink(CTMLink):
  """docstring for DensityCTMLink"""

  def __init__(self, rho=0.0, *args, **kwargs):
    super(DensityCTMLink, self).__init__(*args, **kwargs)
    self.rho = rho

  def jsonify(self):
    """docstring for jsonify"""
    json = super(DensityCTMLink, self).jsonify()
    json.update({
      'rho': self.rho
    })
    return json

  @classmethod
  def additional_kwargs(cls, data):
    return dict(
      l=data['l'],
      rho=data['rho'],
      flow=data['flow'],
      fd=FundamentalDiagram.load_with_json_data(data['fd'])
    )


class DensityCTMNetwork(FlowNetwork):
  link_class = DensityCTMLink

  def __init__(self):
    super(DensityCTMNetwork, self).__init__()


  def tt_free_flow(self, route):
    return sum(link.l / link.fd.v for link in route.get_links)

if __name__ == '__main__':
  print 'hei'
  