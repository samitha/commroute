import json
import math
import pylab
from commroute.data_fixer import DataFixer
from commroute.static_ctm import CTMStaticProblem


class Record(object):
    """docstring for Record"""
    def __init__(self, hour, lid, vel_mean, vel_stdev, dens_mean, dens_stdev, nid):
        super(Record, self).__init__()
        self.nid = nid
        self.lid = lid
        self.vel_mean = vel_mean
        self.vel_stdev = vel_stdev
        self.dens_mean = dens_mean
        self.dens_stdev = dens_stdev
        self.hour = hour
        
    @classmethod
    def from_line(cls, line):
        """docstring for from_line"""
        line = line[:-1].split('\t')
        nid = int(line[0])
        lid = int(line[1])
        vm = float(line[2])
        vs = float(line[3])
        dm = float(line[4])
        ds = float(line[5])
        hour = int(line[6])
        return cls(
            nid, lid, vm, vs, dm, ds, hour
        )
        

records = []
for line in open('data/highway_data.csv','r'):
    try:
        records.append(Record.from_line(line))
    except Exception as e:
        pass

def stdev(lst):
    m = mean(lst)
    val = float(1)/(len(lst) - 1) * sum((x - m)**2 for x in lst)
    return math.sqrt(val)

def mean(lst):
    return 1/float(len(lst))*sum(lst)
        
        
nids = set(rec.nid for rec in records)
lids = set(rec.lid for rec in records)
hours = set(rec.hour for rec in records)

#for hour in hours:
#    stdevs = []
#    for lid in lids:
#        stdevs.append(stdev([rec.dens_mean for rec in records if rec.lid == lid and rec.hour == hour] ))
#    pylab.hist(stdevs, bins = 100)
#    pylab.title(str(hour))
#    pylab.show()

def check_out_stats():

    for hour in [15,16,17]:
        pylab.hist(
            [
            mean(
                [
                rec.vel_mean
                for rec in records
                if rec.lid == lid and rec.hour == hour
                ]
            )
            for lid in lids
            ],
             bins=100
        )
        pylab.title(hour)
        pylab.show()

    for hour in [15,16,17]:
        pylab.hist(
            [
            mean(
                [
                rec.dens_mean
                for rec in records
                if rec.lid == lid and rec.hour == hour
                ]
            )
            for lid in lids
            ],
             bins=100
        )
        pylab.title(hour)
        pylab.show()

def dump_avg(hour):
    with open('data/asdf{0}'.format(hour), 'w') as fn:
        json.dump(
            dict(
                (
                    lid,
                    dict(
                        flow=mean(
                            [
                            rec.dens_mean * rec.vel_mean
                            for rec in records
                            if rec.lid == lid
                            and rec.hour == hour
                            ]
                        ),
                        density=mean(
                            [
                            rec.dens_mean
                            for rec in records
                            if rec.lid == lid
                            and rec.hour == hour
                            ]
                        )
                    )
                )
                for lid in lids
            ),
            fn,
            indent=True
        )

def plots():
    with open('data/asdf16','r') as fn:
        data = json.load(fn)
    pylab.hist(
        [
        lid['flow']
        for lid in data.itervalues()
        ],
         bins=100
    )
    pylab.figure()
    pylab.hist(
        [
        lid['density']
        for lid in data.itervalues()
        ],
         bins=100
    )
    pylab.show()

def combine_data():
    with open('data/asdf16','r') as fn:
        data = json.load(fn)
    net = CTMStaticProblem.load('data/jdr_peninsula_fixed.json')
    lids_data = set(map(int,data.keys()))
    lids_net = set([int(link.name) for link in net.get_links()])
    print len(lids_data.intersection(lids_net))
    for lid, rec in data.iteritems():
        link = net.link_by_name(lid)
        link.state.flow = rec['flow']
        link.state.density = rec['density']
    net.dump('data/jdr_with_state.json')


def checker():
    net = CTMStaticProblem.load("data/jdr_with_state.json")
    for link in net.get_links():
        print link.state

def fixer():
    net = DataFixer.load('data/jdr_with_state.json')
    net.solve_with_state()
    net.dump('data/data_fixed_again.json')

def source_sink_checker():
    net = DataFixer.load('data/jdr_with_state.json')
    net.cache_props()
    print 'sources'
    for source in net.sources:
        print source.state.flow
    print 'sinks'
    for sink in net.sinks:
        print sink.state.flow


def difference_stuff():
    prev = CTMStaticProblem.load("data/jdr_with_state.json")
    final = CTMStaticProblem.load("data/data_fixed.json")
    pylab.figure()
    pylab.hist(
        [
            abs(p.state.flow - f.state.flow) / (p.state.flow)
            for p,f in
            [
                (prev.link_by_name(lid),final.link_by_name(lid))
                for lid in set(
                [
                    link.name for link in prev.get_links()
                ]
            )
            ]
        ],
        bins=20,
        log=True
    )
    pylab.title("Relative change in link flow input")
    pylab.xlabel("Relative change (-)")
    pylab.ylabel("Count (-)")
    pylab.savefig('figures/data_fixer_difference.pdf')

def n_routes():
    net = CTMStaticProblem.load("data/data_fixed.json")
    net.cache_props()
    pylab.figure()
    pylab.hist(
        [
            len(routes)
            for routes in net.od_routes.itervalues()
        ],
        bins=7,
        align='mid',
        range=(-.5, 6.5)
    )
    pylab.title("Number of available routes between o-d pairs")
    pylab.xlabel("# routes (-)")
    pylab.ylabel("Count (-)")
    pylab.savefig("figures/available_routes.pdf")

def nash_comparison():
    net = CTMStaticProblem.load("data/data_fixed.json")
    net.cache_props()
    for routes in net.od_routes.itervalues():
        if len(routes) > 1:
            print ''
            tts = sorted(
                net.route_travel_time(route)
                for route in routes
            )
            print tts[1] - tts[0], tts[:2]


def congestion_level():
    net = CTMStaticProblem.load('data/data_fixed_again.json')
    net.cache_props()
    pylab.figure()
    pylab.hist(
        [
            link.congestion_level()
            for link in net.get_links()
        ],
        bins=50,
        range=(0,1)
    )
    pylab.show()

def figure_out_units():
    # density cars / meter
    # speed meters / second
    # flow cars / second
    # length meters
    pass

# combine_data()
# checker()
# fixer()
# difference_stuff()
# n_routes()
# nash_comparison()
congestion_level()