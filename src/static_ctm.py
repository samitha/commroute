from cr_optimize import SimpleOptimizeMixIn
from ctm import *
from cvxpy import variable, eq, leq, geq, minimize, program, quad_over_lin, hstack
from cvxpy import max as cvx_max
from cr_utils import flatten
from demand import ODDemand, RouteDemand

class LagrangianStaticProblem(FlowNetwork, SimpleOptimizeMixIn):
  """docstring for StaticProblem"""

  def cvxify(self):
    """docstring for cvxify"""
    self.cache_props()
    for link in self.links():
      link.v_flow = variable(name='flow: {0}'.format(link.name))
    for (source, sink), routes in self.od_routes.iteritems():
      for i, route in enumerate(routes):
        route.v_flow = variable(name='rf: o: {0}, d: {1} [{2}]'.format(source.name, sink.name, i))

class CTMStaticProblem(DensityCTMNetwork, LagrangianStaticProblem):

  def cvxify(self):
    super(CTMStaticProblem,self).cvxify()
    for link in self.links():
      link.v_dens = variable(name='dens: {0}'.format(link.name))

class LagrangianConstrained(LagrangianStaticProblem):

  def con_junc(self):
    return [eq(sum(link.v_flow for link in junction.in_links),
               sum(link.v_flow for link in junction.out_links))
            for junction in self.junctions]

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
      for route in self.od_routes[source, sink]:
        flow += route.v_flow
      return flow

    return [
           eq(route_flows(link), link.v_flow)
           for link in self.links()
           ] + [
    eq(od_flows(dem.source, dem.sink), dem.flow)
    for dem in od_demands
    ]

  def constraints(self):
    return super(LagrangianConstrained, self).constraints() + self.con_od_flows()

class CTMConstrained(CTMStaticProblem):

  def con_ctm(self):
    return list(flatten([geq(link.v_flow, 0),
                         leq(link.v_flow, link.fd.q_max),
                         leq(link.v_flow, link.fd.v * link.v_dens),
                         leq(link.v_flow, link.fd.w * (link.fd.rho_max - link.v_dens)),
                         geq(link.v_dens, 0),
                         leq(link.v_dens, link.fd.rho_max),
                         ] for link in self.links()))

  def constraints(self):
    return super(CTMConstrained, self).constraints() + self.con_ctm()

class LagrangianCTMConstrained(CTMConstrained,LagrangianConstrained):
  pass

class ComplianceConstrained(LagrangianCTMConstrained):

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
    for route in self.all_routes()
    ]

  def constraints(self):
    return super(ComplianceConstrained, self).constraints() + self.con_route_tt()

class MinTTT(CTMStaticProblem):

  def objective(self):
    return minimize(sum(link.l * link.v_dens for link in self.links()))

class MinTTTComplianceProblem(MinTTT, ComplianceConstrained, CTMStaticProblem):

  def __init__(self):
    super(MinTTTComplianceProblem, self).__init__()

  def objective(self):
    return MinTTT.objective(self)

  def constraints(self):
    return ComplianceConstrained.constraints(self)

class MinTTTLagrangianCTMProblem(MinTTT, LagrangianCTMConstrained, CTMStaticProblem):

  def __init__(self):
    super(MinTTTLagrangianCTMProblem, self).__init__()

  def objective(self):
    return MinTTT.objective(self)

  def constraints(self):
    return LagrangianCTMConstrained.constraints(self)



def main5():
  net = MinTTTComplianceProblem.load('networks/md_prob_plus.json')
  prog = net.get_program()
  prog.solve()
  prog.show()
  print net.demands[0].flow
  for route in net.all_routes():
    print route
    print route.v_flow.value

def main6():
  net = MinTTTComplianceProblem.load('networks/fpnet_with_demands.json')
  prog = net.get_program()
  prog.solve(quiet = True)
  print prog.objective.value
  net = MinTTTLagrangianCTMProblem.load('networks/fpnet_with_demands.json')
  prog = net.get_program()
  prog.solve(quiet = True)
  print prog.objective.value


if __name__ == '__main__':
  main6()
