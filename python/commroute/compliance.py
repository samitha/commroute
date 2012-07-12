from demand import ODDemand
from demand import FlowNetwork

__author__ = 'jdr'

from demand import RouteDemand

class ComplianceException(Exception):
  pass

def valid_compliance(comp):
  return 0.0 <= comp <= 1.0

class CompliantRouteDemand(RouteDemand):

  def __init__(self, route, flow, compliance):
    super(CompliantRouteDemand, self).__init__(route, flow)
    if not valid_compliance(compliance):
      raise ComplianceException('not valid')
    self.compliance = compliance

  def jsonify(self):
    json = super(CompliantRouteDemand, self).jsonify()
    json['compliance'] = self.compliance
    return json

  @classmethod
  def load_demand(cls, data, net):
    return cls(
      route=net.route_by_names(data['route']),
      flow = data['flow'],
      compliance = data['compliance']
    )

  def non_compliant_flow(self):
    return self.flow - self.compliant_flow()

  def compliant_flow(self):
    return self.flow * self.compliance

  def baseline_demands(self):
    return [RouteDemand(self.route, flow=self.flow)]

  def compliance_demands(self):
    return [
      RouteDemand(self.route, flow=self.non_compliant_flow()),
      ODDemand(
        source=self.route.source(),
        sink=self.route.sink(),
        flow=self.compliant_flow()
      )
    ]

  @classmethod
  def tag(cls):
    return 'compliant route'

CompliantRouteDemand.add_type(CompliantRouteDemand)

class ComplianceMixin(FlowNetwork):

  def add_compliant_demand(self, route, flow, compliance):
    self.demands.append(CompliantRouteDemand(route, flow, compliance))

  def compliant_demands(self):
    return [demand for demand in self.demands if isinstance(demand, CompliantRouteDemand)]

  def get_demands(self):
    if self.compliance_mode():
      return self.demands_with_compliance()
    else:
      return self.demands_without_compliance()

  def compliance_mode(self):
    try:
      return self.COMPLIANCE
    except AttributeError:
      self.COMPLIANCE = False
      return self.COMPLIANCE

  def set_compliance(self, on = True):
    self.COMPLIANCE = on

  def demands_with_compliance(self):
    comp_demands = self.compliant_demands()
    basic_demands = set(self.demands).difference(comp_demands)
    extra_demands = []
    for dem in comp_demands:
      extra_demands.extend(dem.compliance_demands())
    return list(basic_demands) + extra_demands

  def demands_without_compliance(self):
    comp_demands = self.compliant_demands()
    basic_demands = set(self.demands).difference(comp_demands)
    extra_demands = []
    for dem in comp_demands:
      extra_demands.extend(dem.baseline_demands())
    return list(basic_demands) + extra_demands