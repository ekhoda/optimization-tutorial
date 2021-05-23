import logging

import gurobipy as grb

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
        self.model = grb.Model('prod_planning')
        self._create_decision_variables()
        self._create_main_constraints()
        self._set_objective_function()

    # ================== Decision variables ==================
    def _create_decision_variables(self):
        self.production_variables = self.model.addVars(self.input_data.index, vtype=grb.GRB.CONTINUOUS, name="X")
        self.inventory_variables = self.model.addVars(self.input_data.index, vtype=grb.GRB.CONTINUOUS, name="I")

        # Alternative way of creating the variables
        # self.production_variables = {index: self.model.addVar(name='X_' + str(row['period']),
        #                                                       vtype=grb.GRB.CONTINUOUS)
        #                              for index, row in self.input_data.iterrows()}
        #
        # self.inventory_variables = {index: self.model.addVar(name='I_' + str(row['period']),
        #                                                      vtype=grb.GRB.CONTINUOUS)
        #                             for index, row in self.input_data.iterrows()}

    # ================== Constraints ==================
    def _create_main_constraints(self):
        # Depending on what you need, you may want to consider creating any of
        # the expressions (constraints or objective terms) as an attribute of
        # the OptimizationModel class (e.g. self.inv_balance_constraints).
        # That way if, for example, at the end of the optimization you need to check
        # the slack variables of certain constraints, you know they already exists in your model

        # ================== Inventory balance constraints ==================
        self.inv_balance_constraints = {
            period: self.model.addConstr(
                lhs=self.inventory_variables[period - 1] + self.production_variables[period]
                    - self.inventory_variables[period],
                sense=grb.GRB.EQUAL,
                name='inv_balance' + str(period),
                rhs=value.demand)
            for period, value in self.input_data.iloc[1:].iterrows()}

        # inv balance for first period
        self.first_period_inv_balance_constraints = self.model.addConstr(
            lhs=self.production_variables[0] - self.inventory_variables[0],
            sense=grb.GRB.EQUAL,
            name='inv_balance0',
            rhs=self.input_data.iloc[0].demand - self.input_params['initial_inventory'])

        # ================== Production capacity constraints ==================
        self.production_capacity_constraints = {
            index: self.model.addConstr(
                lhs=value,
                sense=grb.GRB.LESS_EQUAL,
                name='prod_cap_month_' + str(index),
                rhs=self.input_data.iloc[index].production_capacity)
            for index, value in self.production_variables.items()}

    # ================== Costs and objective function ==================
    def _set_objective_function(self):
        # Similar to constraints, saving the costs expressions as attributes
        # can give you the chance to retrieve their values at the end of the optimization
        self.total_holding_cost = self.input_params['holding_cost'] * grb.quicksum(self.inventory_variables.values())

        self.total_production_cost = grb.quicksum(row['production_cost'] * self.production_variables[index]
                                                  for index, row in self.input_data.iterrows())

        objective = self.total_holding_cost + self.total_production_cost
        self.model.setObjective(objective, grb.GRB.MINIMIZE)

    # ================== Optimization ==================
    def optimize(self):
        if model_params['write_lp']:
            logger.info('Writing the lp file!')
            self.model.write(self.model.ModelName + '.lp')

        if not model_params['write_log']:
            self.model.setParam('OutputFlag', 0)

        if not model_params['display_log']:  # to enable or disable console logging
            self.model.setParam('LogToConsole', 0)

        logger.info('Optimization starts!')
        if model_params['mip_gap']:
            self.model.setParam(grb.GRB.Param.MIPGap, model_params['mip_gap'])
        if model_params['time_limit']:
            self.model.setParam(grb.GRB.Param.TimeLimit, model_params['time_limit'])

        self.model.optimize()
        if self.model.Status == grb.GRB.OPTIMAL:
            logger.info('The solution is optimal and the objective value '
                        'is ${:,.2f}!'.format(self.model.objVal))

    # ================== Output ==================
    def create_output(self):
        dict_of_variables = {'production_variables': self.production_variables,
                             'inventory_variables': self.inventory_variables}

        output_df = write_outputs(dict_of_variables, attr='x')
        write_to_csv(output_df)
