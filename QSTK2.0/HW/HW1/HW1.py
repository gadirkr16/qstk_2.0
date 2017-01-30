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


def simulate(start_date, end_date , symbols_lists, weights_list):
    ls_port_syms = symbols_lists
    lf_port_alloc = weights_list
    
    # Creating an object of the dataaccess class with Yahoo as the source.
    c_dataobj = da.DataAccess('Yahoo')

    # Reading the historical data.
    dt_end = end_date
    dt_start = start_date
    # print "start date" , dt_start
    # print "end date" , dt_end
    # print "symbols ", ls_port_syms
    # print "wights ", lf_port_alloc
    
    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)
    
    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
    
    # Keys to be read from the data, it is good to read everything in one go.
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    
    # Reading the data, now d_data is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_port_syms, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    
    # Copying close price into separate dataframe to find rets
    df_rets = d_data['close'].copy()
    # Filling the data.
    df_rets = df_rets.fillna(method='ffill')
    df_rets = df_rets.fillna(method='bfill')
    df_rets = df_rets.fillna(1.0)
    
    # Numpy matrix of filled data values
    na_rets = df_rets.values
    # returnize0 works on ndarray and not dataframes.
    tsu.returnize0(na_rets)
    
    # Estimate portfolio returns
    na_portrets = np.sum(na_rets * lf_port_alloc, axis=1)
    na_port_total = np.cumprod(na_portrets + 1)
    na_component_total = np.cumprod(na_rets + 1, axis=0)
    daily_ret = np.average(na_portrets)
    cum_ret  = na_port_total[np.count_nonzero(na_port_total - 1)]
    vol = np.std(na_portrets)
    sharpe = daily_ret/vol * np.sqrt(250)
    # print "average daily return:" , daily_ret
    # print "Cumulative Return:" , cum_ret 
    # print "volatility:" , vol 
    # print "sharpe ratio:" , sharpe 
    return (sharpe, vol, daily_ret, cum_ret) 

def build_array ( array):
    count = 0
    ls_sym_weight = [0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]
    
    for i in ls_sym_weight:
        for j in ls_sym_weight:
            for k in ls_sym_weight:
                for l in ls_sym_weight:
                    if (i+j+k+l) == 1:
                        array[count,0] = i
                        array[count,1] = j
                        array[count,2] = k
                        array[count,3] = l
                        count = count + 1
            
    
        
    
def main():
    ''' Main Function'''
    # List of symbols
    ls_symbols = ['C', 'GS', 'IBM', 'HNZ']
    #w = [0.4,0.4,0.0,0.2]
    dt_start = dt.datetime(2010, 1, 1)
    dt_end = dt.datetime(2010, 12, 31)
    #print simulate(dt_start,dt_end,ls_symbols,w)
    ls_all_weights = np.zeros(shape=(256,4))
    max_sharpe_ratio = 0
    opt_vol=0
    opt_d_ret =0
    opt_c_ret = 0
    
    # Start and End date of the charts
    build_array(ls_all_weights)
    count = 0;
    curr_sharpe =0
    curr_vol =0
    curr_daily_ret =0
    curr_cum_ret =0
    optimized_weights = ls_all_weights[0]
    while count<256:
        
        (curr_sharpe, 
        curr_vol, 
        curr_daily_ret , 
        curr_cum_ret)  =  simulate(
            dt_start,
               dt_end,
               ls_symbols,
               ls_all_weights[count]
               )
        if curr_sharpe >= max_sharpe_ratio:
           max_sharpe_ratio = curr_sharpe
           optimized_weights = ls_all_weights[count]
           opt_vol= curr_vol
           opt_d_ret = curr_daily_ret
           opt_c_ret = curr_cum_ret           
        count = count + 1
       
    print max_sharpe_ratio
    print optimized_weights
    print "start date:" , dt_start
    print "end date:" , dt_end
    print "symbols: ", ls_symbols
    print "weights (optimized) ", optimized_weights
    print "daily return: ", opt_d_ret
    print "commulative returns: ", opt_c_ret
    print "Volatility: ", opt_vol
    print "sharpe: ", max_sharpe_ratio
            
if __name__ == '__main__':
    main()
