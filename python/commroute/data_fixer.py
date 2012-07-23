from cvxpy_solver import SimpleOptimizeMixIn
from static_ctm import CTMStaticProblem
from cr_network import Source, Sink
import cvxpy
from cr_utils.cr_utils import flatten

class DataFixer(CTMStaticProblem, SimpleOptimizeMixIn):

    def solve_with_data(self, fn):
        self.input_data = self.parse_input(fn)
        print 'input', self.input_data

        self.get_program().cr_print()
        self.get_program().cr_solve()

    def solve_with_state(self):
        self.objective = self.objective_state
        self.get_program().cr_print()
        self.get_program().cr_solve()
        self.realize()
        self.dump('data_fixed.json')


    def objective(self):
        return sum(
            cvxpy.abs(self.input_data[link.name]['flow'] - link.v_flow) +
            cvxpy.abs(self.input_data[link.name]['density'] - link.v_dens)
                for link in self.get_links() if self.input_data.has_key(link.name)
        )

    def objective_state(self):
        return sum(
            cvxpy.abs(link.state.flow - link.v_flow) +
            cvxpy.abs(link.state.flow - link.v_dens)
                for link in self.get_links()
        )

    def variablize(self):
        self.cache_props()
        for link in self.get_links():
            link.v_flow = self.create_var('flow {0}'.format(link.name), self.attr_realizer(link.state,'flow'))
            link.v_dens = self.create_var('dens {0}'.format(link.name), self.attr_realizer(link.state,'density'))

    def constraints(self):
        return self.con_mass_balance() + self.con_ctm()

    def con_mass_balance(self):
        return [
        self.cr_eq(sum(link.v_flow for link in junction.in_links),
                   sum(link.v_flow for link in junction.out_links))
        for junction in self.junctions if not isinstance(junction, Source ) and not isinstance(junction, Sink)
        ]

    def parse_input(self, fn):
        with open(fn,'r') as fn:
            flows = {}
            for row in fn:
                splits = row[:-1].split(';')
                name = splits[2].strip()
                flow = float(splits[1])
                density = float(splits[0])
                flows[name] = {
                    'flow': flow,
                    'density': density
                }
        return flows

    def con_ctm(self):
        return list(flatten([self.cr_geq(link.v_flow, 0),
                             self.cr_leq(link.v_flow, link.fd.q_max),
                             self.cr_leq(link.v_flow, link.fd.v * link.v_dens),
                             self.cr_leq(link.v_flow, link.fd.w * (link.fd.rho_max - link.v_dens)),
                             self.cr_geq(link.v_dens, 0),
                             self.cr_leq(link.v_dens, link.fd.rho_max),
                             ] for link in self.get_links()))