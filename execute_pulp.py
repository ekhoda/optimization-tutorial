#!/usr/bin/env python

import logging
from time import time

import pulp

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


# ====================================
# Pulp addConstraint function doesn't return the constraint object.
# So, to have a consistent object, we return it ourselves
def add_constr(model, constraint):
    model.addConstraint(constraint)
    return constraint


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

model = pulp.LpProblem(name='prod_planning', sense=pulp.LpMinimize)

start = time()
# Which of the following variable declarations is better? Well, it depends!
# Knowing different ways of coding the variables and constraints,
# you can evaluate their execution time and use them depending on your case!
# Even "insertions sort" can sometimes become the best sorting algorithm!
# https://www.toptal.com/developers/sorting-algorithms

# ================== Decision variables ==================
production_variables = pulp.LpVariable.dicts(name='X', indexs=input_df_dict['input_data'].index,
                                             lowBound=0, cat=pulp.LpContinuous)

inventory_variables = pulp.LpVariable.dicts(name='I', indexs=input_df_dict['input_data'].index,
                                            lowBound=0, cat=pulp.LpContinuous)

# Alternative way of creating the variables
# production_variables = {index: pulp.LpVariable(name='X_' + str(row['period']),
#                                                lowBound=0, cat=pulp.LpContinuous)
#                         for index, row in input_df_dict['input_data'].iterrows()}
#
# inventory_variables = {index: pulp.LpVariable(name='I_' + str(row['period']),
#                                               lowBound=0, cat=pulp.LpContinuous)
#                        for index, row in input_df_dict['input_data'].iterrows()}

logger.debug("var declaration time: {:.6f}".format(time() - start))

# Version 1
# ================== Inventory balance constraints ==================
for period, value in input_df_dict['input_data'].iloc[1:].iterrows():
    model.addConstraint(pulp.LpConstraint(
        e=inventory_variables[period - 1] + production_variables[period] - inventory_variables[period],
        sense=pulp.LpConstraintEQ,
        name='inv_balance' + str(period),
        rhs=value.demand))

# inv balance for first period
model.addConstraint(pulp.LpConstraint(
    e=production_variables[0] - inventory_variables[0],
    sense=pulp.LpConstraintEQ,
    name='inv_balance0',
    rhs=input_df_dict['input_data'].iloc[0].demand - input_param_dict['initial_inventory']))

# ================== Production capacity constraints ==================
for index, value in production_variables.items():
    model.addConstraint(pulp.LpConstraint(
        e=value,
        sense=pulp.LpConstraintLE,
        name='prod_cap_month_' + str(index),
        rhs=input_df_dict['input_data'].iloc[index].production_capacity))

"""
Following is an alternative way of defining the above 3 constraints.
I show you version 2 and 2-modified (the correct choice) for illustration.
Check for yourself the difference between the two.

# ================== Inventory balance constraints ==================
# Version 2
inv_balance_constraints = {
    period: model.addConstraint(pulp.LpConstraint(
        e=inventory_variables[period - 1] + production_variables[period] - inventory_variables[period],
        sense=pulp.LpConstraintEQ,
        name='inv_balance' + str(period),
        rhs=value.demand))
    for period, value in input_df_dict['input_data'].iloc[1:].iterrows()}

# Version 2-modified
inv_balance_constraints = {
    period: add_constr(model, pulp.LpConstraint(
        e=inventory_variables[period - 1] + production_variables[period] - inventory_variables[period],
        sense=pulp.LpConstraintEQ,
        name='inv_balance' + str(period),
        rhs=value.demand))
    for period, value in input_df_dict['input_data'].iloc[1:].iterrows()}

# inv balance for first period
first_period_inv_balance_constraints = add_constr(model, pulp.LpConstraint(
    e=production_variables[0] - inventory_variables[0],
    sense=pulp.LpConstraintEQ,
    name='inv_balance0',
    rhs=input_df_dict['input_data'].iloc[0].demand - input_param_dict['initial_inventory']))

# ================== Production capacity constraints ==================
production_capacity_constraints = {
    index: add_constr(model, pulp.LpConstraint(
        e=value,
        sense=pulp.LpConstraintLE,
        name='prod_cap_month_' + str(index),
        rhs=input_df_dict['input_data'].iloc[index].production_capacity))
    for index, value in production_variables.items()}

"""

# ================== Costs and objective function ==================
total_holding_cost = input_param_dict['holding_cost'] * pulp.lpSum(inventory_variables)
total_production_cost = pulp.lpSum(row['production_cost'] * production_variables[index]
                                   for index, row in input_df_dict['input_data'].iterrows())

objective = total_holding_cost + total_production_cost

model.setObjective(objective)
logger.info('Model creation time in sec: {:.4f}'.format(time() - start))

# ================== Optimization ==================
if model_params['write_lp']:
    logger.info('Writing the lp file!')
    model.writeLP(model.name + '.lp')

logger.info('Optimization starts!')
model.solve()

if model.status == pulp.LpStatusOptimal:
    logger.info('The solution is optimal and the objective value '
                'is ${:,.2f}'.format(pulp.value(model.objective)))

# ================== Output ==================
dict_of_variables = {'production_variables': production_variables,
                     'inventory_variables': inventory_variables}

output_df = process_data.write_outputs(dict_of_variables)
helper.write_to_csv(output_df)
logger.info('Outputs are written to csv!')
