import logging

import docplex.mp.model as cpx
from docplex.mp.context import Context

from helper import write_to_csv
from parameters import model_params
from process_data import write_outputs

__author__ = 'Ehsan Khodabandeh'
__version__ = '1.0'
# ====================================

logger = logging.getLogger(__name__ + ': ')


class OptimizationModel(object):
    def __init__(self, input_data, input_params):
        self.input_data = input_data
        self.input_params = input_params
        self.model = cpx.Model('prod_planning')
        self._create_decision_variables()
        self._create_main_constraints()
        self._set_objective_function()

    # ================== Decision variables ==================
    def _create_decision_variables(self):
        self.production_variables = self.model.continuous_var_dict(self.input_data.index, name="X")
        self.inventory_variables = self.model.continuous_var_dict(self.input_data.index, name="I")

        # Alternative way of creating the variables
        # self.production_variables = {index: self.model.continuous_var(name='X_' + str(row['period']))
        #                              for index, row in self.input_data.iterrows()}
        #
        # self.inventory_variables = {index: self.model.continuous_var(name='I_' + str(row['period']))
        #                             for index, row in self.input_data.iterrows()}

    # ================== Constraints ==================
    def _create_main_constraints(self):
        # Depending on what you need, you may want to consider creating any of
        # the expressions (constraints or objective terms) as an attribute of
        # the OptimizationModel class (e.g. self.inv_balance_constraints).
        # That way if, for example, at the end of the optimization you need to check
        # the slack variables of certain constraints, you know they already exists in your model

        # ================== Inventory balance constraints ==================
        self.inv_balance_constraints = self.model.add_constraints(
            (self.inventory_variables[period - 1] + self.production_variables[period]
             - self.inventory_variables[period] == value.demand,
             'inv_balance' + str(period))
            for period, value in self.input_data.iloc[1:].iterrows())

        # inv balance for first period
        self.first_period_inv_balance_constraints = self.model.add_constraint(
            ct=self.production_variables[0] - self.inventory_variables[0]
               == self.input_data.iloc[0].demand - self.input_params['initial_inventory'],
            ctname='inv_balance0')

        # ================== Production capacity constraints ==================
        self.production_capacity_constraints = self.model.add_constraints(
            (value <= self.input_data.iloc[index].production_capacity,
             'prod_cap_month_' + str(index))
            for index, value in self.production_variables.items())

    # ================== Costs and objective function ==================
    def _set_objective_function(self):
        # Similar to constraints, saving the costs expressions as attributes
        # can give you the chance to retrieve their values at the end of the optimization
        self.total_holding_cost = self.input_params['holding_cost'] * self.model.sum(self.inventory_variables)

        self.total_production_cost = self.model.sum(row['production_cost'] * self.production_variables[index]
                                                    for index, row in self.input_data.iterrows())

        objective = self.total_holding_cost + self.total_production_cost
        self.model.minimize(objective)

    # ================== Optimization ==================
    def optimize(self):
        """
        If CPLEX is installed locally, we can use that to solve the problem.
        Otherwise, we can use DOcplexcloud. For docloud solve, we need valid 'url' and 'key'.
        Note, that if 'url' and 'key' parameters are present,
        the solve will be started on DOcplexcloud even if CPLEX is available.
            e.g. this forces the solve on DOcplexcloud:
            model.solve(url='https://foo.com', key='bar')

        Using 'docplex.mp.context.Context', it is possible to control how to solve.
        """

        if model_params['write_lp']:
            logger.info('Writing the lp file!')
            self.model.export_as_lp('./{}.lp'.format(self.model.name))

        ctx = Context()
        ctx.solver.docloud.url = model_params['url']
        ctx.solver.docloud.key = model_params['api_key']
        agent = 'docloud' if model_params['cplex_cloud'] else 'local'

        # There are several ways to set the parameters. Here are two ways:
        # method 1:
        if model_params['mip_gap']:
            self.model.parameters.mip.tolerances.mipgap = model_params['mip_gap']
        if model_params['time_limit']:
            self.model.set_time_limit(model_params['time_limit'])

        # # method 2:
        # cplex_parameters = {'mip.tolerances.mipgap': model_params['mip_gap'],
        #                     'timelimit': model_params['time_limit']}
        # ctx.update(cplex_parameters, create_missing_nodes=True)

        logger.info('Optimization starts!')
        if model_params['write_log']:
            with open("cplex.log", "w") as outs:
                # prints CPLEX output to file "cplex.log"
                self.model.solve(context=ctx, agent=agent, log_output=outs)
        else:
            self.model.solve(context=ctx, agent=agent, log_output=model_params['display_log'])

        if self.model.solve_details.status == 'optimal':
            logger.info('The solution is optimal and the objective value '
                        'is ${:,.2f}!'.format(self.model.objective_value))

    # ================== Output ==================
    def create_output(self):
        dict_of_variables = {'production_variables': self.production_variables,
                             'inventory_variables': self.inventory_variables}

        output_df = write_outputs(dict_of_variables, attr='solution_value')
        write_to_csv(output_df)
