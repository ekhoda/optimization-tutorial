import logging

import xpress as xp

from helper import write_to_csv
from parameters import model_params
from process_data import write_outputs_xpress

__author__ = 'Ehsan Khodabandeh'
__version__ = '1.0'
# ====================================

logger = logging.getLogger(__name__ + ': ')


class OptimizationModel:
    def __init__(self, input_data, input_params):
        self.input_data = input_data
        self.input_params = input_params
        self.model = xp.problem('prod_planning')
        self._create_decision_variables()
        self._create_main_constraints()
        self._set_objective_function()

    # ================== Decision variables ==================
    def _create_decision_variables(self):
        self.production_variables = xp.vars(self.input_data.index, name='X', vartype=xp.continuous)
        self.inventory_variables = xp.vars(self.input_data.index, name='I', vartype=xp.continuous)

        # Alternative way of creating the variables
        # self.production_variables = {index: xp.var(name=f'X{row["period"]}', vartype=xp.continuous)
        #                              for index, row in self.input_data.iterrows()}
        # self.inventory_variables = {index: xp.var(name=f'I{row["period"]}', vartype=xp.continuous)
        #                             for index, row in self.input_data.iterrows()}
        self.model.addVariable(self.production_variables, self.inventory_variables)

    # ================== Constraints ==================
    def _create_main_constraints(self):
        # Depending on what you need, you may want to consider creating any of
        # the expressions (constraints or objective terms) as an attribute of
        # the OptimizationModel class (e.g. self.inv_balance_constraints).
        # That way if, for example, at the end of the optimization you need to check
        # the slack variables of certain constraints, you know they already exists in your model

        # ================== Inventory balance constraints ==================
        self.inv_balance_constraints = self.model.addConstraint(
            xp.constraint(
                body=self.inventory_variables[period - 1] + self.production_variables[period] -
                     self.inventory_variables[period],
                sense=xp.eq,
                name='inv_balance' + str(period),
                rhs=value.demand)
            for period, value in self.input_data.iloc[1:].iterrows())

        # inv balance for first period
        self.first_period_inv_balance_constraints = self.model.addConstraint(
            xp.constraint(
                body=self.production_variables[0] - self.inventory_variables[0],
                sense=xp.eq,
                name='inv_balance0',
                rhs=self.input_data.iloc[0].demand - self.input_params['initial_inventory']))

        # ================== Production capacity constraints ==================
        self.production_capacity_constraints = self.model.addConstraint(
            xp.constraint(
                body=value,
                sense=xp.leq,
                name='prod_cap_month_' + str(index),
                rhs=self.input_data.iloc[index].production_capacity)
            for index, value in self.production_variables.items())

    # ================== Costs and objective function ==================
    def _set_objective_function(self):
        # Similar to constraints, saving the costs expressions as attributes
        # can give you the chance to retrieve their values at the end of the optimization
        self.total_holding_cost = self.input_params['holding_cost'] * xp.Sum(self.inventory_variables)
        self.total_production_cost = xp.Sum(row['production_cost'] * self.production_variables[index]
                                            for index, row in self.input_data.iterrows())

        objective = self.total_holding_cost + self.total_production_cost
        self.model.setObjective(objective, sense=xp.minimize)

    # ================== Optimization ==================
    def optimize(self):
        """
        XPRESS has a community license that comes with your python installation.
        You can use it for solving very small examples, like the one we have here.
        """
        if model_params['write_lp']:
            logger.info('Writing the lp file!')
            self.model.write(self.model.name(), 'lp')

        # In xpress, parameters to control the model are added by setControl(ctrl, value)
        # or setControl ({ctrl1: value1, ctrl2: value2, ..., ctrlk: valuek}).
        logger.info('Optimization starts!')
        if model_params['mip_gap']:
            self.model.setControl('miprelstop', model_params['mip_gap'])
        if model_params['time_limit']:  # maxtime should be an integer
            self.model.setControl('maxtime', model_params['time_limit'])
        if model_params['display_log']:  # {0: no message, 1: all, 3: error and warning, 4: error only}
            self.model.setControl('outputlog', 0)

        self.model.solve()
        # xpress's status (currently on version 8.11) is not as user-friendly as other packages.
        # The status is different depending on the problem type.
        # For LP: {1: optimal, 2: infeasible, 5: unbounded}
        # For MIP: {5: infeasible, 6: optimal, 7: unbounded}
        if self.model.getProbStatus() == 1:  # because this is an LP problem
            logger.info(f'The solution is optimal and the objective value is ${self.model.getObjVal():,.2f}!')

    # ================== Output ==================
    def create_output(self):
        dict_of_variables = {'production_variables': self.production_variables,
                             'inventory_variables': self.inventory_variables}

        output_df = write_outputs_xpress(dict_of_variables, self.model)
        write_to_csv(output_df)
