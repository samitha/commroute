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

  @classmethod
  def tag(cls):
    return 'compliant route'
