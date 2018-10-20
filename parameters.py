# Ensure to have gurobi or cplex license if you intend to use either one

model_params = {
    'input_type': 'excel',  # 'csv' for csv files, 'excel' for excel sheets
    'solver': None,  # default is None for 'cbc'; can also be 'gurobi', 'cplex', 'glpk'
    'module': None,  # default is None for pulp; 'gurobi' for using gurobi
    'write_lp': True,  # whether to write the model .lp file
    'write_log': False,  # whether to write the output .log file
    'mip_gap': None,  # default is None to use the solver's default value. Can be any float less than 1.0
    'time_limit': None,  # in seconds
}
