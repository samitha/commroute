from cvxpy_solver import SimpleOptimizeMixIn
from cr_utils.cr_utils import flatten
from ctm import CTMNetwork
from static_op import LagrangianConstrained

__author__ = 'jdr'


class CTMStaticProblem(CTMNetwork, LagrangianConstrained):
  def variablize(self):
    super(CTMStaticProblem, self).variablize()
    for link in self.get_links():
      link.v_dens = self.create_var('dens: {0}'.format(link.name), self.attr_realizer(link.state, 'density'))


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
        [self.cr_geq(link.v_flow, link.state.flow),
         self.cr_geq(link.v_dens, link.state.density),
         self.cr_leq(link.v_flow, link.state.flow),
         self.cr_leq(link.v_dens, link.state.density)]
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


class MinTTTMixin(CTMStaticProblem):
  def objective(self):
    return sum(link.l * link.v_dens for link in self.get_links())

class MinTTTLagrangianCTMProblem(MinTTTMixin, CTMConstrained):
  pass

