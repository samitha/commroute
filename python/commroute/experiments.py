from demand import RouteDemand, ODDemand
from state_constrained import StateConstrainedNetwork, StateConstrainedComplacentNetwork, StateConstrainedLink
from static_ctm import *
from ctm import FundamentalDiagram
from ctm import DensityCTMLink
from cr_network import Junction

__author__ = 'jdr'

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
  net = DensityCTMNetwork.load('../../networks/exps/exp1/net.json')
  left = net.route_by_names([
    'source', 'left', 'sink'
  ])
  route_demand = RouteDemand(left, .2)
  od_demand = ODDemand(net.link_by_name('source'), net.link_by_name('sink'), .8)
  net.demands.extend([route_demand, od_demand])
  net.dump('../../networks/exps/exp1/net_w_demand.json')

def exp_1_opt():
  """
show that you can add constraints on the fly, and that this increases the objective when you force large densities
  """
  net = MinTTTComplacencyProblem.load('../../networks/exps/exp1/net_w_demand.json')
  prog = net.get_program()
  prog.cr_print()
  prog.cr_solve()
  print 'obnjective', prog.cr_objective()
  left = net.link_by_name('left')
  prog.add_constraint(
    net.cr_geq(left.v_dens, left.fd.v * left.fd.q_max * 1.2)
  )
  prog.cr_print()
  prog.cr_solve()
  print 'obnjective', prog.cr_objective()
  for link in net.get_links():
    link.flow = link.v_flow.value
    link.rho = link.v_dens.value
  net.d3ize()
  print net.check_feasible()

def exp_1_nash():
  net = MinTTTComplacencyProblem.load('../../networks/exps/exp1/net_w_demand.json')
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
  net.dump('../../networks/exps/exp1/net_nash.json')

def exp_1_nash_feasible():
  net = MinTTTComplacencyProblem.load('../../networks/exps/exp1/net_nash.json')
  print 'is feasible: ', net.check_feasible()
  for route in net.all_routes():
    print 'route', route
    print route.travel_time()
  for link in net.get_links():
    print 'link', link
    print 'flow', link.flow
    print 'rho', link.rho
  print 'net tt', net.total_travel_time()
  program = net.get_program()
  left = net.link_by_name('left')
  program.add_constraint(net.cr_geq(left.v_dens,left.fd.rho_crit()*1.5))
  program.cr_print()
  program.cr_solve()
  net.realize()
  for link in net.get_links():
    print 'link', link
    print 'flow', link.flow
    print 'rho', link.rho
  print 'net tt', net.total_travel_time()

def exp_1():
  exp_1_create()
  exp_1_demands()
  exp_1_opt()
  exp_1_nash()
  exp_1_nash_feasible()

def exp_2():
  """
  starting to figure out stateconstrained things
  """
  net = StateConstrainedComplacentNetwork.load('../../networks/exps/exp2/lf_rc.json')
  net.get_program().cr_print()


def exp_3_setup():
  net = StateConstrainedComplacentNetwork()
  l = 1; v = 1; w = 1; q_max = 1; rho_max = 2; r = 1;

  fd = FundamentalDiagram.triangular(
    v=v,q_max=q_max,rho_max=rho_max
  )

  l_rho = 1.372281323
  r_rho = 3 - l_rho

  source = StateConstrainedLink(
    fd=fd,
    name='source',
    state=StateConstrainedLink.State.ANY,
    l=l,
    flow=r,
    rho=fd.rho_ff(r)
  )
  left = StateConstrainedLink(
    fd=fd,
    name='left',
    state=StateConstrainedLink.State.CONG,
    l=2*l,
    flow=fd.flow_cong(l_rho),
    rho=l_rho
  )
  right = StateConstrainedLink(
    fd=fd,
    name='right',
    state=StateConstrainedLink.State.CONG,
    l=l,
    flow=fd.flow_cong(r_rho),
    rho=r_rho
  )
  sink = StateConstrainedLink(
    fd=fd,
    name='sink',
    state=StateConstrainedLink.State.ANY,
    l=l,
    flow=r,
    rho=fd.rho_ff(r)
  )
  js = [
    Junction([source],[left,right]),
    Junction([left,right],[sink]),
  ]
  [net.add_junction(junction) for junction in js]
  net.dump('../../networks/exps/exp3/net.json')
  left_demand = RouteDemand(
    route=net.route_by_names(['source','left','sink']),
    flow=.2
  )
  od_demand = ODDemand(
    source=source,
    sink=sink,
    flow=.8
  )
  net.demands.append(left_demand)
  net.demands.append(od_demand)
  net.dump('../../networks/exps/exp3/net_demand.json')

def exp_3_info():
  net = StateConstrainedComplacentNetwork.load('../networks/exps/exp3/net_demand.json')
  print 'ttt previous', net.total_travel_time()
  net.get_program().cr_solve()
  net.realize()
  print 'ttt after complacence optimize', net.total_travel_time()
  for route in net.all_routes():
    print 'route', route
    print 'heur tt', net.route_tt_heuristic(route).value
    print 'actual tt', route.travel_time()
  net = StateConstrainedNetwork.load('../networks/exps/exp3/net_demand.json')
  net.get_program().cr_solve()
  net.realize()
  print 'ttt after non-comp optimize', net.total_travel_time()

def exp_4():
  net = StateConstrainedNetwork.load('../networks/fpnet_with_demands.json')
  net.objective = lambda: 0
  for link in net.get_links():
    link.set_state(link.State.CONG)
  net.get_program().cr_solve()
  net.realize()
  print net.total_travel_time()
  for link in net.get_links():
    print 'link', link
    print link.rho
    print link.flow
  net.dump('../networks/exps/exp4/net_cong.json')
  net = StateConstrainedComplacentNetwork.load('../networks/exps/exp4/net_cong.json')
  net.get_program().cr_print()
  net.get_program().cr_solve()
  net.realize()
  print net.total_travel_time()


if __name__ == '__main__':
  exp_4()

