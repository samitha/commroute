from static_op import LagrangianStaticProblem

__author__ = 'jdr'

class ComplacencyConstrained(LagrangianStaticProblem):

  # TODO: scale hack, fix this yo!
  scale = 1.1

  def variablize(self):
    super(ComplacencyConstrained, self).variablize()
    for route in self.all_routes():
      route.old_tt = self.route_travel_time(route)

  def route_tt_heuristic(self, route):
    raise NotImplementedError("abstract")

  def con_route_tt(self):
    return [
    self.cr_leq(self.route_tt_heuristic(route), route.old_tt*self.scale)
    for route in self.all_routes()
    ]

  def constraints(self):
    return super(ComplacencyConstrained, self).constraints() + self.con_route_tt()