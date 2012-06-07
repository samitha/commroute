from networkx import DiGraph

class Link(object):
	"""docstring for Link"""
	def __init__(self, net = None, name = None):
		super(Link, self).__init__()
		self.net = net
		self.name = str(name)
		
	def neighbors(self):
		return self.net.neighbors(self)
		
	def upstream_links(self):
		return self.net.in_edges(self)
		
	def downstream_links(self):
		return self.net.out_edges(self)
		
	def is_sink(self):
		return len(self.downstream_links()) == 0

	def is_source(self):
		return len(self.upstream_links()) == 0
		
	def __repr__(self):
		if self.name is None:
			return super(Link,self).__repr__()
		return self.name
		
	def __str__(self):
		return self.__repr__()
		
		
class Junction(object):
	"""docstring for Junction"""
	def __init__(self, in_links, out_links):
		super(Junction, self).__init__()
		self.in_links = in_links
		self.out_links = out_links
		
	def edges(self):
		"""docstring for edges"""
		return [(i,o) for i in self.in_links for o in self.out_links]
		
		


class CRNetwork(DiGraph):
	"""docstring for CRNetwork"""
	def __init__(self):
		super(CRNetwork, self).__init__()
		
	def add_junction(self, junction):
		"""docstring for add_junction"""
		self.add_edges_from(junction.edges())
	
		

def main():
	"""docstring for main"""
	net = CRNetwork()
	links = [Link(net) for _ in range(3)]
	junction = Junction([links[0]],[links[1], links[2]])
	net.add_junction(junction)
	print [link.neighbors() for link in links]
	print [link.upstream_links() for link in links]
	print [link.downstream_links() for link in links]
	print [link.is_sink() for link in links]
	print [link.is_source() for link in links]

		
if __name__ == '__main__':
	main()