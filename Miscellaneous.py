import sys
import datetime as dt
import pandas as pd
import numpy as np
import math

#to import data as dataframe
class DataImport(object):

    def __init__(self,location):
        #read in data, txt format
        self._dataframe = pd.read_csv(location)

    def singleDataColumn(self,colName,val):
        return self._dataframe.loc[self._dataframe[colName] == val]

    def fridayDates(self):
        dates = self._dataframe['Date'].as_matrix()
        return pd.date_range(str(dates[0]),str(dates[-1]),freq='W-FRI') # friday strategy

    def PushData(self):
        return self._dataframe

class SupportFunc(object):

    def busDayCount(sdate,edate):
        #count business days between two given days
        date1= dt.datetime.strptime(sdate,'%Y%m%d').date()
        date2= dt.datetime.strptime(edate,'%Y%m%d').date()
        return np.busday_count( date1,  date2)

    def volAtExpiry(expiry,df):
        tempExp1 = df['Volatility'].where(df['Maturity'] >= float(expiry))
        tempExp2 = [i for i in tempExp1 if str(i) != 'nan']
        return tempExp2[0]
