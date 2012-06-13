from cr_utils import Dumpable
from cr_network import CRNetwork
from demand import Demand
from cvxpy import program, minimize

__author__ = 'jdr'

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

  def cvx_realize(self):
    pass


class Feasible:

  def objective(self):
    return minimize(0.0)


class Unconstrained:

  def constraints(self):
    return []

class SimpleOptimizeMixIn(Feasible, Unconstrained, OptimizeMixIn):
  pass