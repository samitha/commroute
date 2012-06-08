from crnetwork import Link, CRNetwork, Junction
from random import random
from pprint import pprint

class FundamentalDiagram(object):
  """docstring for FundamentalDiagram"""
  def __init__(self, v, w, rho_max, q_max):
    super(FundamentalDiagram, self).__init__()
    self.v = v
    self.w = w
    self.rho_max = rho_max
    self.q_max = q_max
    
  def jsonify(self):
    """docstring for jsonify"""
    return {
      'v': self.v,
      'w': self.w,
      'rho_max': self.rho_max,
      'q_max': self.q_max
    }

class CTMLink(Link):
  """docstring for CTMLink"""
  def __init__(self, l, fd, *args, **kwargs):
    super(CTMLink, self).__init__(*args, **kwargs)
    self.l = l
    self.fd = fd
    
  def jsonify(self):
    json = super(CTMLink,self).jsonify()
    json.update({
    'l': self.l,
    'fd': self.fd.jsonify()
    })
    return json
    
class DensityCTMLink(CTMLink):
  """docstring for DensityCTMLink"""
  def __init__(self, rho = 0.0, *args, **kwargs):
    super(DensityCTMLink, self).__init__(*args,**kwargs)
    self.rho = rho
    
  def jsonify(self):
    """docstring for jsonify"""
    json = super(DensityCTMLink,self).jsonify()
    json.update({
      'rho': self.rho
    })
    return json
    
def load_ctm(fn, net_class = CRNetwork):
  from simplejson import load
  net = net_class()
  with open(fn,'r') as fn:
    data = load(fn)
  links = dict((link['name'],
    DensityCTMLink(net = net, 
         name = link['name'], 
         l = link['l'], 
         rho = link['rho'], 
         fd = FundamentalDiagram(v = link['fd']['v'],
                                 w = link['fd']['w'],
                                 rho_max = link['fd']['rho_max'],
                                 q_max = link['fd']['q_max'])))
      for link in data['links'])
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
  l = [DensityCTMLink(name=_,net=net,l = 1, rho = 1, fd = FundamentalDiagram(v = 1., w=1., rho_max = 10., q_max = 10.)) for _ in range(3)]
  j = Junction([l[0]],[l[1],l[2]])
  net.add_junction(j)
  net.dump('simple.json')
  
def main2():
  net = load_ctm('fpnet.json')
  net.cache_props()
  pprint(net.od_routes)
  
if __name__ == '__main__':
  main()
  