from cvxpy import geq, leq, quad_over_lin, variable, hstack, minimize, eq
from cvxpy import max as cvx_max
from cr_utils import flatten
from ctm import DensityCTMNetwork
from static_op import LagrangianConstrained

__author__ = 'jdr'


class CTMStaticProblem(DensityCTMNetwork, LagrangianConstrained):
  def cvxify(self):
    super(CTMStaticProblem, self).cvxify()
    for link in self.get_links():
      link.v_dens = variable(name='dens: {0}'.format(link.name))
      # this next line isn't useful right now
      # link.d3_value = lambda: link.v_dens.value


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

  def check_feasible(self):
    extra_cons = list(flatten(
      [eq(link.v_flow, link.flow), eq(link.v_dens, link.rho)]
        for link in self.get_links()
    ))


class ComplianceConstrained(CTMConstrained):
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
    for link in route.get_links
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
    return minimize(sum(link.l * link.v_dens for link in self.get_links()))


class MinTTTComplianceProblem(MinTTT, ComplianceConstrained):
  def __init__(self):
    super(MinTTTComplianceProblem, self).__init__()

  def objective(self):
    return MinTTT.objective(self)

  def constraints(self):
    return ComplianceConstrained.constraints(self)


class MinTTTLagrangianCTMProblem(MinTTT, CTMConstrained):
  def __init__(self):
    super(MinTTTLagrangianCTMProblem, self).__init__()

  def objective(self):
    return MinTTT.objective(self)

  def constraints(self):
    return CTMStaticProblem.constraints(self)