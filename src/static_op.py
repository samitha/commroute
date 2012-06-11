from cr_optimize import SimpleOptimizeMixIn
from ctm import *
from cvxpy import variable, eq, geq
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
    ] + [
      geq(route.v_flow, 0.0) for route in self.all_routes()
    ]

  def constraints(self):
    return super(LagrangianConstrained, self).constraints() + self.con_od_flows()