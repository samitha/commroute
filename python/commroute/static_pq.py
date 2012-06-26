from cvxpy_solver import SimpleOptimizeMixIn
from complacency import ComplacencyConstrained
from cr_utils.cr_utils import flatten
from point_queue import FlowLinkNetwork, PQState

__author__ = 'jdr'

from static_op import LagrangianConstrained


class CapacityConstrained(LagrangianConstrained, FlowLinkNetwork):

  def con_capacity(self):
    return list(
      flatten(
        [
          self.cr_geq(link.v_flow, 0.0),
          self.cr_leq(link.v_flow, link.q_max)
        ]
        for link in self.get_links()
      )
    )

  def constraints(self):
    return super(CapacityConstrained, self).constraints() + self.con_capacity()

  def check_feasible(self):
    """
    checks the feasibility of the problem
    @rtype: bool
    """
    def check_feasible_constraints():
      return list(flatten(
        [self.cr_geq(link.v_flow, link.state.flow),
         self.cr_leq(link.v_flow, link.state.flow)]
          for link in self.get_links()
      ))

    class FeasibleProgram(SimpleOptimizeMixIn):
      outer = self
      def constraints(self):
        return self.outer.constraints() + check_feasible_constraints()

      def variablize(self):
        self.outer.variablize()

    op = FeasibleProgram()
    op.get_program().cr_print()
    return op.is_feasible()


class MinTTT(LagrangianConstrained):

  def objective(self):
    return sum([
      link.flow_flow_latency(link.v_flow)
      for link in self.get_links()
    ])


class MinTTTFlowLinkProblem(MinTTT, CapacityConstrained):
  pass

class MinTTTFlowLinkComplacencyProblem(MinTTTFlowLinkProblem, ComplacencyConstrained):

  def route_tt_heuristic(self, route):
    return sum(
      link.travel_time(PQState(link.v_flow))
      for link in route.links
    )