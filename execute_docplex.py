#!/usr/bin/env python

import logging
from time import time

import docplex.mp.model as cpx

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

model = cpx.Model('prod_planning')

start = time()

# ================== Decision variables ==================
production_variables = model.continuous_var_dict(input_df_dict['input_data'].index, name="X")
inventory_variables = model.continuous_var_dict(input_df_dict['input_data'].index, name="I")

# Alternative way of creating the variables
# production_variables = {index: model.continuous_var(name='X_' + str(row['period']))
#                         for index, row in input_df_dict['input_data'].iterrows()}
#
# inventory_variables = {index: model.continuous_var(name='I_' + str(row['period']))
#                        for index, row in input_df_dict['input_data'].iterrows()}

logger.debug("var declaration time: {:.6f}".format(time() - start))

# ================== Inventory balance constraints ==================
inv_balance_constraints = model.add_constraints(
    (inventory_variables[period - 1] + production_variables[period]
     - inventory_variables[period] == value.demand,
     'inv_balance' + str(period))
    for period, value in input_df_dict['input_data'].iloc[1:].iterrows())

# inv balance for first period
first_period_inv_balance_constraints = model.add_constraint(
    ct=production_variables[0] - inventory_variables[0]
       == input_df_dict['input_data'].iloc[0].demand - input_param_dict['initial_inventory'],
    ctname='inv_balance0')

# ================== Production capacity constraints ==================
production_capacity_constraints = model.add_constraints(
    (value <= input_df_dict['input_data'].iloc[index].production_capacity,
     'prod_cap_month_' + str(index))
    for index, value in production_variables.items())

"""
Following is an alternative way of defining 2 of the above 3 constraints.
Check for yourself the difference between the two.

# ================== Inventory balance constraints ==================
# Version 2
inv_balance_constraints = {
    period: model.add_constraint(
        ct=inventory_variables[period - 1] + production_variables[period]
           - inventory_variables[period] == value.demand,
        ctname='inv_balance' + str(period))
    for period, value in input_df_dict['input_data'].iloc[1:].iterrows()}

# inv balance for first period
first_period_inv_balance_constraints = model.add_constraint(
    ct=production_variables[0] - inventory_variables[0]
       == input_df_dict['input_data'].iloc[0].demand - input_param_dict['initial_inventory'],
    ctname='inv_balance0')

# ================== Production capacity constraints ==================
production_capacity_constraints = {
    index: model.add_constraint(
        ct=value <= input_df_dict['input_data'].iloc[index].production_capacity,
        ctname='prod_cap_month_' + str(index))
    for index, value in production_variables.items()}"""

# ================== Costs and objective function ==================
total_holding_cost = input_param_dict['holding_cost'] * model.sum(inventory_variables)
total_production_cost = model.sum(row['production_cost'] * production_variables[index]
                                  for index, row in input_df_dict['input_data'].iterrows())

objective = total_holding_cost + total_production_cost

model.minimize(objective)
logger.info('Model creation time in sec: {:.4f}'.format(time() - start))

# ================== Optimization ==================
if model_params['write_lp']:
    logger.info('Writing the lp file!')
    model.export_as_lp('./{}.lp'.format(model.name))

logger.info('Optimization starts!')

# If CPLEX is installed locally, we can use that to solve the problem.
# Otherwise, we can use DOcplexcloud. For docloud solve, we need valid 'url' and 'key'.
# Note, that if 'url' and 'key' parameters are present,
# the solve will be started on DOcplexcloud even if CPLEX is available.
# I've provided more info on this in optimization_model_docplex.py

# For now, a simple way to handle local or docloud solve
if model_params['cplex_cloud']:
    model.solve(url=model_params['url'], key=model_params['api_key'])
else:
    model.solve()

if model.solve_details.status == 'optimal':
    logger.info('The solution is optimal and the objective value '
                'is ${:,.2f}!'.format(model.objective_value))

# ================== Output ==================
dict_of_variables = {'production_variables': production_variables,
                     'inventory_variables': inventory_variables}

output_df = process_data.write_outputs(dict_of_variables, attr='solution_value')
helper.write_to_csv(output_df)
logger.info('Outputs are written to csv!')
