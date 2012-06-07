from crnetwork import Link, CRNetwork, Junction
from random import random

class FundamentalDiagram(object):
	"""docstring for FundamentalDiagram"""
	def __init__(self, v, w, rho_max, q_max):
		super(FundamentalDiagram, self).__init__()
		self.v = v
		self.w = w
		self.rho_max = rho_max
		self.q_max = q_max
		

class CTMLink(Link):
	"""docstring for CTMLink"""
	def __init__(self, l, fd, *args, **kwargs):
		super(CTMLink, self).__init__(*args, **kwargs)
		self.l = l
		self.fd = fd
		
class DensityCTMLink(CTMLink):
	"""docstring for DensityCTMLink"""
	def __init__(self, rho = 0.0, *args, **kwargs):
		super(DensityCTMLink, self).__init__(*args,**kwargs)
		self.rho = rho
		
def main():
	"""docstring for main"""
	fd = FundamentalDiagram(1,2,5,3)
	net = CRNetwork()
	n_links = 10
	links = [DensityCTMLink(rho = random(), l = random(), fd = fd, net = net, name = _) for _ in range(n_links)]
	j1 = Junction([links[0],links[1]],[links[2],links[3],links[4]])
	j2 = Junction([links[2],links[5]],[links[6],links[7]])
	j3 = Junction([links[7]],[links[8],links[9]])
	[net.add_junction(j) for j in [j1,j2,j3]]
	print [link.neighbors() for link in links]
	print [link.upstream_links() for link in links]
	print [link.downstream_links() for link in links]
	print [link.is_sink() for link in links]
	print [link.is_source() for link in links]
	
if __name__ == '__main__':
	main()
	