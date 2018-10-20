import pandas as pd

from helper import load_raw_data


def load_data():
    return get_modified_data(load_raw_data())


def get_modified_data(input_df_dict):
    # Our "parameters" table is very simple here. So, we can create a new dictionary
    # for our parameters as follows or just modify our df a little in place.
    # There shouldn't be any performance gain here to concern us, so I went with
    # the dictionary. In the comment below, I also show the latter for illustration

    # input_df_dict['parameters'].set_index('attribute', inplace=True)

    input_param_dict = input_df_dict['parameters'].set_index('attribute')['value'].to_dict()
    return input_df_dict, input_param_dict


# To not overkill, I only created one module here for processing the data, either input or output
def _create_outputs_df(opt_series, cols, name, output_df_dict):
    df = pd.DataFrame(data=opt_series, index=opt_series.index.values).reset_index()
    df.columns = cols
    output_df_dict[name] = df


def write_outputs(dict_of_variables, attr='varValue'):
    """
    The outputs we want are very simple and can be achieved almost identically
    in either pulp or gurobi. The only difference is in the attribute name of their
    decision variable value.
    In gurobi you get it by 'your_dv.x' and in pulp by 'your_dv.varValue'.
    """

    output_df_dict = {}
    cols = ['period', 'value']
    for name, var in dict_of_variables.items():
        opt_series = pd.Series({k + 1: getattr(v, attr) for k, v in var.items()})
        _create_outputs_df(opt_series, cols, name, output_df_dict)
    return output_df_dict
