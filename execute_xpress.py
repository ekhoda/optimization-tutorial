#!/usr/bin/env python

import logging
from time import time

import xpress as xp

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

model = xp.problem(name='prod_planning')

start = time()

# ================== Decision variables ==================
production_variables = xp.vars(input_df_dict['input_data'].index, name='X', vartype=xp.continuous)
inventory_variables = xp.vars(input_df_dict['input_data'].index, name='I', vartype=xp.continuous)

# Alternative way of creating the variables
# production_variables = {i: xp.var(name=f'X{i}', vartype=xp.continuous)
#                         for i in input_df_dict['input_data'].index}
# inventory_variables = {i: xp.var(name=f'I{i}', vartype=xp.continuous)
#                        for i in input_df_dict['input_data'].index}
model.addVariable(production_variables, inventory_variables)

logger.debug(f'var declaration time: {time() - start:.6f}')

# ================== Inventory balance constraints ==================
model.addConstraint(
    xp.constraint(
        body=inventory_variables[period - 1] + production_variables[period] - inventory_variables[period],
        sense=xp.eq,
        name='inv_balance' + str(period),
        rhs=value.demand)
    for period, value in input_df_dict['input_data'].iloc[1:].iterrows())

# inv balance for first period
model.addConstraint(
    xp.constraint(
        body=production_variables[0] - inventory_variables[0],
        sense=xp.eq,
        name='inv_balance0',
        rhs=input_df_dict['input_data'].iloc[0].demand - input_param_dict['initial_inventory']))

# ================== Production capacity constraints ==================
model.addConstraint(
    xp.constraint(
        body=value,
        sense=xp.leq,
        name='prod_cap_month_' + str(index),
        rhs=input_df_dict['input_data'].iloc[index].production_capacity)
    for index, value in production_variables.items())

"""
# Following is an alternative way of defining the above 3 constraints.
# Check for yourself the difference between the two.

# ================== Inventory balance constraints ==================
# Version 2  # no name because no easy way without use of xp.constraint
model.addConstraint(
    (inventory_variables[period - 1] + production_variables[period]
     - inventory_variables[period] == value.demand)
    for period, value in input_df_dict['input_data'].iloc[1:].iterrows())

# inv balance for first period
model.addConstraint(
    production_variables[0] - inventory_variables[0]
    == input_df_dict['input_data'].iloc[0].demand - input_param_dict['initial_inventory'])

# ================== Production capacity constraints ==================
model.addConstraint(
    (value <= input_df_dict['input_data'].iloc[index].production_capacity)
    for index, value in production_variables.items())
"""

# ================== Costs and objective function ==================
total_holding_cost = input_param_dict['holding_cost'] * xp.Sum(inventory_variables)
total_production_cost = xp.Sum(row['production_cost'] * production_variables[index]
                               for index, row in input_df_dict['input_data'].iterrows())

objective = total_holding_cost + total_production_cost

model.setObjective(objective, sense=xp.minimize)
logger.info(f'Model creation time in sec: {time() - start:.4f}')

# ================== Optimization ==================
if model_params['write_lp']:
    logger.info('Writing the lp file!')
    model.write(model.name(), 'lp')

logger.info('Optimization starts!')
model.solve()

logger.info(f'status code: {model.getProbStatus()} --> {model.getProbStatusString()}')
# for LP: 1: optimal, 2: infeasible, 5: unbounded. for MIP: 5: infeasible, 6: optimal, 7: unbounded
if model.getProbStatus() == 1:
    logger.info(f'The solution is optimal and the objective value is ${model.getObjVal():,.2f}!')

# ================== Output ==================
dict_of_variables = {'production_variables': production_variables,
                     'inventory_variables': inventory_variables}

output_df = process_data.write_outputs_xpress(dict_of_variables, model)
helper.write_to_csv(output_df)
logger.info('Outputs are written to csv!')
