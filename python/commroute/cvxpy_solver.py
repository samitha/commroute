from cvxpy import eq, program, variable, minimize, geq, leq, maximize
from numpy import inf
from cr_optimize import OptimizeMixIn, Program, Constraint

__author__ = 'jdr'


class Feasible(object):

  def objective(self):
    return 0.0


class Unconstrained(object):

  def constraints(self):
    return []

class CVXPyConstraint(Constraint):

  def constraint(self):
    if self.type == self.Type.EQ:
      return eq(self.a, self.b)
    if self.type == self.Type.LEQ:
      return leq(self.a, self.b)
    if self.type == self.Type.GEQ:
      return geq(self.a, self.b)

class CVXPyProgram(Program):

  def __init__(self, program):
    super(CVXPyProgram, self).__init__()
    self.program = program

  @classmethod
  def new_program(cls, program):
    prog = cls(program)
    return prog

  def cr_objective(self):
    return self.program.objective.value

  def cr_solve(self, **kwargs):
    """
    @rtype: float
    """
    quiet = kwargs.pop('quiet', True)
    return self.program.solve(quiet, **kwargs)

  def cr_print(self):
    self.program.show()

  def add_constraint(self, constraint):
    if self.type == Constraint.Type.EQ:
      self.add_constraint(CVXPyConstraint(Constraint.Type.LEQ, constraint.a, constraint.b))
      self.add_constraint(CVXPyConstraint(Constraint.Type.GEQ, constraint.a, constraint.b))
    else:
      self.program.constraints.append(constraint.constraint())

class CVXPySolver(OptimizeMixIn):

  def cr_constraint(self, type, a , b):
    return CVXPyConstraint(type, a, b)

  def cr_value(self, var):
    return var.value
    
  def hack_constraints(self, constraints):
    next = []
    for c in constraints:
      if c.type == Constraint.Type.EQ:
        next.append(self.cr_leq(c.a, c.b))
        next.append(self.cr_geq(c.a, c.b))
      else:
        next.append(c)
    return next

  def cr_program(self, goal, cost, constraints):
    constraints = self.hack_constraints(constraints)
    if goal == self.Goal.MIN:
      wrap = minimize
    else:
      wrap = maximize
    return CVXPyProgram.new_program(program(wrap(cost),
      [constraint.constraint() for constraint in constraints]))

  def cr_var(self, name):
    return variable(name=name)

  def is_feasible(self):
    return not (self.get_program().cr_solve() == inf)


class SimpleOptimizeMixIn(Feasible, Unconstrained, CVXPySolver):
  pass
