# Ensure to have gurobi or cplex license if you intend to use either one

model_params = {
    'input_type': 'excel',  # 'csv' for csv files, 'excel' for excel sheets
    'solver': None,  # used for pulp. Default is None for 'cbc'; can also be 'cbc', 'gurobi', 'cplex', 'glpk', 'xpress'
    'module': None,  # default is None for pulp; can also be 'gurobi', 'cplex', and 'xpress'
    'write_lp': True,  # whether to write the model .lp file
    'write_log': False,  # whether to keep the output files such as .sol or .mps (or .log for cplex or gurobi)
    'display_log': False,  # displays information from the solver to stdout
    'mip_gap': None,  # default is None to use the solver's default value. Can be any float less than 1.0
    'time_limit': None,  # in seconds
    'cplex_cloud': False,  # control whether cplex solve runs locally or on cloud
    # Check here to learn how to get url and api for docloud:
    # https://developer.ibm.com/docloud/documentation/decision-optimization-on-cloud/api-key/
    'url': 'https://your_application_url.com',
    'api_key': 'your_key',
}
