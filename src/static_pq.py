from cvxpy.interface import geq, leq, minimize
from cr_utils import flatten
from point_queue import FlowLinkNetwork

__author__ = 'jdr'

from static_op import LagrangianConstrained


class CapacityConstrained(LagrangianConstrained, FlowLinkNetwork):

  def con_capacity(self):
    return list(
      flatten(
        [
          geq(link.v_flow, 0.0),
          leq(link.v_flow, link.q_max)
        ]
        for link in self.get_links()
      )
    )

  def constraints(self):
    return super(CapacityConstrained, self).constraints() + self.con_capacity()


class MinTTT(LagrangianConstrained):

  def objective(self):
    return minimize(sum([
      link.flow_flow_latency(link.v_flow)
      for link in self.get_links()
    ]))


class MinTTTFlowLinkProblem(MinTTT, CapacityConstrained):
  pass



def main():
  net = MinTTTFlowLinkProblem.load('networks/flownet.json')
  program = net.get_program()
  program.show()
  program.solve()
  print program.objective.value
  for route in net.all_routes():
    print route.v_flow.value
  net = MinTTTFlowLinkProblem.load("networks/flownet_od.json")
  program = net.get_program()
  program.show()
  program.solve()
  print program.objective.value
  for route in net.all_routes():
    print route.v_flow.value


if __name__ == '__main__':
  main()
