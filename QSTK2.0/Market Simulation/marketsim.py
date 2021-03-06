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
import sys , getopt
import csv

############################################################################

def read_positions_list (file_name):
    
    #reader = csv.reader(open(file_name, 'rU'), delimiter=',')
    na_positions_raw = pd.read_csv(file_name)
    na_positions_raw.columns = ['year','month','day','symbol','direction','amount']
    print na_positions_raw
    
    print dates
    
    
                
    return na_positions


############################################################################

def get_dates_array(positions_list):    
    #np_dates = []
    #date = 0
    #for obj in positions_list:
    #    date =  dt.datetime(int(obj[0]),int(obj[1]),int(obj[2]),16,00)
    #    np_dates.append(date)
     
    
      
    # Reading the historical data.
    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)
    print "The final value of the portfolio using the sample file is -- " , dt_end
    
    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)
    
    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
    
    return ldt_timestamps

############################################################################

def get_instruments_list(positions_list):
    ls_instruments=[]
    for obj in positions_list:
            ls_instruments.append(obj[3])   
    ls_instruments = np.unique(ls_instruments)
    return ls_instruments

############################################################################

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
    print na_rets
    return na_rets

############################################################################

def get_daily_amounts(positions, prices, dates,symbols,balance):
    ls_daily_amounts = np.zeros(prices.shape)
    index = len(positions)
    size =  len(dates)
    daily_balance = np.zeros(size)
    daily_balance.fill(balance)
    
    for nbr in range(0,index):
        obj = positions[nbr]
        symbol_index = np.where(obj[3]==symbols)
        curr_date = dt.datetime(int(obj[0]),int(obj[1]),int(obj[2]),int(16),int(00))
        date_index = dates.index(curr_date)
        if obj[4] == "Buy":
            ls_daily_amounts[ date_index, symbol_index] += int(obj[5])
            balance_change = -1 * ls_daily_amounts[ date_index, symbol_index]* prices[ date_index, symbol_index]
            print balance_change
        else:
            ls_daily_amounts[ date_index, symbol_index] -= int(obj[5])
            balance_change =  -1 * ls_daily_amounts[ date_index, symbol_index]* prices[ date_index, symbol_index]
            print balance_change        
        for nbr in range(date_index,size):
            daily_balance[nbr]=daily_balance[nbr]+balance_change
    for date in range(1,size):
        ls_daily_amounts[ date, :]=ls_daily_amounts[ date, :]+ls_daily_amounts[ date-1, :]     
   
    return ls_daily_amounts,daily_balance

############################################################################

def write_output(file_name,dates,daily_equity):
    size =  np.count_nonzero(dates)
    output_array = np.zeros((size,4))
    for index in range(0,size):
        output_array[index,0] = int(dates[index].year)
        output_array[index,1] = int(dates[index].month)
        output_array[index,2] = int(dates[index].day)
        output_array[index,3] = int(daily_equity[index])
    np.savetxt( file_name, output_array,fmt='%4.0u,%2.0u,%2.0u,%10.2u')

############################################################################

def main(argv):
    ''' Main Function'''
    init_balance = ''
    fl_input = ''
    fl_output = ''
    if len(sys.argv)!=4:
        print "usage: python marketsim.py <amount> <input file name> <output file name>" 
        sys.exit()
    init_balance = sys.argv[1]
    fl_input = sys.argv[2]
    fl_output = sys.argv[3]  
    ls_positions = read_positions_list(fl_input)
    ls_dates = get_dates_array(ls_positions)
    ls_instruments = get_instruments_list(ls_positions)
    ls_prices = get_prices_array(ls_instruments,ls_dates)
    ls_amounts, ls_balance = get_daily_amounts(ls_positions,ls_prices,ls_dates,ls_instruments,init_balance)
    na_open_PnL = np.sum(ls_amounts *ls_prices,axis=1)   
    na_equity = na_open_PnL+ls_balance
    write_output(fl_output,ls_dates,na_equity)
            
if __name__ == '__main__':
    main(sys.argv[1:])
