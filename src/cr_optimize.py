from operator import eq
from cvxopt.modeling import variable
from cvxpy.interface import leq, geq, maximize
from cr_utils import Dumpable
from cr_network import CRNetwork
from demand import Demand
from cvxpy import program, minimize

__author__ = 'jdr'

def do_nothing():
  pass



class Solver(object):

  class Goal:
    MIN = 0
    MAX = 1

  @staticmethod
  def attr_realizer(obj, attr):
    def helper(val):
      setattr(obj, attr, val)
    return helper

  def create_var(self, name, realizer = do_nothing):
    variable = self.cr_var(name)
    variable.realizer = realizer
    self.add_var(variable)
    return variable

  def add_var(self, var):
    self.all_vars().append(var)

  def all_vars(self):
    try:
      return self.variables
    except:
      self.variables = []
      return self.variables

  def cr_program(self, goal, cost, constraints):
    raise NotImplementedError("implement me")

  def cr_value(self, var):
    raise NotImplementedError("implement me")

  def cr_var(self, name):
    raise NotImplementedError("implement me")

  def realize(self, var=None):
    if var is None:
      self.realize_all()
    else:
      var.realizer(self.cr_value(var))

  def realize_all(self):
    for var in self.all_vars():
      self.realize(var)

  def cr_leq(self,a,b):
    raise NotImplementedError("implement me")

  def cr_geq(self,a,b):
    raise NotImplementedError("implement me")

  def cr_eq(self,a,b):
    raise NotImplementedError("implement me")

class Program(object):

  def cr_solve(self, **kwargs):
    raise NotImplementedError("implement me")

  def cr_objective(self):
    raise NotImplementedError("implement me")

  def add_constraint(self, constraint):
    raise NotImplementedError("implement me")

  def cr_print(self):
    pass

class OptimizeMixIn(Solver):

  def constraints(self):
    raise NotImplementedError("implement me")

  def objective(self):
    raise NotImplementedError("implement me")

  def goal(self):
    return self.Goal.MIN

  def variablize(self):
    pass

  def get_program(self):
    self.variablize()
    return self.cr_program(self.goal(), self.objective(), self.constraints())

