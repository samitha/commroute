from collections import defaultdict
from itertools import ifilter

class Queue(object):
  """docstring for Queue"""
  def __init__(self):
    super(Queue, self).__init__()
    self.queue = list()
    
  def enqueue(self, v):
    """docstring for enqueue"""
    self.queue.append(v)
    
  def dequeue(self):
    """docstring for dequeueu"""
    return self.queue.pop(0)
    
  def is_empty(self):
    return not self.queue

def bfs(s):
  """docstring for bfs"""
  class Color(object):
    """docstring for Color"""
    unf = 'unfilled'
    sha = 'shaded'
    fil = 'filled'
  net = s.net         
  colors = defaultdict(lambda: Color.unf)
  d = defaultdict(lambda: -1)
  pi = defaultdict(lambda: None)
  queue = Queue()
  colors[s] = Color.sha
  d[s] = 0
  queue.enqueue(s)
  while not queue.is_empty():
    u = queue.dequeue()
    for v in ifilter(lambda x: colors[x] is Color.unf,u.neighbors()):
      colors[v] = Color.sha
      d[v] = d[u] + 1
      pi[v] = u
      queue.enqueue(v)
    colors[u] = Color.fil
  return d,pi,colors

def all_paths(s):
  """docstring for bfs"""
  class Color(object):
    """docstring for Color"""
    unf = 'unfilled'
    sha = 'shaded'
    fil = 'filled'
  colors = defaultdict(lambda: Color.unf)
  pi = defaultdict(lambda: list())
  queue = Queue()
  colors[s] = Color.sha
  pi[s].append([])
  queue.enqueue(s)
  while not queue.is_empty():
    u = queue.dequeue()
    for v in u.neighbors():
      pi[v]+=[path + [u] for path in pi[u]]
    for v in ifilter(lambda x: colors[x] is Color.unf,u.neighbors()):
      colors[v] = Color.sha
      queue.enqueue(v)
    colors[u] = Color.fil
  return pi
  
  
  
  
    