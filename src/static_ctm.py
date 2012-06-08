from ctm import *
from crnetwork import *
from cvxpy import variable, eq, leq, geq, minimize, program
from itertools import product, chain

def flatten(listOfLists):
    "Flatten one level of nesting"
    return chain.from_iterable(listOfLists)


class StaticCvxNetwork(CRNetwork):
	"""docstring for StaticCvxNetwork"""
	def __init__(self, *args, **kwargs):
		super(StaticCvxNetwork, self).__init__(*args, **kwargs)
		self.cvxify()
		
	def cvxify(self):
		"""docstring for cvxify"""
		self.cache_props()
		for link in self.links():
			link.v_flow = variable(name='flow: {0}'.format(link.name))
			link.v_dens = variable(name='dens: {0}'.format(link.name))
		for (source,sink), routes in self.od_routes.iteritems():
			for route in routes:
				route.v_flow = variable(name = 'rf: o: {0}, d: {1}'.format(source.name, sink.name))
				
			

class Demand(object):
	"""docstring for Demand"""
	def __init__(self, net, flow):
		super(Demand, self).__init__()
		self.net = net
		self.flow = flow

class RouteDemand(Demand):
	"""docstring for RouteDemand"""
	def __init__(self, route, flow):
		self.route = route
		super(RouteDemand, self).__init__(route.net, flow)

class ODDemand(Demand):
	"""docstring for RouteDemand"""
	def __init__(self, source, sink, flow):
		super(ODDemand, self).__init__(source.net, flow)
		self.source = source
		self.sink = sink

class LinkDemand(Demand):
	"""docstring for LinkDemand"""
	def __init__(self, link, flow):
		super(LinkDemand, self).__init__(link.net, flow)
		self.link = link
		
class StaticProblem(object):
	"""docstring for StaticProblem"""
	def __init__(self, net, demands):
		super(StaticProblem, self).__init__()
		self.net = net
		self.demands = demands
		
	def con_junc(self):
		return [eq(sum(link.v_flow for link in junction.in_links),
							 sum(link.v_flow for link in junction.out_links))
							for junction in self.net.junctions]
							
	def con_od_flows(self):
		od_demands = filter(lambda dem: isinstance(dem,ODDemand), self.demands)
		return [eq(sum(route.v_flow for route in link.routes()),link.v_flow) 
							for link in self.net.links()] + [
					 eq(sum(route.v_flow for route in self.net.od_routes[dem.source,dem.sink]),dem.flow)
							for dem in od_demands]
							
	def con_ctm(self):
		return list(flatten([geq(link.v_flow,0),
										leq(link.v_flow,link.fd.q_max),
										leq(link.v_flow,link.fd.v*link.v_dens),
										leq(link.v_flow,link.fd.w*(link.fd.rho_max - link.v_dens)),
										geq(link.v_dens,0),
										leq(link.v_dens,link.fd.rho_max),
										] for link in self.net.links()))
										
	
	def obj_min_ttt(self):
		return minimize(sum(link.l*link.v_dens for link in self.net.links()))
		
	def obj_feas(self):
		return minimize(0)
	
	def con_feas(self):
		"""docstring for con_feas"""
		return self.con_ctm() + self.con_od_flows() #+ self.con_junc() 

	def solve_feasible(self):
		self.net.cvxify()
		p = program(self.obj_feas(), self.con_feas())
		p.solve()
		return p

	def solve_ttt(self):
		self.net.cvxify()
		p = program(self.obj_min_ttt(), self.con_feas())
		p.solve()
		return p
		
		
		
def main():
	"""docstring for main"""
	net = load_ctm('networks/fpnet.json',net_class = StaticCvxNetwork)
	source = list(net._sources())[0]
	sinks = net._sinks()
	dems = [ODDemand(source, sink, flow = .05) for sink in sinks]
	problem = StaticProblem(net = net, demands = dems)
	prog = problem.solve_ttt()
	prog.show()
	for link in net.links():
		print link.name
		print link.v_flow.value
		print link.v_dens.value
	print prog.objective.value
	print '\n\n\n'
	for junction in net.junctions:
		print sum(link.v_flow.value for link in junction.in_links)
		print sum(link.v_flow.value for link in junction.out_links)
		print ''
	
	
	
		
if __name__ == '__main__':
	main()
