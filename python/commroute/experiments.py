from complacency import PQCC, MinTTTFlowLinkComplacencyProblem
from compliance import CompliantRouteDemand
from point_queue import MM1Latency
from point_queue import FlowLink, AffineLatency
from static_pq import MinTTTFlowLinkProblem
from demand import RouteDemand, ODDemand
from state_constrained import StateConstrainedNetwork, StateConstrainedComplacentNetwork, StateConstrainedLink
from static_ctm import *
from ctm import FundamentalDiagram
from ctm import CTMLink
from cr_network import Junction
from data_fixer import DataFixer

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
  source = CTMLink(
    net=net,
    name='source',
    l=l,
    fd=fd,
    rho=1.0
  )
  left = CTMLink(
    net=net,
    name='left',
    l=l,
    fd=fd,
    rho=1.0
  )
  right = CTMLink(
    net=net,
    name='right',
    l=2 * l,
    fd=fd,
    rho=1.0
  )
  sink = CTMLink(
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
    cong_state=StateConstrainedLink.CongState.ANY,
    l=l,
    flow=r,
    density=fd.rho_ff(r)
  )
  left = StateConstrainedLink(
    fd=fd,
    name='left',
    cong_state=StateConstrainedLink.CongState.CONG,
    l=2*l,
    flow=fd.flow_cong(l_rho),
    density=l_rho
  )
  right = StateConstrainedLink(
    fd=fd,
    name='right',
    cong_state=StateConstrainedLink.CongState.CONG,
    l=l,
    flow=fd.flow_cong(r_rho),
    density=r_rho
  )
  sink = StateConstrainedLink(
    fd=fd,
    name='sink',
    cong_state=StateConstrainedLink.CongState.ANY,
    l=l,
    flow=r,
    density=fd.rho_ff(r)
  )
  js = [
    Junction([source],[left,right]),
    Junction([left,right],[sink]),
  ]
  [net.add_junction(junction) for junction in js]
  net.dump('../networks/exps/exp3/net.json')
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
  net.dump('../networks/exps/exp3/net_demand.json')

def exp_3_info():
  net = StateConstrainedComplacentNetwork.load('../networks/exps/exp3/net_demand.json')
  for cls in net.__class__.__mro__:
    print cls
  print 'ttt previous', net.total_travel_time()
  net.get_program().cr_print()
  net.get_program().cr_solve(quiet=False)
  for link in net.get_links():
    print link
    print link.v_dens.value
    print link.l
  net.realize()
  print 'ttt after complacence optimize', net.total_travel_time()
  for route in net.all_routes():
    print 'route', route
    print 'heur tt', net.route_tt_heuristic(route).value
    print 'actual tt', net.route_travel_time(route)
  net = StateConstrainedNetwork.load('../networks/exps/exp3/net_demand.json')
  net.get_program().cr_solve()
  net.realize()
  print 'ttt after non-comp optimize', net.total_travel_time()

def exp_4():
  net = StateConstrainedNetwork.load('../networks/fpnet_with_demands.json')
  net.objective = lambda: 0
  l_9 = net.link_by_name('9')
  l_3 = net.link_by_name('3')
  l_8 = net.link_by_name('8')
  for link in net.get_links():
    if link in [l_9, l_3, l_8]:
      link.set_cong_state(link.CongState.CONG)
    else:
      link.set_cong_state(link.CongState.FF)
  net.get_program().cr_solve()
  net.realize()
  print net.total_travel_time()
  net.dump('../networks/exps/exp4/net_cong.json')

  net = StateConstrainedNetwork.load('../networks/exps/exp4/net_cong.json')
  net.get_program().cr_solve()
  net.realize()
  print net.total_travel_time()

  net = StateConstrainedComplacentNetwork.load('../networks/exps/exp4/net_cong.json')
  net.scale = 1.1
  net.get_program().cr_solve()
  net.realize()
  print net.total_travel_time()

  net = StateConstrainedComplacentNetwork.load('../networks/exps/exp4/net_cong.json')
  net.scale = 1000.0
  net.get_program().cr_solve()
  net.realize()
  print net.total_travel_time()

  net = StateConstrainedComplacentNetwork.load('../networks/exps/exp4/net_cong.json')
  net.scale = 10.0
  net.get_program().cr_solve()
  net.realize()
  print net.total_travel_time()

def exp_5():
  net = MinTTTFlowLinkProblem()
  source = FlowLink(
    name='source',
    latency=AffineLatency(
      a=1.0,
      b=0.0
    ),
    q_max=1.0,
    flow=1.0
  )
  sink = FlowLink(
    name='sink',
    latency=AffineLatency(
      a=1.0,
      b=0.0
    ),
    q_max=1.0,
    flow=1.0
  )
  left = FlowLink(
    name='left',
    latency=AffineLatency(
      a=1.0,
      b=0.0
    ),
    q_max=1.0,
    flow=2.0/3
  )
  right = FlowLink(
    name='right',
    latency=AffineLatency(
      a=.5,
      b=.5
    ),
    q_max=1.0,
    flow=1.0/3
  )
  js = [
    Junction([source], [left,right]),
    Junction([left,right], [sink]),
    ]
  [net.add_junction(j) for j in js]
  left_demand = RouteDemand(
    flow=.1,
    route=net.route_by_names(['source','left','sink'])
  )
  right_demand = RouteDemand(
    flow=.1,
    route=net.route_by_names(['source','right','sink'])
  )
  od_demand = ODDemand(
    source=source,
    sink=sink,
    flow=.8
  )
  net.demands.extend([left_demand,right_demand,od_demand])
  print net.check_feasible()
  net.dump('../networks/exps/exp5/net_nash.json')

def exp_5_test():
  net = MinTTTFlowLinkProblem.load('../networks/exps/exp5/net_nash.json')
  print net.total_travel_time()
  for route in net.all_routes():
    print route
    print net.route_travel_time(route)
  net.get_program().cr_solve()
  net.realize()
  print net.total_travel_time()
  for route in net.all_routes():
    print route
    print net.route_travel_time(route)
  net = MinTTTFlowLinkComplacencyProblem.load('../networks/exps/exp5/net_nash.json')
  net.scale = 1.01
  net.get_program().cr_solve()
  net.realize()
  print net.total_travel_time()
  for route in net.all_routes():
    print route
    print net.route_travel_time(route)

def exp_6():
  source = FlowLink(
    name = 'source',
    q_max=1.0,
    latency=MM1Latency(
      rho=1.0,
      mu=1.0
    )
  )
  sink = FlowLink(
    name = 'sink',
    q_max=1.0,
    latency=MM1Latency(
      rho=1.0,
      mu=1.0
    )
  )
  j = Junction([source], [sink])
  dem = ODDemand(
    source=source,
    sink=sink,
    flow=.5
  )
  net = MinTTTFlowLinkProblem()
  net.add_junction(j)
  net.demands.append(dem)
  net.dump('../networks/exps/exp6/net.json')
  net.get_program().cr_print()
  net.get_program().cr_solve(quiet=False)

def exp_7_setup():
  net = PQCC.load('../networks/exps/exp5/net_nash.json')
  net.demands = []
  left_demand = CompliantRouteDemand(
    route = net.route_by_names(['source','left','sink']),
    flow = 2./3,
    compliance=.8
  )
  right_demand = CompliantRouteDemand(
    route = net.route_by_names(['source','right','sink']),
    flow = 1./3,
    compliance=.8
  )
  net.demands.append(left_demand)
  net.demands.append(right_demand)
  net.dump('../networks/exps/exp7/net.json')

def exp_7_test():
  net = PQCC.load('../networks/exps/exp7/net.json')
  net.run()
  net = PQCC.load('../networks/exps/exp7/net.json')
  net.scale = 1.01
  net.run()
  net = PQCC.load('../networks/exps/exp7/net.json')
  net.scale = 10.0
  net.run()
  net = PQCC.load('../networks/exps/exp7/net.json')
  net.scale = 1.01
  net.run()

def exp_8_scala():
  net = MinTTTLagrangianCTMProblem.load("../networks/exps/exp8/net.json")
  route = net.all_routes()[0]
  o = list(net.sources)[0]
  d = list(net.sinks)[0]
  r_demand  = RouteDemand(route = route, flow = .000001)
  o = route.links[0]
  d = route.links[-1]
  flow = min(link.fd.q_max for link in net.get_links())
  print 'flow', flow
  od_demand = ODDemand(source = o, sink = d, flow = flow*.9)
  net.demands.extend([r_demand, od_demand])
  net.dump("../networks/exps/exp8/netd.json")
  print 'n links', len(net.get_links())
  net.get_program().cr_solve(quiet=False)
  

def exp_9():  
  net = DataFixer.load("/Users/jdr/Documents/github/commroute/python/networks/exps/exp9/net.json")
  fn = '/Users/jdr/Documents/github/commroute/python/networks/exps/exp9/flowdata.csv'
  net.solve_with_data(fn)
  for link in net.get_links():
    print link, link.v_flow.value, link.v_dens.value
  net.realize()
  net.dump('/Users/jdr/Documents/github/commroute/python/networks/exps/exp9/bignetstate.json')
  
def exp_9_next():
  net = DataFixer.load('/Users/jdr/Documents/github/commroute/python/networks/exps/exp9/bignetstate.json')
  net.cache_props()
  for source in net.sources:
    for sink in net.sinks:
      routes = net.od_routes[source,sink]
      print '\n\n'
      print 'o', source, 'd', sink
      for route in routes:
        print net.route_travel_time(route) / net.ff_travel_time(route)
        
def exp_9_hist():
  import pylab
  net = DataFixer.load('/Users/jdr/Documents/github/commroute/python/networks/exps/exp9/bignetstate.json')
  net.cache_props()
  for link in net.get_links():
    if link.congestion_level() < -1.0:
      print 'bad 1'
      print link.state.flow / link.fd.q_max
  pylab.hist([
    link.congestion_level()
    for link in net.get_links()
  ], bins = 100)
  pylab.show()

  
def exp_10():
  net = MinTTTLagrangianCTMProblem.load("/Users/jdr/Desktop/out.json")
  net.cache_props()
  print len(net.sources)
  print len(net.sinks)
  print len(net.all_routes())
  print len(net.get_links())
  # for route in net.all_routes():
  #   print net.max_flow(route), net.ff_travel_time(route)
  import networkx
  print networkx.is_weakly_connected(net)
  with open('/Users/jdr/Desktop/flowdata.csv','r') as fn:
    flows = {}
    for row in fn:
      splits = row[:-1].split(';')
      print splits
      name = splits[2]
      flow = float(splits[1])
      density = float(splits[0])
      flows[name] = {
        'flow': flow,
        'density': density
      }
  def get_flows(link):
    try:
      return flows[link.name]['flow']
    except:
      return 0.0
  for junction in net.junctions:
    lsum = sum(get_flows(link) for link in junction.in_links)
    rsum = sum(get_flows(link) for link in junction.out_links)
    print lsum, rsum
  for link in net.get_links():
    print bool(link.fd.q_max < get_flows(link)), link.fd.q_max, get_flows(link)
  # for source in net.sources:
  #   for sink in net.sinks:
  #     routes = net.od_routes[source,sink]
  #     print '\n\n###\n\n'
  #     print 'source', source, 'sink', sink
  #     for route in routes:
  #       print net.ff_travel_time(route)

exp_9_hist()
