from collections import defaultdict
from cvxpy_solver import SimpleOptimizeMixIn
from commroute.demand import FlowNetwork

__author__ = 'jdr'
from demand import Demand


class DynamicDemand(Demand):

  def __init__(self, t, *args, **kwargs):
    super(DynamicDemand, self).__init__(*args, **kwargs)
    self.t = t

  def jsonify(self):
    json = super(DynamicDemand, self).jsonify()
    json['t'] = self.t
    return json


class SourceDemand(DynamicDemand):

  def __init__(self, source, *args, **kwargs):
    super(SourceDemand, self).__init__(*args, **kwargs)

  @classmethod
  def tag(cls):
    return 'dynamic source'

  @classmethod
  def load_demand(cls, data, net):
    return cls(
      flow=data['flow'],
      t = data['t'],
      source = net.link_by_name(data['source'])
    )

  def jsonify(self):
    json = super(DynamicDemand, self).jsonify()
    json['source'] = self.source.name
    return json


class DynamicLagrangianProblem(FlowNetwork, SimpleOptimizeMixIn):

  def __init__(self, *args, **kwargs):
    super(DynamicLagrangianProblem, self).__init__(*args, **kwargs)
    self.source_demands = defaultdict(list)

  def add_source_demand(self, demand):
    source_list = self.source_demands[demand.source]
    n_sl = len(source_list)
    if demand.t > n_sl:
      source_list.extend([source_list[-1]*(demand.t - n_sl)])
    source_list.insert(demand.t, demand.flow)

  def variablize(self):
    pass


