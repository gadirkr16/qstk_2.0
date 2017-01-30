'''

@author: Gadi ROsenfeld
@contact: gadi.rosenfeld@leverate.com
@summary: Example tutorial code.

'''


import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep
import sys , getopt, csv

"""
Accepts a list of symbols along with start and end date
Returns the Event Matrix which is a pandas Datamatrix
Event matrix has the following structure :
    |IBM |GOOG|XOM |MSFT| GS | JP |
(d1)|nan |nan | 1  |nan |nan | 1  |
(d2)|nan | 1  |nan |nan |nan |nan |
(d3)| 1  |nan | 1  |nan | 1  |nan |
(d4)|nan |  1 |nan | 1  |nan |nan |
...................................
...................................
Also, d1 = start date
nan = no information about any event.
1 = status bit(positively confirms the event occurence)
"""


def find_events_sym_less_than_x(ls_symbols, d_data, end_date, nbr, fname):
    ''' Finding the event dataframe '''
    df_close = d_data['actual_close']
    ts_market = df_close['SPY']
    print "Finding Events"
    writer = csv.writer(open(fname,'wb'),delimiter=',')
    # Creating an empty dataframe
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_close.index
    
    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)-5):
            # Calculating the returns for this timestamp
            f_symprice_today = df_close[s_sym].ix[ldt_timestamps[i]]
            f_symprice_yest = df_close[s_sym].ix[ldt_timestamps[i - 1]]
            f_symreturn_today = (f_symprice_today / f_symprice_yest) - 1
            f_symreturn_5d = df_close[s_sym].ix[ldt_timestamps[i+5]]
            # Event is found if the symbol actual close today is less then 
            # nbr and it actual close yesterday was nbr or bigger
            row =[]
            if f_symprice_today < nbr and f_symprice_yest >= nbr :
                df_events[s_sym].ix[ldt_timestamps[i]] = 1
                row = [ldt_timestamps[i].year,
                       ldt_timestamps[i].month,
                       ldt_timestamps[i].day,
                       s_sym,
                       "Buy",
                       100]
                writer.writerow(row)
                row = [ldt_timestamps[i+5].year,
                       ldt_timestamps[i+5].month,
                       ldt_timestamps[i+5].day,
                       s_sym,
                       "Sell",
                       100]
                writer.writerow(row)
                                                
                print ldt_timestamps[i],",",s_sym,(f_symreturn_5d - f_symprice_today)*100,",",f_symreturn_5d/f_symprice_today-1,"%"
                
    
    return df_events

def main(argv):
    ''' Main Function'''
    dt_start = dt.datetime(2012, 1, 1)
    dt_end = dt.datetime(2013, 12, 31)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end+dt.timedelta(days=10), dt.timedelta(hours=16))
    nbr = 7
    dataobj = da.DataAccess('Yahoo')
    ls_symbols = dataobj.get_symbols_from_list('sp5002013')
    ls_symbols.append('SPY')

    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)
    
    fl_name = 'EVENT_PROFILER_'+str(nbr)+"_"+str(dt_start.year)+"_"+str(dt_end.year)
    fl_csv = '.csv'
    fl_pdf = '.pdf'
    file_name = fl_name+fl_csv
    print file_name
    df_events = find_events_sym_less_than_x(ls_symbols, 
                            d_data, 
                            dt_end,
                            nbr,
                            file_name)
    print "Creating Study"
    file_name = fl_name+fl_pdf
    print file_name    
    ep.eventprofiler(df_events, 
                     d_data, 
                     i_lookback=20, 
                     i_lookforward=20,
                     s_filename=file_name, 
                     b_market_neutral=True, 
                     b_errorbars=True,
                     s_market_sym='SPY')
    print "output name: %s" % (file_name)
    
if __name__ == '__main__':
    main(sys.argv[1:])
