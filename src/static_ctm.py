from cvxpy import geq, leq, quad_over_lin, variable, hstack, minimize
from cvxpy import max as cvx_max
from cr_utils import flatten
from ctm import DensityCTMNetwork
from static_op import LagrangianStaticProblem, LagrangianConstrained

__author__ = 'jdr'



class CTMStaticProblem(DensityCTMNetwork, LagrangianStaticProblem):

  def cvxify(self):
    super(CTMStaticProblem,self).cvxify()
    for link in self.links():
      link.v_dens = variable(name='dens: {0}'.format(link.name))
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
