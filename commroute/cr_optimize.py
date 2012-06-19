__author__ = 'jdr'

def do_nothing():
  pass

class Constraint(object):
  class Type:
    EQ = 0
    GEQ = 1
    LEQ = 2

  def __init__(self, type, a, b):
    """

    :param type: eq, geq, or leq
    :param a: first expression
    :param b: second expression
    :returns: Constraint
    """

    self.type = type
    self.a = a
    self.b = b

  def constraint(self):
    raise NotImplementedError("abstract")


class Solver(object):

  class Goal:
    MIN = 0
    MAX = 1

  def reset_solver(self):
    self.variables = []

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
    except AttributeError:
      self.reset_solver()
      return self.variables

  def cr_program(self, goal, cost, constraints):
    """
    the program to be solved
    @param goal:
    @param cost:
    @param constraints:
    @return:
    @rtype: Program
    """
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
    return self.cr_constraint(Constraint.Type.LEQ, a, b)

  def cr_geq(self,a,b):
    return self.cr_constraint(Constraint.Type.GEQ, a, b)

  def cr_eq(self,a,b):
    return self.cr_constraint(Constraint.Type.EQ, a, b)

  def cr_constraint(self, type, a , b):
    """
    unified constraint method
    @rtype: Constraint
    """
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
    """helper function for getting programs"""
    self.variablize()
    return self.cr_program(self.goal(), self.objective(), self.constraints())

  def is_feasible(self):
    raise NotImplementedError("abstract")

