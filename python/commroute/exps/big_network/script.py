from commroute.static_ctm import CTMStaticProblem
import networkx
__author__ = 'jdr'


net = CTMStaticProblem.load("/Users/jdr/Documents/github/commroute/python/commroute/exps/big_network/jdr_peninsula_fixed.json")
net.cache_props()
for source in net.sources:
    print source
    print source.up_junc
print len(net.get_links())
for junction in net.junctions:
    if len(junction.in_links) == 0 and len(junction.out_links) > 1:
        print 'junction', junction
        for link in junction.out_links:
            pass#link.set_up_junc(None)