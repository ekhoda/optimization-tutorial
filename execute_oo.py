#!/usr/bin/env python

import logging
from time import time

from process_data import load_data
from parameters import model_params

if model_params['module'] == 'gurobi':
    from optimization_model_gurobi import OptimizationModel
elif model_params['module'] == 'cplex':
    from optimization_model_docplex import OptimizationModel
elif model_params['module'] == 'xpress':
    from optimization_model_xpress import OptimizationModel
else:
    from optimization_model_pulp import OptimizationModel

__author__ = 'Ehsan Khodabandeh'
__version__ = '1.1'
# ====================================

LOG_FORMAT = '%(asctime)s  %(name)-12s %(levelname)s : %(message)s'
logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
logger = logging.getLogger(__name__ + ': ')

# ================== Set up data ==================
input_df_dict, input_param_dict = load_data()
logger.info('Data is loaded!')

# ================== Optimization ==================
start = time()
optimizer = OptimizationModel(input_df_dict['input_data'], input_param_dict)
logger.info(f'Model creation time in sec: {time() - start:.4f}')
optimizer.optimize()

# ================== Output ==================
optimizer.create_output()
logger.info('Outputs are written to csv!')
