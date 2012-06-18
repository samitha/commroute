from ctm import DensityCTMLink
from static_ctm import CTMConstrained

__author__ = 'jdr'



class StateConstrainedLink(DensityCTMLink):

  class State:
    FF = 0
    CONG = 1
    ANY = 2

  def state(self):
    return self.state

  def init_state(self):
    self.set_state(self.State.ANY)

  def set_state(self, state):
    self.state = state

  def ctm_constraint(self, solver):
    """
    gives the constraint taking into account the state
    of the link
    @param solver:
    @type solver: cvxpy_solver.CVXPySolver
    @rtype: cvxpy_solver.CVXPyConstraint
    """
    

