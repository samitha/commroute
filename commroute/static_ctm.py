from cvxpy import  quad_over_lin, hstack
from cvxpy import max as cvx_max
from cvxpy_solver import SimpleOptimizeMixIn
from cr_utils import flatten
from ctm import DensityCTMNetwork
from static_op import LagrangianConstrained
from numpy import inf

__author__ = 'jdr'


class CTMStaticProblem(DensityCTMNetwork, LagrangianConstrained):
  def variablize(self):
    super(CTMStaticProblem, self).variablize()
    for link in self.get_links():
      link.v_dens = self.create_var('dens: {0}'.format(link.name), self.attr_realizer(link, 'rho'))


class CTMConstrained(CTMStaticProblem):
  def con_ctm(self):
    return list(flatten([self.cr_geq(link.v_flow, 0),
                         self.cr_leq(link.v_flow, link.fd.q_max),
                         self.cr_leq(link.v_flow, link.fd.v * link.v_dens),
                         self.cr_leq(link.v_flow, link.fd.w * (link.fd.rho_max - link.v_dens)),
                         self.cr_geq(link.v_dens, 0),
                         self.cr_leq(link.v_dens, link.fd.rho_max),
                         ] for link in self.get_links()))

  def constraints(self):
    return super(CTMConstrained, self).constraints() + self.con_ctm()

  def check_feasible(self):
    """
    checks the feasibility of the problem
    @rtype: bool
    """
    def check_feasible_constraints():
      return list(flatten(
        [self.cr_geq(link.v_flow, link.flow),
         self.cr_geq(link.v_dens, link.rho),
         self.cr_leq(link.v_flow, link.flow),
         self.cr_leq(link.v_dens, link.rho)]
          for link in self.get_links()
      ))

    class FeasibleProgram(SimpleOptimizeMixIn):
      outer = self
      def constraints(self):
        return self.outer.constraints() + check_feasible_constraints()

      def variablize(self):
        self.outer.variablize()

    op = FeasibleProgram()
    return op.is_feasible()


class ComplacencyConstrained(CTMConstrained):
  def route_tt_heuristic(self, route):
    def link_tt_heuristic(link):
      ff = link.l / link.fd.v
      q_max = (link.l / link.fd.q_max) * link.v_dens
      rho_hat = link.fd.rho_max - link.v_dens
      cong = link.l / link.fd.w * (quad_over_lin(link.fd.rho_max ** .5, rho_hat) - 1)
      return cvx_max(hstack([ff, q_max, cong]))

    return sum(map(link_tt_heuristic, route.links))

  def con_route_tt(self):
    return [
    self.cr_leq(self.route_tt_heuristic(route), 10000.0)
    for route in self.all_routes()
    ]

  def constraints(self):
    return super(ComplacencyConstrained, self).constraints() + self.con_route_tt()


class MinTTT(CTMStaticProblem):
  def objective(self):
    return sum(link.l * link.v_dens for link in self.get_links())


class MinTTTComplacencyProblem(MinTTT, ComplacencyConstrained):
  def __init__(self):
    super(MinTTTComplacencyProblem, self).__init__()

  def objective(self):
    return MinTTT.objective(self)

  def constraints(self):
    return ComplacencyConstrained.constraints(self)


class MinTTTLagrangianCTMProblem(MinTTT, CTMConstrained):
  def __init__(self):
    super(MinTTTLagrangianCTMProblem, self).__init__()

  def objective(self):
    return MinTTT.objective(self)

  def constraints(self):
    return CTMConstrained.constraints(self)


