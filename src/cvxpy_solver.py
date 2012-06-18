from cvxpy import eq, program, variable, minimize, geq, leq
from numpy import inf
from cr_optimize import OptimizeMixIn, Program, Constraint

__author__ = 'jdr'


class Feasible:

  def objective(self):
    return 0.0


class Unconstrained:

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

  @classmethod
  def new_program(cls, program):
    prog = cls()
    prog.program = program
    return prog

  def cr_objective(self):
    return self.program.objective.value

  def cr_solve(self, quiet=True, **kwargs):
    """
    @rtype: float
    """
    self.program.solve(quiet, **kwargs)

  def cr_print(self):
    self.program.show()

  def add_constraint(self, constraint):
    self.program.constraints.append(constraint.constraint())

class CVXPySolver(OptimizeMixIn):

  def cr_constraint(self, type, a , b):
    return CVXPyConstraint(type, a, b)

  def cr_value(self, var):
    return var.value

  def cr_program(self, goal, cost, constraints):
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
