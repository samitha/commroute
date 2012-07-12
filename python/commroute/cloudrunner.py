from static_ctm import MinTTTLagrangianCTMProblem
from demand import RouteDemand, ODDemand
import cloud
cloud.setkey(1441)
cloud.files.put('../networks/exps/exp8/netd.json')
def runner():
  MinTTTLagrangianCTMProblem.load("netd.json", cloud = True).get_program().cr_solve()
cloud.call(runner, _env = 'science', _fast_serialization=2 )