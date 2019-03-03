from abc import ABCMeta, abstractmethod
from Miscellaneous import SupportFunc
import numpy as np
import scipy.stats as sta
import math

#Black-Scholes model from wikipedia: https://en.wikipedia.org/wiki/Black%E2%80%93Scholes_model
class BSmodel(object):

    def __init__(self,S0,K,r,sigma,T,isCall=True):
        #inputs are
        self._S0 = S0   #start underlying price
        self._K = K     #strike
        self._r = r     #short rate
        self._sigma = sigma #spot volatility
        self._T = T         #maturity
        self._isCall = isCall   #boolean to check if it is a call option
        self._d1 = (np.log(self._S0/self._K) + (self._r + self._sigma**2 / 2) * self._T)/(self._sigma * np.sqrt(self._T))   #d1 of Black-Scholes model
        self._d2 = (np.log(self._S0 / self._K) + (self._r - self._sigma**2 / 2) * self._T)/(self._sigma * np.sqrt(self._T)) #d2 of Black-Scholes model

    def BSpricer(self):
        if self._isCall == True:
            return self._S0 * sta.norm.cdf(self._d1) - self._K * np.exp(-self._r * self._T) * sta.norm.cdf(self._d2)
        else:
            return self._K * np.exp(-self._r * self._T) * sta.norm.cdf(-self._d2) - self._S0 * sta.norm.cdf(-self._d1)

    # greeks for individual facilities
    def calDelta(self):
        if self._isCall == True:
            return sta.norm.cdf(- self._d1)
        else:
            return sta.norm.cdf(- self._d1) - 1

    def calGamma(self):
        return np.exp(-self._d1**2/2)/(self._S0*self._sigma*np.sqrt(self._T)*np.sqrt(2*math.pi))

    def calVega(self):
        return np.exp(-self._d1**2/2)*self._S0*np.sqrt(self._T)/(np.sqrt(2*math.pi)*100.0)

    def calTheta(self):
        if self._isCall == True:
            return (-((self._S0*self._sigma)*(np.exp(-self._d1**2/2)/np.sqrt(2*math.pi)))/(2*np.sqrt(self._T)) - self._r*self._K*np.exp(-self._r*self._T)*sta.norm.cdf(self._d2))/365
        else:
            return (-((self._S0*self._sigma)*(np.exp(-self._d1**2/2)/np.sqrt(2*math.pi)))/(2*np.sqrt(self._T)) + self._r*self._K*np.exp(-self._r*self._T)*sta.norm.cdf(-self._d2))/365


#create an abstruct parent class - inherited child classes are option and cashspot
class Instrument(object):
    def __init__(self, instrType):
        self._instrumentType = instrType
        self._value = 0.0
        self._V0 = 0.0
        self._delta = 0

    @abstractmethod
    def InstrumentType(self):
        pass

    def InstrumentValue(self):
        return self._value

    @abstractmethod
    def InstrumentGreeks(self):
        pass

    @abstractmethod
    def InstrumentPricer(self,*args,modelname):
        pass

#inherited child class - European vanilla option
class Option(Instrument):
    # inputs: strike, time to maturity in year fraction, isCall = True/False,
    def __init__(self,strike,expiry,isCall=True):
        self._instrumentType = 'Option'
        self.isCall = isCall
        self._strike = strike
        self._expiry = int(expiry)
        self._model = None
        self._value = 0.0
        self._V0 = 0.0

    def InstrumentValue(self):
        return self._value

    def InstrumentV0(self):
        return self._V0

    def calV0(self,args):
        self._V0 = self.InstrumentPricer(args)

    def InstrumentPricer(self,args,modelname='BSmodel'):
        rate = args[0]
        rows = args[1]
        valuedate = rows['Date'].iloc[0]
        spot = rows['Spot'].iloc[0]
        vol = SupportFunc.volAtExpiry(self._expiry,rows)

        if valuedate < self._expiry:
            busDays = SupportFunc.busDayCount(str(valuedate),str(self._expiry))
            if modelname == 'BSmodel':
                self._model = BSmodel(spot,self._strike,rate,vol,busDays/250,self.isCall)
                self._value = self._model.BSpricer()

        return self._value

    #the pay off of this instrument
    def PayOff(self,*args,modelname='BSmodel'):
        rows = args[1]
        isShort = args[2]
        spot = rows['Spot'].iloc[0]

        if isShort == True and self.isCall == True:
            _payOff =   self._strike + self._V0 - spot
        elif isShort == True and self.isCall == False:
            _payOff = - self._strike + self._V0  + spot

        return _payOff

    def InstrumentGreeks(self,args,modelname='BSmodel'):
        return self.OptDelta(args,modelname='BSmodel'), self.OptGamma(args,modelname='BSmodel'), self.OptVega(args,modelname='BSmodel'), self.OptTheta(args,modelname='BSmodel')

    def OptDelta(self,args,modelname='BSmodel'):
        rate = args[0]
        rows = args[1]
        valuedate = rows['Date'].iloc[0]
        spot = rows['Spot'].iloc[0]
        vol = SupportFunc.volAtExpiry(self._expiry,rows)

        if valuedate < self._expiry:
            busDays = SupportFunc.busDayCount(str(valuedate),str(self._expiry))
            if modelname == 'BSmodel':
                self._model = BSmodel(spot,self._strike,rate,vol,busDays/250,self.isCall)
                return self._model.calDelta()
        else:
            return 0.0

    def OptGamma(self,args,modelname='BSmodel'):
        rate = args[0]
        rows = args[1]
        valuedate = rows['Date'].iloc[0]
        spot = int(math.ceil(rows['Spot'].iloc[0]/10.0)* 10)
        vol = SupportFunc.volAtExpiry(self._expiry,rows)

        if valuedate < self._expiry:
            busDays = SupportFunc.busDayCount(str(valuedate),str(self._expiry))
            if modelname == 'BSmodel':
                self._model = BSmodel(spot,self._strike,rate,vol,busDays/250,self.isCall)
                return self._model.calGamma()
        else:
            return 0.0

    def OptVega(self,args,modelname='BSmodel'):
        rate = args[0]
        rows = args[1]
        valuedate = rows['Date'].iloc[0]
        spot = int(math.ceil(rows['Spot'].iloc[0]/10.0)* 10)
        vol = SupportFunc.volAtExpiry(self._expiry,rows)

        if valuedate < self._expiry:
            busDays = SupportFunc.busDayCount(str(valuedate),str(self._expiry))
            if modelname == 'BSmodel':
                self._model = BSmodel(spot,self._strike,rate,vol,busDays/250,self.isCall)
                return self._model.calVega()
        else:
            return 0.0

    def OptTheta(self,args,modelname='BSmodel'):
        rate = args[0]
        rows = args[1]
        valuedate = rows['Date'].iloc[0]
        spot = int(math.ceil(rows['Spot'].iloc[0]/10.0)* 10)
        vol = SupportFunc.volAtExpiry(self._expiry,rows)

        if valuedate < self._expiry:
            busDays = SupportFunc.busDayCount(str(valuedate),str(self._expiry))
            if modelname == 'BSmodel':
                self._model = BSmodel(spot,self._strike,rate,vol,busDays/250,self.isCall)
                return self._model.calTheta()
        else:
            return 0.0

    #difference of purchase value and current one - which will can be used for strategy transaction pnl calculation
    def valueChange(self,args):
        return self.InstrumentPricer(args) - self.InstrumentV0()

    def InstrumentType(self):
        return 'Option'

    def InstrumentExpiry(self):
        return self._expiry

#inherited child class - CashSpot
class CashSpot(Instrument):

    def __init__(self, name, value):
        self._V0 = value
        self._name = name

    def InstrumentName(self):
        return self._name

    def InstrumentValue(self):
        return self._value

    def InstrumentV0(self):
        return self._V0

    def InstrumentType(self):
        return 'CashSpot'

    #price of underlying is the spot price
    def InstrumentPricer(self,args):
        rows = args[1]
        self._value = rows['Spot'].iloc[0]
        return self._value

    #valuechange is the linear difference
    def valueChange(self,args):
        return self.InstrumentPricer(args) - self.InstrumentV0()

#calculate metrics multi-volume on one same instruments
class Transaction(object):
    def __init__(self,Instrument,volume,date):
        self.Instrument = Instrument
        self._volume = volume
        self._date = date

    def TransactionGreeks(self):
        delta,gamma,vega,theta = self.Instrument.InstrumentGreeks()
        return delta*self._volume,gamma*self._volume,vega*self._volume,theta*self._volume

    def UpdateVolume(self,volume):
        self._volume = volume

    def PrintVolume(self):
        return self._volume

    def UpdateDate(self,date):
        self._date = date

    def PrintDate(self):
        return self._date

    def PrintValue(self):
        return self._value

    def calV0(self,*args):
        self._value = self.Instrument.calV0(args)

    def TransactionPricer(self,*args):
        return self.Instrument.InstrumentPricer(args)

    def TransactionPnL(self,*args):
        return self.Instrument.valueChange(args)*abs(self._volume)

    def TransactionDelta(self,*args):
        return self.Instrument.OptDelta(args)*self._volume

    def TransactionGamma(self,*args):
        return self.Instrument.OptGamma(args)*self._volume

    def TransactionVega(self,*args):
        return self.Instrument.OptVega(args)*self._volume

    def TransactionTheta(self,*args):
        return self.Instrument.OptTheta(args)*self._volume
