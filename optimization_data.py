import glob
import logging

import helper
from parameters import model_params

logger = logging.getLogger(__name__ + ': ')


def load_data():
    if model_params['input_type'] == 'excel':
        # I assume I only have one excel file in the directory
        _input_file = glob.glob(helper.get_file_directory('data/excel/') + '*.xlsx')[0]
        if not _input_file:
            raise ValueError('Invalid file path! No Excel file was found!')
        input_df_dict = helper.read_excel(_input_file)
    elif model_params['input_type'] == 'csv':
        _input_file = glob.glob(helper.get_file_directory('data/csv/') + '*.csv')
        if not _input_file:
            raise ValueError('Invalid file path! No csv file was found!')
        input_df_dict = helper.read_csv_files(_input_file)
    else:
        raise ValueError('input_type parameter should be either "excel" or "csv"!')

    input_param_dict = input_df_dict['parameters'].set_index('attribute')['value'].to_dict()
    logger.info('Data is loaded!')
    return input_df_dict, input_param_dict
