from cr_utils import Dumpable
from crnetwork import Link, CRNetwork, Junction
from pprint import pprint

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


class CTMLink(Link, Dumpable):
  """docstring for CTMLink"""

  def __init__(self, l, fd, *args, **kwargs):
    super(CTMLink, self).__init__(*args, **kwargs)
    self.l = l
    self.fd = fd

  def jsonify(self):
    json = super(CTMLink, self).jsonify()
    json.update({
      'l': self.l,
      'fd': self.fd.jsonify()
    })
    return json


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
  def load_with_json_data(cls, data, **kwargs):
    try:
      net = kwargs['net']
    except:
      raise Exception('need to pass in network')
    return cls(
      net=net,
      l=data['l'],
      rho=data['rho'],
      name=data['name'],
      fd=FundamentalDiagram.load_with_json_data(data['fd'])
    )


class CTMNetwork(CRNetwork):
  def __init__(self):
    super(CTMNetwork, self).__init__()

  @classmethod
  def load_with_json_data(cls, data):
    net = cls()
    links = dict(
      (link['name'],
       DensityCTMLink.load_with_json_data(link, net=net))
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


def main():
  net = CRNetwork()
  l = [DensityCTMLink(name=_, net=net, l=1, rho=1, fd=FundamentalDiagram(v=1., w=1., rho_max=10., q_max=10.)) for _ in
       range(3)]
  j = Junction([l[0]], [l[1], l[2]])
  net.add_junction(j)
  net.dump('simple.json')


def main2():
  net = CTMNetwork.load('networks/fpnet.json')
  net.cache_props()
  pprint(net.od_routes)

if __name__ == '__main__':
  main2()
  