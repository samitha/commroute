from complacency import MinTTTComplacencyProblem
from ctm import CTMLink
from static_ctm import MinTTTLagrangianCTMProblem

__author__ = 'jdr'

class StateConstrainedLink(CTMLink):

  class CongState:
    FF = 0
    CONG = 1
    ANY = 2
    BOUND = 3

  def __init__(self, cong_state=None, *args, **kwargs):
    if cong_state is None:
      cong_state = self.CongState.ANY
    super(StateConstrainedLink, self).__init__(*args, **kwargs)
    self.cong_state = cong_state


  def cong_state(self):
    return self.cong_state

  def set_ff(self):
    self.cong_state = self.CongState.FF

  def set_cong(self):
    self.cong_state = self.CongState.CONG

  def set_any(self):
    self.cong_state = self.CongState.ANY
    
  def set_bound(self, lower, upper):
    self.cong_state = self.CongState.BOUND
    self.cong_bounds = dict(
      upper=upper,
      lower=lower
    )

  def init_state(self):
    self.set_cong_state(self.CongState.ANY)

  def set_cong_state(self, state):
    self.cong_state = state

  def ctm_constraints(self, solver):
    """
    gives the constraint taking into account the state
    of the link
    @param solver:
    @type solver: cvxpy_solver.CVXPySolver
    @rtype: cvxpy_solver.CVXPyConstraint
    """
    if self.cong_state is self.CongState.FF:
      return [solver.cr_leq(self.v_dens, self.fd.rho_crit())]
    if self.cong_state is self.CongState.CONG:
      return [solver.cr_geq(self.v_dens, self.fd.rho_crit())]
    if self.cong_state is self.CongState.BOUND:
      return [solver.cr_geq(self.v_dens, self.cong_bounds['lower']), solver.cr_leq(self.v_dens, self.cong_bounds['upper'])]
    if self.cong_state is self.CongState.ANY:
      return []

  def jsonify(self):
    json = super(StateConstrainedLink, self).jsonify()
    json['cong_state'] = self.cong_state
    if self.cong_state is self.CongState.BOUND:
      json['cong_bounds'] = self.cong_bounds
    return json

  @classmethod
  def additional_kwargs(cls, data):
    kwargs = super(StateConstrainedLink, cls).additional_kwargs(data)
    kwargs['cong_state'] = data.get('cong_state', cls.CongState.ANY)
    kwargs['cong_bounds'] = data.get('cong_bounds', None)
    return kwargs

class StateConstrainedNetwork(MinTTTLagrangianCTMProblem):
  link_class = StateConstrainedLink

  def state_constrained_constraints(self):
    constraints = []
    for link in self.get_links():
      constraints+=link.ctm_constraints(self)
    return constraints

  def constraints(self):
    constraints = super(StateConstrainedNetwork, self).constraints()
    return constraints + self.state_constrained_constraints()

class StateConstrainedComplacentNetwork(StateConstrainedNetwork, MinTTTComplacencyProblem):
  pass