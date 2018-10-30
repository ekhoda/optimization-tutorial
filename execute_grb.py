#!/usr/bin/env python

import logging
from time import time

import gurobipy as grb

import helper
import process_data
from parameters import model_params

__author__ = 'Ehsan Khodabandeh'
__version__ = '1.0'
# ====================================

LOG_FORMAT = '%(asctime)s  %(name)-12s %(levelname)s : %(message)s'
logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
# Since the level here is INFO, all the logger.debug below are not displayed
logger = logging.getLogger(__name__ + ': ')

# ================== Set up data ==================
input_df_dict, input_param_dict = process_data.load_data()
logger.info('Data is loaded!')

# ================== Set up the optimization model ==================
"""
Parameters:
h: unit holding cost
p: production capacity per month
I_0: initial_inventory
c_t: unit production cost in month t
d_t: demand of month t

Variables:
X_t: Amount produced in month t
I_t: Inventory at the end of period t

Constraints:
Inventory Constraints: I_{t-1} + X_t - d_t = I_t
Capacity Constraints: X_t <= p

Objective: Min Sum(h*I_t + c_t*X_t)
"""

model = grb.Model('prod_planning')

start = time()

# ================== Decision variables ==================
production_variables = model.addVars(input_df_dict['input_data'].index, vtype=grb.GRB.CONTINUOUS, name="X")
inventory_variables = model.addVars(input_df_dict['input_data'].index, vtype=grb.GRB.CONTINUOUS, name="I")

# Alternative way of creating the variables
# production_variables = {index: model.addVar(name='X_' + str(row['period']),
#                                             vtype=grb.GRB.CONTINUOUS)
#                         for index, row in input_df_dict['input_data'].iterrows()}
#
# inventory_variables = {index: model.addVar(name='I_' + str(row['period']),
#                                            vtype=grb.GRB.CONTINUOUS)
#                        for index, row in input_df_dict['input_data'].iterrows()}

logger.debug("var declaration time: {:.6f}".format(time() - start))

# ================== Inventory balance constraints ==================
inv_balance_constraints = {
    period: model.addConstr(
        lhs=inventory_variables[period - 1] + production_variables[period] - inventory_variables[period],
        sense=grb.GRB.EQUAL,
        name='inv_balance' + str(period),
        rhs=value.demand)
    for period, value in input_df_dict['input_data'].iloc[1:].iterrows()}

# inv balance for first period
first_period_inv_balance_constraints = model.addConstr(
    lhs=production_variables[0] - inventory_variables[0],
    sense=grb.GRB.EQUAL,
    name='inv_balance0',
    rhs=input_df_dict['input_data'].iloc[0].demand - input_param_dict['initial_inventory'])

# ================== Production capacity constraints ==================
production_capacity_constraints = {
    index: model.addConstr(
        lhs=value,
        sense=grb.GRB.LESS_EQUAL,
        name='prod_cap_month_' + str(index),
        rhs=input_df_dict['input_data'].iloc[index].production_capacity)
    for index, value in production_variables.items()}

# ================== Costs and objective function ==================
total_holding_cost = input_param_dict['holding_cost'] * grb.quicksum(inventory_variables.values())

total_production_cost = grb.quicksum(row['production_cost'] * production_variables[index]
                                     for index, row in input_df_dict['input_data'].iterrows())

objective = total_holding_cost + total_production_cost

model.setObjective(objective, grb.GRB.MINIMIZE)
logger.info('Model creation time in sec: {:.4f}'.format(time() - start))

# ================== Optimization ==================
if model_params['write_lp']:
    logger.info('Writing the lp file!')
    model.write(model.ModelName + '.lp')

if not model_params['write_log']:
    model.setParam('OutputFlag', 0)

logger.info('Optimization starts!')
model.optimize()

if model.Status == grb.GRB.OPTIMAL:
    logger.info('The solution is optimal and the objective value '
                'is ${:,.2f}!'.format(model.objVal))

# ================== Output ==================
dict_of_variables = {'production_variables': production_variables,
                     'inventory_variables': inventory_variables}

output_df = process_data.write_outputs(dict_of_variables, attr='x')
helper.write_to_csv(output_df)
logger.info('Outputs are written to csv!')
