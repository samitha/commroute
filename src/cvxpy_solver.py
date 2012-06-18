from cvxpy import eq, program, variable, minimize, geq, leq
from cr_optimize import OptimizeMixIn, Program

__author__ = 'jdr'


class Feasible:

  def objective(self):
    return 0.0


class Unconstrained:

  def constraints(self):
    return []


class CVXPYProgram(Program):

  @classmethod
  def new_program(cls, program):
    prog = cls()
    prog.program = program
    return prog

  def cr_objective(self):
    return self.program.objective.value

  def cr_solve(self, **kwargs):
    self.program.solve(**kwargs)

  def cr_print(self):
    self.program.show()

  def add_constraint(self, constraint):
    self.program.constraints.append(constraint)

class CVXPySolver(OptimizeMixIn):

  def cr_eq(self,a,b):
    return eq(a,b)

  def cr_leq(self,a,b):
    return leq(a,b)

  def cr_geq(self,a,b):
    return geq(a,b)

  def cr_value(self, var):
    return var.value

  def cr_program(self, goal, cost, constraints):
    if goal == self.Goal.MIN:
      wrap = minimize
    else:
      wrap = maximize
    return CVXPYProgram.new_program(program(wrap(cost), constraints))

  def cr_var(self, name):
    return variable(name=name)


class SimpleOptimizeMixIn(Feasible, Unconstrained, CVXPySolver):
  pass
