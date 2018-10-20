#!/usr/bin/env python

import logging
from time import time

from process_data import load_data
from parameters import model_params

LOG_FORMAT = '%(asctime)s  %(name)-12s %(levelname)s : %(message)s'
logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
logger = logging.getLogger(__name__ + ': ')

# ================== Set up data ==================
input_df_dict, input_param_dict = load_data()
logger.info('Data is loaded!')

start = time()
# ================== Optimization ==================
if model_params['module'] == 'gurobi':
    from optimization_model_gurobi import OptimizationModel
    optimizer = OptimizationModel(input_df_dict['input_data'], input_param_dict)
else:
    from optimization_model_pulp import OptimizationModel
    optimizer = OptimizationModel(input_df_dict['input_data'], input_param_dict)

logger.info('Model creation time in sec: {:.4f}'.format(time() - start))
optimizer.optimize()

# ================== Output ==================
optimizer.create_output()
logger.info('Outputs are written to csv!')
