from ctm import DensityCTMLink
from static_ctm import MinTTTLagrangianCTMProblem

__author__ = 'jdr'

class StateConstrainedLink(DensityCTMLink):

  class State:
    FF = 0
    CONG = 1
    ANY = 2

  def __init__(self, state=None, *args, **kwargs):
    if state is None:
      state = self.State.ANY
    super(StateConstrainedLink, self).__init__(*args, **kwargs)
    self.state = state


  def state(self):
    return self.state

  def set_ff(self):
    self.state = self.State.FF

  def set_cong(self):
    self.state = self.State.CONG

  def set_any(self):
    self.state = self.State.ANY

  def init_state(self):
    self.set_state(self.State.ANY)

  def set_state(self, state):
    self.state = state

  def ctm_constraints(self, solver):
    """
    gives the constraint taking into account the state
    of the link
    @param solver:
    @type solver: cvxpy_solver.CVXPySolver
    @rtype: cvxpy_solver.CVXPyConstraint
    """
    if self.state is self.State.FF:
      return [solver.cr_eq(self.v_flow, self.fd.flow_ff(self.v_dens))]
    if self.state is self.State.CONG:
      return [solver.cr_eq(self.v_flow, self.fd.flow_cong(self.v_dens))]
    if self.state is self.State.ANY:
      return []

  def jsonify(self):
    json = super(StateConstrainedLink, self).jsonify()
    json['state'] = self.state
    return json

  @classmethod
  def additional_kwargs(cls, data):
    kwargs = super(StateConstrainedLink, cls).additional_kwargs(data)
    kwargs['state'] = data.get('state', cls.State.ANY)
    return kwargs

class StateConstrainedNetwork(MinTTTLagrangianCTMProblem):
  link_class = StateConstrainedLink

  def constraints(self):
    constraints = super(StateConstrainedNetwork, self).constraints()
    for link in self.get_links():
      constraints+=link.ctm_constraints(self)
    return constraints


if __name__ == '__main__':
  main()




