import argparse
import pandas
import os

def load_data(filepath, filename):
    flightplan = pandas.read_csv(os.path.join(filepath, filename))

    for idx, row in flightplan.iterrows():
        row['ETA'] = pandas.to_datetime(row['ETA'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--flightplanpath', default='C:/Users/julia/OneDrive - ZHAW/MSc Engineering/VT2_AGAP/Data',
                        help='absolute path to raw flight plan data folder')
    parser.add_argument('--flightplanfile', default='Test_Dataset_7.csv', help='Name of raw flight plan data')
    args = parser.parse_args()

    filepath = args.flightplanpath
    filename = args.flightplanfile

    load_data(filepath, filename)



