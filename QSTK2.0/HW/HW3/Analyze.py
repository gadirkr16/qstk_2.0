'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on January, 24, 2013

@author: Sourabh Bajaj
@contact: sourabhbajaj@gatech.edu
@summary: Example tutorial code.
'''

# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys , getopt, csv


def read_daily_valuse_list (file_name):
    reader = csv.reader(open(file_name, 'rU'), delimiter=',')
    np_position_list = []
    for row in reader:
        np_position_list.append(row)

    return np_position_list

def get_dates_array(positions_list):    
    np_dates = []
    for obj in positions_list:
        np_dates.append(dt.datetime(int(obj[0]),int(obj[1]),int(obj[2]),int(16),int(00)))
    # Reading the historical data.
    dt_end = np.max(np_dates)
    dt_start = np.min(np_dates)
    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)
    
    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
    return ldt_timestamps
def get_daily_equity(portfolio):
    np_equity = np.ndarray(shape=(len(portfolio),1), dtype =int)
    for i in range(0,len(portfolio)):
        print portfolio[i]
        #np_equity[i,0]=int(portfolio[i,3])              
    fla    
    return np_equity
def get_prices_array(instruments,dates):    
    # Creating an object of the dataaccess class with Yahoo as the source.
    c_dataobj = da.DataAccess('Yahoo')
          
    # Keys to be read from the data, it is good to read everything in one go.
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    
    # Reading the data, now d_data is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
    
    ldf_data = c_dataobj.get_data(dates, instruments, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    # Copying close price into separate dataframe to find rets
    df_rets = d_data['close'].copy()
    # Filling the data.
    df_rets = df_rets.fillna(method='ffill')
    df_rets = df_rets.fillna(method='bfill')
    df_rets = df_rets.fillna(1.0)
    
    # Numpy matrix of filled data values
    na_rets = df_rets.values
    return na_rets


def main(argv):
    ''' Main Function'''
    fl_input = ''
    fl_indices = ''
    ls_symbols = []
    na_price = []
    ls_port =[]
    if len(sys.argv)!=3:
       print "usage: python marketsim.py <input file name> <indices to compare>" 
       sys.exit()
    fl_input = sys.argv[1]
    fl_indices = sys.argv[2]  
    # List of symbols
    ls_symbols.append(str(fl_indices))
    print ls_symbols
    # Start and End date of the charts
    na_price = read_daily_valuse_list(fl_input)
    ls_dates = get_dates_array(na_price)
    ls_port = get_daily_equity(na_price)
    ls_indices = get_prices_array(ls_symbols,ls_dates)
    na_ind_rets = ls_indices.copy()
    tsu.returnize0(na_ind_rets)
    #na_port_rets = ls_port.copy()
    #tsu.returnize0(na_port_rets)
    print ls_port        
    ls_indices = ls_indices * int(ls_port[0])/ls_indices[0]
    na_price = pd.DataFrame(index = ls_dates, columns=['a', 'b'])
    na_price['a'] = ls_port
    na_price['b'] = ls_indices
    print na_ind_rets
    #print na_port_rets
    
    
    # Plotting the prices with x-axis=timestamps
    plt.clf()
    plt.plot(ls_dates, na_price)
    plt.legend(['portfolio',fl_indices])
    plt.ylabel('Adjusted Close')
    plt.xlabel('Date')
    plt.savefig('adjustedclose.pdf', format='pdf')
    
if __name__ == '__main__':
    main(sys.argv[1:])
