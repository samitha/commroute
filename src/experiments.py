from demand import RouteDemand, ODDemand

__author__ = 'jdr'
from static_ctm import *
from ctm import FundamentalDiagram
from ctm import DensityCTMLink
from cr_network import Junction

def exp_1_create():
  """
  create the base network
  """
  v = 1.0
  w = .5
  rho_max = 3
  q_max = 1.0
  l = 1.0

  fd = FundamentalDiagram(
    v=v,
    w=w,
    rho_max=rho_max,
    q_max=q_max
  )

  net = DensityCTMNetwork()
  source = DensityCTMLink(
    net=net,
    name='source',
    l=l,
    fd=fd,
    rho=1.0
  )
  left = DensityCTMLink(
    net=net,
    name='left',
    l=l,
    fd=fd,
    rho=1.0
  )
  right = DensityCTMLink(
    net=net,
    name='right',
    l=2 * l,
    fd=fd,
    rho=1.0
  )
  sink = DensityCTMLink(
    net=net,
    name='sink',
    l=l,
    fd=fd,
    rho=1.0
  )
  junctions = [
    Junction([source], [left, right]),
    Junction([left, right], [sink]),
    ]
  for junction in junctions:
    net.add_junction(junction)

  net.dump("networks/exps/exp1/net.json")


def exp_1_demands():
  net = DensityCTMNetwork.load('networks/exps/exp1/net.json')
  left = net.route_by_names([
    'source', 'left', 'sink'
  ])
  route_demand = RouteDemand(left, .2)
  od_demand = ODDemand(net.link_by_name('source'), net.link_by_name('sink'), .8)
  net.demands.extend([route_demand, od_demand])
  net.dump('networks/exps/exp1/net_w_demand.json')


def exp_1_opt():
  '''
  @return: nothing, demonstrate

  show that you can add constraints on the fly, and that this increases the objective when you force large densities
  '''
  net = MinTTTComplianceProblem.load('networks/exps/exp1/net_w_demand.json')
  prog = net.get_program()
  prog.show()
  prog.solve()
  print 'obnjective', prog.objective.value
  left = net.link_by_name('left')
  prog.constraints.extend([
    geq(left.v_dens, left.fd.v * left.fd.q_max * 1.2)
  ])
  prog.show()
  prog.solve()
  print 'obnjective', prog.objective.value
  for link in net.get_links():
    link.flow = link.v_flow.value
    link.rho = link.v_dens.value
  net.d3ize()
  print net.check_feasible()


def exp_1_nash():
  net = MinTTTComplianceProblem.load('networks/exps/exp1/net_w_demand.json')
  left = net.link_by_name('left')
  right = net.link_by_name('right')
  left.flow = .75
  left.rho = left.fd.rho_cong(left.flow)
  right.flow = 1 - left.flow
  right.rho = right.fd.rho_ff(right.flow)
  source = net.link_by_name('source')
  sink = net.link_by_name('sink')
  source.flow = 1.0
  source.rho = source.fd.rho_ff(source.flow)
  sink.flow = 1.0
  sink.rho = source.fd.rho_ff(sink.flow)
  net.dump('networks/exps/exp1/net_nash.json')

def exp_1_nash_feasible():
  net = MinTTTComplianceProblem.load('networks/exps/exp1/net_nash.json')
  print net.check_feasible()

def main():
#  exp_1_create()
#  exp_1_demands()
#  exp_1_opt()
#  exp_1_nash()
  exp_1_nash_feasible()

if __name__ == '__main__':
  main()
