from cvxpy_solver import SimpleOptimizeMixIn
from ctm import *
from demand import ODDemand, RouteDemand

class LagrangianStaticProblem(FlowNetwork, SimpleOptimizeMixIn):
  """docstring for StaticProblem"""

  def variablize(self):
    """docstring for cvxify"""
    self.cache_props()
    super(LagrangianStaticProblem, self).variablize()
    for link in self.get_links():
      link.v_flow = self.create_var('flow: {0}'.format(link.name),self.attr_realizer(link.state,'flow'))
    for route in self.all_routes():
      route.v_flow = self.create_var('route: {0}'.format(route.links), self.attr_realizer(route,'flow'))

class LagrangianConstrained(LagrangianStaticProblem):

  def con_junc(self):
    return [self.cr_eq(sum(link.v_flow for link in junction.in_links),
               sum(link.v_flow for link in junction.out_links))
            for junction in self.junctions]

  def con_od_flows(self):
    od_demands = filter(lambda dem: isinstance(dem, ODDemand), self.get_demands())
    route_demands = filter(lambda dem: isinstance(dem, RouteDemand), self.get_demands())
    for route in self.all_routes():
      matches = [dem for dem in route_demands if dem.route is route]
      if len(matches) is 0:
        route_demands.append(RouteDemand(route=route, flow=0.0))
      elif len(matches) > 1:
        for dem in matches:
          route_demands.remove(dem)
        route_demands.append(RouteDemand(route=route, flow = sum(
          [dem.flow for dem in matches]
        )))
    for source in self.sources:
      for sink in self.sinks:
        matches = [
          dem for dem in od_demands
          if dem.source is source and dem.sink is sink
        ]
        if len(matches) is 0:
          od_demands.append(ODDemand(
            source=source,
            sink=sink,
            flow=0.0
          ))
        elif len(matches) > 1:
          for dem in matches:
            od_demands.remove(dem)
          od_demands.append(
            ODDemand(
              source=source,
              sink=sink,
              flow=sum(
                dem.flow for dem in matches
              )
            )
          )
    def route_flows(link):
      flow = 0.0
      link_routes = link.routes(self)
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
           self.cr_eq(route_flows(link), link.v_flow)
           for link in self.get_links()
           ] + [
    self.cr_eq(od_flows(dem.source, dem.sink), dem.flow)
    for dem in od_demands
    ] + [
      self.cr_geq(route.v_flow, 0.0) for route in self.all_routes()
    ]

  def constraints(self):
    return super(LagrangianConstrained, self).constraints() + self.con_od_flows()