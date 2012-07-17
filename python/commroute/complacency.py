from cvxpy.functions.quad_over_lin import quad_over_lin
from cvxpy.utils import hstack
from point_queue import PQState
from static_ctm import MinTTTMixin
from static_pq import MinTTTFlowLinkProblem
from compliance import ComplianceMixin
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


class ComplacencyCompliance(ComplacencyConstrained, ComplianceMixin):

  def run(self):
    self.set_compliance(False)
    self.assign_demand_flows()
    print 'before', self.total_travel_time()
    self.set_compliance(True)
    self.get_program().cr_solve(quiet=True)
    self.realize()
    print 'after', self.total_travel_time()
    self.set_compliance(False)

  def assign_demand_flows(self):
    self.FAKE_OBJECTIVE = True
    self.get_program().cr_solve()
    self.realize()
    self.FAKE_OBJECTIVE = False

  def objective(self):
    try:
      if self.FAKE_OBJECTIVE:
        return 0.0
      else:
        return super(ComplacencyCompliance, self).objective()
    except:
      return super(ComplacencyCompliance, self).objective()



class MinTTTComplacencyProblem(ComplacencyConstrained, MinTTTMixin):
  def route_tt_heuristic(self, route):
    def link_tt_heuristic(link):
      ff = link.l / link.fd.v
      q_max = (link.l / link.fd.q_max) * link.v_dens
      rho_hat = link.fd.rho_max - link.v_dens
      cong = link.l / link.fd.w * (link.fd.rho_max * quad_over_lin(1.0 , rho_hat) - 1)
      return cvx_max(hstack([ff, q_max, cong]))

    return sum(map(link_tt_heuristic, route.links))

# class CTMCC(MinTTTComplacencyProblem, ComplacencyCompliance):
#   pass

class MinTTTFlowLinkComplacencyProblem(MinTTTFlowLinkProblem, ComplacencyConstrained):

  def route_tt_heuristic(self, route):
    return sum(
      link.travel_time(PQState(link.v_flow))
        for link in route.links
    )

class PQCC(ComplacencyCompliance, MinTTTFlowLinkComplacencyProblem):
  pass