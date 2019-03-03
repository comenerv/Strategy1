from Miscellaneous import DataImport, SupportFunc
from Portfolio import Portfolio
from Instrument import Instrument,Option,CashSpot,Transaction
import pandas as pd
from pandas.tseries.offsets import BDay
import math

class Strategy(object):
    def __init__(self,data,portfolio):
        self._data = data
        self._portfolio = portfolio

    #find the dates to trade straddles and the amount  -default by Fridays
    def Straddles(self,date,isSell=True,freq='W-FRI',MaxNotionalRatio=0.25,MaturityDays=25):
        NotionalAmount = self._portfolio.PrintNotional()*MaxNotionalRatio

        TradeDates = self._data.fridayDates()

        if date in TradeDates:
            if NotionalAmount > 0.0:
                TempData = self._data.singleDataColumn('Date',int(date))

                DateToMaturity = pd.to_datetime(date, format='%Y%m%d')
                expiry = (DateToMaturity + BDay(MaturityDays)).date()
                self.RunOneTrade(date,TempData,NotionalAmount,expiry.strftime('%Y%m%d'),self._portfolio.PrintRate())

    def RunOneTrade(self,date,TempData,NotionalAmount,expiry,rate):

        RoundedSpot = int(math.ceil(TempData['Spot'].iloc[0] / 10.0)) * 10

        OneCall = Option(RoundedSpot,int(expiry),True)
        args = rate, TempData
        OneCallValue = OneCall.InstrumentPricer(args)

        OnePut = Option(RoundedSpot,int(expiry),False)
        args = rate, TempData
        OnePutValue = OnePut.InstrumentPricer(args)

        VolumeToShort = int(NotionalAmount/((OneCallValue + OnePutValue) / 2)/2)

        OneCallTransaction = Transaction(OneCall,-VolumeToShort,date)
        OneCallTransaction.calV0(rate, TempData)
        self._portfolio.AddTransaction(OneCallTransaction)

        OnePutTransaction = Transaction(OnePut,-VolumeToShort,date)
        OnePutTransaction.calV0(rate, TempData)
        self._portfolio.AddTransaction(OnePutTransaction)

        self._portfolio.UpdateNotional(self._portfolio.PrintNotional() + VolumeToShort*OneCallValue + VolumeToShort*OnePutValue)
