'''

@author: Gadi ROsenfeld
@contact: gadi.rosenfeld@leverate.com
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

#******************************************************************************#
#******************************************************************************#

def get_average_daily_returns(vals):
    rt_average_daily = 0
    na_rets = vals
    rt_average_daily = np.average(na_rets)
    return rt_average_daily

#******************************************************************************#

def get_standart_deviation(vals):
    rt_ret = 1
    na_rets = vals
    rt_ret = np.std(na_rets)
    return rt_ret

#******************************************************************************#

def get_total_returns(vals):
    rt_ret = 1
    na_rets = vals
    rt_daily = np.cumprod(na_rets+1, axis=1)
    rt_ret = np.prod(rt_daily,axis=0)
    return rt_ret[0]

#******************************************************************************#

def get_sharpe_ratio(vals):
    rt_sharpe = 0
    trading_days_in_year = 252
    rt_sharpe = (trading_days_in_year * get_average_daily_returns(vals))/(np.sqrt(trading_days_in_year)*get_standart_deviation(vals))
    return rt_sharpe

#******************************************************************************#

def get_statistics(vals):
    na_rets = np.array(vals.copy())
    tsu.returnize0(na_rets)    
    ret_total = get_total_returns(na_rets)
    ret_std = get_standart_deviation(na_rets)
    ret_avg = get_average_daily_returns(na_rets)
    ret_sharpe = get_sharpe_ratio(na_rets)    
    return ret_total, ret_std, ret_avg ,ret_sharpe

#******************************************************************************#

def print_statistics (portfolio, indices, dates, symbols_list):
    start_date = np.min(dates)
    end_date = np.max(dates)
    ind_total, ind_std, ind_avg, ind_sharpe = get_statistics(indices)
    port_total, port_std, port_avg, port_sharpe = get_statistics(portfolio)
    end_value = portfolio[len(portfolio)-1,0]
    print 
    print        
    print "The final value of the portfolio using the sample file is --",end_date
    print
    print "Data Range :",start_date, "to ", end_date, ",",end_value
    print    
    print "Details of the Performance of the portfolio :"
    print
    print "Sharpe Ratio of fund :" , port_sharpe
    print "Sharpe Ratio of ",symbols_list[0]," :" , ind_sharpe
    print
    print "Total Return of fund :",port_total 
    print "Total Return of ",symbols_list[0]," :",ind_total 
    print
    print "Standard Deviation of fund :", port_std
    print "Standard Deviation of ",symbols_list[0]," :", ind_std
    print
    print "Average Daily Return of fund :", port_avg
    print "Average Daily Return of ",symbols_list[0]," :", ind_avg

#******************************************************************************#
    
def read_daily_valuse_list (file_name):
    reader = csv.reader(open(file_name, 'rU'), delimiter=',')
    np_position_list = []
    for row in reader:
        np_position_list.append(row)
    return np_position_list

#******************************************************************************#

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

#******************************************************************************#

def get_daily_equity(portfolio):
    np_equity_list = []
    for obj in portfolio:
        np_equity_list.append(int(obj[3]))
    np_equity = np.array(np_equity_list, dtype = float).reshape(len(np_equity_list),1)
    return np_equity

#******************************************************************************#

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

#******************************************************************************#

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
    
    # Start and End date of the charts
    na_price = read_daily_valuse_list(fl_input)
    ls_dates = get_dates_array(na_price)
    ls_port = get_daily_equity(na_price)
    ls_indices = get_prices_array(ls_symbols,ls_dates)
    print_statistics(ls_port,ls_indices,ls_dates,ls_symbols)
            
    ls_indices = ls_indices * int(ls_port[0])/ls_indices[0]
    na_price = pd.DataFrame(index = ls_dates, columns=['Portfolio', 'Reference'])
    na_price['Portfolio'] = ls_port
    na_price['Reference'] = ls_indices
    
    fname = fl_input
    fname =fname.replace(".csv",".pdf")
    print fname
    # Plotting the prices with x-axis=timestamps
    plt.clf()
    plt.plot(ls_dates, na_price)
    plt.legend(['portfolio',fl_indices])
    plt.ylabel('Adjusted Close')
    plt.xlabel('Date')
    plt.savefig(fname, format='pdf')
    
if __name__ == '__main__':
    main(sys.argv[1:])
