import errno
import glob
import os

import pandas as pd

from parameters import model_params


def get_file_directory(file):
    try:
        script_path = os.path.dirname(__file__)
    except NameError:
        return os.path.abspath(file)
    file_path = os.path.join(script_path, file)
    return file_path


def ensure_directory_exists(directory):
    # Create the 'directory' if it doesn't exists. If it exists,
    # it does nothing unless the error code is something else!
    try:
        os.makedirs(directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def read_excel(input_file):
    excel_file = pd.ExcelFile(input_file)
    input_df_dict = {sheet_name: excel_file.parse(sheet_name)
                     for sheet_name in excel_file.sheet_names}
    return input_df_dict


def read_csv_files(input_files):
    input_df_dict = {}
    for _file in input_files:
        file_name = os.path.basename(_file)[:-4]  # excluding '.csv' from the name
        df = pd.read_csv(_file)
        input_df_dict[file_name] = df
    return input_df_dict


def load_raw_data():
    if model_params['input_type'] == 'excel':
        # I assume I only have one excel file in the directory
        _input_file = glob.glob(get_file_directory('data/excel/') + '*.xlsx')[0]
        if not _input_file:
            raise ValueError('Invalid file path! No Excel file was found!')
        input_df_dict = read_excel(_input_file)
    elif model_params['input_type'] == 'csv':
        _input_file = glob.glob(get_file_directory('data/csv/') + '*.csv')
        if not _input_file:
            raise ValueError('Invalid file path! No csv file was found!')
        input_df_dict = read_csv_files(_input_file)
    else:
        raise ValueError('input_type parameter should be either "excel" or "csv"!')

    return input_df_dict


def write_to_csv(output_df_dict, output_folder='output'):
    output_dir = get_file_directory(output_folder + '/')
    ensure_directory_exists(output_dir)
    for key, df in output_df_dict.items():
        out_name = ''.join(('optimal_', key, '.csv'))
        df.to_csv(os.path.join(output_dir, out_name))
