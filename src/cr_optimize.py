from cr_utils import Dumpable
from crnetwork import CRNetwork
from demand import Demand
from cvxpy import program, minimize

__author__ = 'jdr'


class CvxNetworkOptimizationProblem(Dumpable):

  def __init__(self, net, demands):
    super(CvxNetworkOptimizationProblem,self).__init__()
    self.net = net
    self.demands = demands

  NET_CLASS = CRNetwork


  def jsonify(self):
    return {
      'net': self.net.jsonify(),
      'demands': [demand.jsonify() for demand in self.demands]
    }


  @classmethod
  def load_with_json_data(cls, data, **kwargs):
    net = cls.NET_CLASS.load_with_json_data(data['net'])
    net.cache_props()
    demands = [Demand.load_with_json_data(demand, net=net) for demand in data['demands']]
    return cls(
      net=net,
      demands=demands
    )


class OptimizeMixIn(object):

  def constraints(self):
    raise NotImplementedError("implement me")

  def objective(self):
    raise NotImplementedError("implement me")

  def cvxify(self):
    pass

  def get_program(self):
    self.cvxify()
    return program(self.objective(), self.constraints())

  def solve_problem(self):
    program = self.get_program()
    program.solve()
    return program


class Feasible:

  def objective(self):
    return minimize(0.0)


class Unconstrained:

  def constraints(self):
    return []

class SimpleOptimizeMixIn(Feasible, Unconstrained, OptimizeMixIn):
  pass