import os
import pandas
import pandas as pd
from vis import simple_flightplan
from warnings import warn


def remove_codeshare(arrivals, departures):
    unique_arr = pandas.DataFrame(columns=arrivals.columns)
    unique_dep = pandas.DataFrame(columns=departures.columns)

    while (len(arrivals)) != 0:
        codeshares = arrivals.loc[arrivals['AC_REG'] == arrivals.iloc[0]['AC_REG']].loc[
            arrivals['ETA'] == arrivals.iloc[0]['ETA']]
        codeshares.iloc[0]['FLN'] = codeshares.FLN.str.cat(sep=',')
        arrivals = arrivals.drop(codeshares.index)
        unique_arr = pandas.concat((unique_arr, codeshares.drop(codeshares.iloc[1:].index)), ignore_index=True, axis=0,
                                   join='outer')

    while (len(departures)) != 0:
        codeshares = departures.loc[departures['AC_REG'] == departures.iloc[0]['AC_REG']].loc[
            departures['SDT'] == departures.iloc[0]['SDT']]
        codeshares.iloc[0]['FLN'] = codeshares.FLN.str.cat(sep=',')
        departures = departures.drop(codeshares.index)
        unique_dep = pandas.concat((unique_dep, codeshares.drop(codeshares.iloc[1:].index)), ignore_index=True, axis=0,
                                   join='outer')

    return unique_arr, unique_dep


def load_data(filepath, filename):
    flightplan = pandas.read_csv(os.path.join(filepath, filename))
    arr, dep = ([], [])
    for idx, row in flightplan.iterrows():
        row['ETA'] = pandas.to_datetime(row['ETA'])
        row['SDT'] = pandas.to_datetime(row['SDT'])

        if isinstance(row['ETA'], pandas._libs.tslibs.nattype.NaTType):
            row['ETA'] = None
            dep.append(idx)
        elif isinstance(row['SDT'], pandas._libs.tslibs.nattype.NaTType):
            row['SDT'] = None
            arr.append(idx)
        else:
            warn(f'Row does not contain a valid arrival or departure time and will be skipped. \n{print(row)}\n')
            continue

    arrivals, departures = remove_codeshare(flightplan.iloc[arr, :].sort_values('ETA'),
                                            flightplan.iloc[dep, :].sort_values('SDT'))
    regs = flightplan['AC_REG'].unique()

    return arrivals, departures, regs


def flight_pairing(arrivals, departures, regs, start, end):
    cols = [x for x in arrivals.columns[1:]]
    cols.append('FLN_arr');
    cols.append('FLN_dep')
    flight_pairs = pandas.DataFrame(columns=arrivals.columns[1:])
    FLNarr = []
    FLNdep = []
    for reg in regs:
        arr = arrivals.loc[arrivals['AC_REG'] == reg]
        dep = departures.loc[departures['AC_REG'] == reg]
        if len(arr) == 0:
            # assign departing flight 0 to an OVN (first departure is before the first arrival of the ACFT)
            flight_pairs = pandas.concat((flight_pairs, dep.iloc[0:1, 1:]), ignore_index=True, axis=0, join='outer')
            flight_pairs.iloc[-1]['ETA'] = start
            flight_pairs.iloc[-1]['SDT'] = dep.iloc[0]['SDT']
            FLNarr.append('OVN')
            FLNdep.append(dep.iloc[0]['FLN'])
            continue
        else:
            while len(arr) != 0:
                flight = arr.iloc[[0]]
                if len(dep) == 0:
                    # ACFT only arrives, assign it an OVN departure FLN
                    flight_pairs = pandas.concat((flight_pairs, flight.iloc[:, 1:]), ignore_index=True, axis=0,
                                                 join='outer')
                    flight_pairs.iloc[-1]['SDT'] = end
                    FLNarr.append(flight.iloc[0]['FLN'])
                    FLNdep.append('OVN')

                    # remove used flights
                    arr = arr.drop(arr.index[0], axis=0)

                elif dep.iloc[0]['SDT'] > flight.iloc[0]['ETA']:
                    # assign departing flight 0 to arriving flight 0 (first departure is after first arrival of the ACFT)
                    flight_pairs = pandas.concat((flight_pairs, flight.iloc[:, 1:]), ignore_index=True, axis=0,
                                                 join='outer')
                    # assign SDT
                    flight_pairs.iloc[-1]['SDT'] = dep.iloc[0]['SDT']
                    # assign arriving and departing flight numbers
                    FLNarr.append(flight.iloc[0]['FLN'])
                    FLNdep.append(dep.iloc[0]['FLN'])

                    # remove used flights
                    arr = arr.drop(arr.index[0], axis=0)
                    dep = dep.drop(dep.index[0], axis=0)

                elif dep.iloc[0]['SDT'] < flight.iloc[0]['ETA']:
                    # assign departing flight 0 to an OVN (first departure is before the first arrival of the ACFT)
                    flight_pairs = pandas.concat((flight_pairs, dep.iloc[0:1, 1:]), ignore_index=True, axis=0,
                                                 join='outer')
                    flight_pairs.iloc[-1]['ETA'] = start
                    flight_pairs.iloc[-1]['SDT'] = dep.iloc[0]['SDT']
                    FLNarr.append('OVN')
                    FLNdep.append(dep.iloc[0]['FLN'])

                    # assign departing flight 1 to arriving flight 0
                    flight_pairs = pandas.concat((flight_pairs, flight.iloc[:, 1:]), ignore_index=True, axis=0,
                                                 join='outer')
                    flight_pairs.iloc[-1]['SDT'] = dep.iloc[1]['SDT']
                    FLNarr.append(flight.iloc[0]['FLN'])
                    FLNdep.append(dep.iloc[1]['FLN'])

                    # remove used flights
                    arr = arr.drop(arr.index[0], axis=0)
                    dep = dep.drop([dep.index[0], dep.index[1]], axis=0)

    flight_pairs['FLN_arr'] = FLNarr
    del FLNarr
    flight_pairs['FLN_dep'] = FLNdep
    del FLNdep

    return flight_pairs


filepath = 'C:/Users/julia/OneDrive - ZHAW/MSc Engineering/VT2_AGAP/Data'
filename = 'Test_Dataset_7.csv'

# start and end times for OVN flights
start = pd.to_datetime('9:00')
end = pd.to_datetime('19:00')

arrivals, departures, regs = load_data(filepath, filename)
flightpairs = flight_pairing(arrivals, departures, regs, start, end)
simple_flightplan(flightpairs)
