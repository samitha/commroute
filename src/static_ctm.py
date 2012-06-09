from ctm import *
from cvxpy import variable, eq, leq, geq, minimize, program, quad_over_lin, hstack
from cvxpy import max as cvx_max
from cr_utils import Dumpable, flatten

class StaticCvxNetwork(CTMNetwork):
  """docstring for StaticCvxNetwork"""

  def __init__(self, *args, **kwargs):
    super(StaticCvxNetwork, self).__init__()
    self.cvxify()

  def cvxify(self):
    """docstring for cvxify"""
    self.cache_props()
    for link in self.links():
      link.v_flow = variable(name='flow: {0}'.format(link.name))
      link.v_dens = variable(name='dens: {0}'.format(link.name))
    for (source, sink), routes in self.od_routes.iteritems():
      for route in routes:
        route.v_flow = variable(name='rf: o: {0}, d: {1}'.format(source.name, sink.name))

  def tt_free_flow(self, route):
    return sum(link.l / link.fd.v for link in route.links)


class Demand(Dumpable):
  """docstring for Demand"""
  types = None

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

Demand.types = dict(
  (cls.tag(), cls)
    for cls in (Demand, ODDemand, LinkDemand, RouteDemand)
)

class StaticProblem(Dumpable):
  """docstring for StaticProblem"""

  def __init__(self, net, demands):
    super(StaticProblem, self).__init__()
    self.net = net
    self.demands = demands

  def jsonify(self):
    return {
      'net': self.net.jsonify(),
      'demands': [demand.jsonify() for demand in self.demands]
    }

  @classmethod
  def load_with_json_data(cls, data, **kwargs):
    net = StaticCvxNetwork.load_with_json_data(data['net'])
    net.cache_props()
    demands = [Demand.load_with_json_data(demand, net=net) for demand in data['demands']]
    return cls(
      net=net,
      demands=demands
    )

  def con_junc(self):
    return [eq(sum(link.v_flow for link in junction.in_links),
               sum(link.v_flow for link in junction.out_links))
            for junction in self.net.junctions]

  def con_od_flows(self):
    od_demands = filter(lambda dem: isinstance(dem, ODDemand), self.demands)
    route_demands = filter(lambda dem: isinstance(dem, RouteDemand), self.demands)

    def route_flows(link):
      flow = 0.0
      link_routes = link.routes()
      for route in link_routes:
        flow += route.v_flow
      for dem in route_demands:
        if dem.route in link_routes:
          flow += dem.flow
      return flow

    def od_flows(source, sink):
      flow = 0
      for route in self.net.od_routes[source, sink]:
        flow += route.v_flow
      return flow

    return [
           eq(route_flows(link), link.v_flow)
           for link in self.net.links()
           ] + [
    eq(od_flows(dem.source, dem.sink), dem.flow)
    for dem in od_demands
    ]

  def con_ctm(self):
    return list(flatten([geq(link.v_flow, 0),
                         leq(link.v_flow, link.fd.q_max),
                         leq(link.v_flow, link.fd.v * link.v_dens),
                         leq(link.v_flow, link.fd.w * (link.fd.rho_max - link.v_dens)),
                         geq(link.v_dens, 0),
                         leq(link.v_dens, link.fd.rho_max),
                         ] for link in self.net.links()))

  def route_tt_heuristic(self, route):
    def link_tt_heuristic(link):
      ff = link.l / link.fd.v
      q_max = (link.l / link.fd.q_max) * link.v_dens
      rho_hat = link.fd.rho_max - link.v_dens
      cong = link.l / link.fd.w * (quad_over_lin(link.fd.rho_max ** .5, rho_hat) - 1)
      return cvx_max(hstack([ff, q_max, cong]))

    return sum(map(link_tt_heuristic, route.links))

  def route_tt_real(self, route):
    def link_tt(link):
      if link.v_dens.value < link.fd.rho_max * 10e-8:
        return link.l / link.fd.v
      return link.l * link.v_dens.value / link.v_flow.value

    return sum([
    link_tt(link)
    for link in route.links
    ])

  def con_route_tt(self):
    return [
    leq(self.route_tt_heuristic(route), 10000.0)
    for routes in self.net.od_routes.itervalues()
    for route in routes
    ]

  def obj_min_ttt(self):
    return minimize(sum(link.l * link.v_dens for link in self.net.links()))

  def obj_feas(self):
    return minimize(0)

  def con_feas(self):
    """docstring for con_feas"""
    return self.con_ctm() + self.con_od_flows() + self.con_route_tt() #+ self.con_junc()

  def solve_feasible(self):
    self.net.cvxify()
    p = program(self.obj_feas(), self.con_feas())
    p.solve()
    return p

  def solve_ttt(self):
    self.net.cvxify()
    p = program(self.obj_min_ttt(), self.con_feas())
    p.solve()
    return p


def main5():
  prob = StaticProblem.load('networks/md_prob_plus.json')
  prog = prob.solve_ttt()
  prog.show()
  print prob.demands[0].flow
  for route in prob.net.all_routes():
    print route
    print route.v_flow.value

if __name__ == '__main__':
  main5()
