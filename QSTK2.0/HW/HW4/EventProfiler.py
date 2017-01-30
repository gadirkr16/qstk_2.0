'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on January, 23, 2013

@author: Sourabh Bajaj
@contact: sourabhbajaj@gatech.edu
@summary: Event Profiler Tutorial
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
        for i in range(1, len(ldt_timestamps)):
            # Calculating the returns for this timestamp
            f_symprice_today = df_close[s_sym].ix[ldt_timestamps[i]]
            f_symprice_yest = df_close[s_sym].ix[ldt_timestamps[i - 1]]
            f_symreturn_today = (f_symprice_today / f_symprice_yest) - 1
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
                sell_date =ldt_timestamps[i]
                if ldt_timestamps[i]+dt.timedelta(days=7) >= end_date:
                    sell_date = end_date
                else:
                    sell_date = ldt_timestamps[i+5]
                                                
                row = [sell_date.year, 
                       sell_date.month, 
                       sell_date.day,
                       s_sym,
                       "Sell",
                       100]
                writer.writerow(row)
                                                
                print ldt_timestamps[i],",",s_sym
                
    
    return df_events

def main(argv):
    ''' Main Function'''
    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    dataobj = da.DataAccess('Yahoo')
    ls_symbols = dataobj.get_symbols_from_list('sp5002012')
    ls_symbols.append('SPY')

    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)
    fl_name = 'EVENT_PROFILER_'
    fl_csv = '.csv'
    fl_pdf = '.pdf'            
    for i in range(5,11):
        file_name = fl_name+str(i)+fl_csv
        print file_name
        df_events = find_events_sym_less_than_x(ls_symbols, 
                                                d_data, 
                                                dt_end,
                                                i,
                                                file_name)
        print "Creating Study"
        file_name = fl_name+str(i)+fl_pdf
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
