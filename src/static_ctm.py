from cvxpy import geq, leq, quad_over_lin, variable, hstack, minimize, eq
from cvxpy import max as cvx_max
from cr_optimize import SimpleOptimizeMixIn
from cr_utils import flatten
from ctm import DensityCTMNetwork
from static_op import LagrangianConstrained
from numpy import inf

__author__ = 'jdr'


class CTMStaticProblem(DensityCTMNetwork, LagrangianConstrained):
  def cvxify(self):
    super(CTMStaticProblem, self).cvxify()
    self.cache_props()
    for link in self.get_links():
      link.v_dens = variable(name='dens: {0}'.format(link.name))
      # this next line isn't useful right now
      # link.d3_value = lambda: link.v_dens.value

  def cvx_realize(self):
    super(CTMStaticProblem, self).cvx_realize()
    for link in self.get_links():
      link.rho = link.v_dens.value


class CTMConstrained(CTMStaticProblem):
  def con_ctm(self):
    return list(flatten([geq(link.v_flow, 0),
                         leq(link.v_flow, link.fd.q_max),
                         leq(link.v_flow, link.fd.v * link.v_dens),
                         leq(link.v_flow, link.fd.w * (link.fd.rho_max - link.v_dens)),
                         geq(link.v_dens, 0),
                         leq(link.v_dens, link.fd.rho_max),
                         ] for link in self.get_links()))

  def constraints(self):
    return super(CTMConstrained, self).constraints() + self.con_ctm()

  def check_feasible_constraints(self):
    return list(flatten(
      [geq(link.v_flow, link.flow), geq(link.v_dens, link.rho),leq(link.v_flow, link.flow), leq(link.v_dens, link.rho)]
        for link in self.get_links()
    ))

  def check_feasible(self):
    class FeasibleProgram(SimpleOptimizeMixIn):
      outer = self
      def constraints(self):
        return self.outer.constraints() + self.outer.check_feasible_constraints()

      def cvxify(self):
        self.outer.cvxify()

    op = FeasibleProgram()
    prog  = op.get_program()
    prog.show()
    return not (prog.solve(quiet=True) == inf)

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
    leq(self.route_tt_heuristic(route), 10000.0)
    for route in self.all_routes()
    ]

  def constraints(self):
    return super(ComplacencyConstrained, self).constraints() + self.con_route_tt()


class MinTTT(CTMStaticProblem):
  def objective(self):
    return minimize(sum(link.l * link.v_dens for link in self.get_links()))


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
    return CTMStaticProblem.constraints(self)