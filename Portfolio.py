from Instrument import Instrument,Option,CashSpot,Transaction
import pandas as pd

class Portfolio(object):

    def __init__(self,notional,rate):
        self.transctions = []
        self.notional = notional
        self._rate = rate
        self._TotalDelta = 0.0
        self._TotalDeltaOld = 0.0
        self._TotalVega = 0.0
        self._TotalGamma = 0.0
        self._TotalTheta = 0.0
        self._TotalVolumeOfCalls = 0.0
        self._TotalVolumeOfPuts = 0.0
        self._TotalVolumeOfCashSpot = 0.0
        self._PortfolioPnL = 0.0
        self._PortfolioPnLOld = 0.0
        self._PortfolioPnLVariance = 0.0

    def PortfolioDelta(self,rate,InputData):
        self._TotalDeltaOld = self._TotalDelta
        self._TotalDelta = 0.0
        for i in self.transctions:
            if i.PrintVolume() != 0 and i.Instrument.InstrumentType() == 'Option':
                self._TotalDelta += i.TransactionDelta(rate,InputData)
        return self._TotalDelta

    def PrintPortDelta(self):
        return self._TotalDelta

    def PortfolioGamma(self,rate,InputData):
        self._TotalGamma = 0.0
        for i in self.transctions:
            if i.PrintVolume() != 0 and i.Instrument.InstrumentType() == 'Option':
                self._TotalGamma += i.TransactionGamma(rate,InputData)
        return self._TotalGamma

    def PrintPortGamma(self):
        return self._TotalGamma

    def PortfolioVega(self,rate,InputData):
        self._TotalVega = 0.0
        for i in self.transctions:
            if i.PrintVolume() != 0 and i.Instrument.InstrumentType() == 'Option':
                self._TotalVega += i.TransactionVega(rate,InputData)
        return self._TotalVega

    def PrintPortVega(self):
        return self._TotalVega

    def PortfolioTheta(self,rate,InputData):
        self._TotalTheta = 0.0
        for i in self.transctions:
            if i.PrintVolume() != 0 and i.Instrument.InstrumentType() == 'Option':
                self._TotalTheta += i.TransactionTheta(rate,InputData)
        return self._TotalTheta

    def PrintPortTheta(self):
        return self._TotalTheta

    def PortfolioPricer(self, InputData):
        #iterate through transctions given
        for i in self.transctions:
            i.PrintValue(InputData)

    def AddTransaction(self,transction):
        self.transctions.append(transction)

    def PrintNotional(self):
        return self.notional

    def UpdateNotional(self,value):
        self.notional = value

    def PrintRate(self):
        return self._rate

    def NumberOfTransactions(self):
        return len(self.transctions)

    def VolumeOfCalls(self):
        self._TotalVolumeOfCalls = 0
        for i in self.transctions:
            if i.Instrument.InstrumentType() == 'Option' and i.Instrument.isCall == True  and i.PrintVolume() != 0:
                self._TotalVolumeOfCalls += i.PrintVolume()
        return int(self._TotalVolumeOfCalls)

    def VolumeOfPuts(self):
        self._TotalVolumeOfPuts = 0
        for i in self.transctions:
            if i.Instrument.InstrumentType() == 'Option' and i.Instrument.isCall == False and i.PrintVolume() != 0:
                self._TotalVolumeOfPuts += i.PrintVolume()
        return int(self._TotalVolumeOfPuts)

    def VolumeOfCashSpot(self):
        for i in self.transctions:
            if i.Instrument.InstrumentType() == 'Index':
                self._TotalVolumeOfCashSpot += i.PrintVolume()
        return int(self._TotalVolumeOfCashSpot)

    def PortfolioPnL(self,InputData):
        self._PortfolioPnL = 0.0
        for i in self.transctions:
            self._PortfolioPnL += i.TransactionPnL(self._rate,InputData)
        self._PortfolioPnLVariance = self._PortfolioPnL - self._PortfolioPnLOld
        self._PortfolioPnLOld = self._PortfolioPnL

    def TotalPortfolioPnL(self):
        return self._PortfolioPnLVariance

    def AddPortfolioPnLToNational(self):
        self.notional += self._PortfolioPnLVariance

    def ExciseOptions(self,date,InputData):
        for i in self.transctions:
            if i.Instrument.InstrumentType() == 'Option' and i.PrintVolume() != 0:
                if i.Instrument.InstrumentExpiry() == int(date):
                    if i.PrintVolume() < 0: #short
                        isShort = True
                    else:
                        isShort = False

                    temp = self.PrintNotional() + i.Instrument.PayOff(self._rate,InputData,isShort)*i.PrintVolume()
                    self.UpdateNotional(temp)
                    i.UpdateVolume(0)

    def PortfolioHedging(self,delta,InputData):
        spot = InputData['Spot'].iloc[0]
        date = InputData['Date'].iloc[0]

        #buy CashSpot to hedge delta
        if self._TotalDelta > 0.0:
            RoundedTotalDelta = int(self._TotalDelta)
            if RoundedTotalDelta*spot <= self.PrintNotional():
                TempInstr = CashSpot('SPX',spot)
                TempTransaction = Transaction(TempInstr,RoundedTotalDelta,date)
                self.AddTransaction(TempTransaction)
                TempNotional = self.PrintNotional() - RoundedTotalDelta*spot
                self.UpdateNotional(TempNotional)
