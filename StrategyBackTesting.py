from Miscellaneous import DataImport, SupportFunc
from Portfolio import Portfolio
from Instrument import Instrument
from Strategy import Strategy
import time
import pickle

class Backtest(object):
    def __init__(self,portfolio,MaxNotionalRatio=0.25,DaysToMaturity=25,rate=0.0005):
        self.portfolio = portfolio
        self.data = None
        self.MaxNotionalRatio = MaxNotionalRatio
        self.DaysToMaturity = DaysToMaturity
        self.output = []

    def BT(self):
        self.data = DataImport('spx_vols.txt')
        tempData = self.data.PushData()
        AllDates = sorted(set(tempData['Date']))
        LocalStrategy = Strategy(self.data,self.portfolio)
        rate = self.portfolio.PrintRate()
        lable = ['Date','Delta','Gamma','Vega','Theta','#Call','#Put','#CashSpot','$P&L','$Notional']
        self.output.append(lable)

        for OneDate in AllDates:
            LocalStrategy.Straddles(str(OneDate),True,'W-FRI',self.MaxNotionalRatio,self.DaysToMaturity)
            DataForOneDate = self.data.singleDataColumn('Date',int(OneDate))
            self.portfolio.PortfolioDelta(rate,DataForOneDate)
            self.portfolio.PortfolioGamma(rate,DataForOneDate)
            self.portfolio.PortfolioVega(rate,DataForOneDate)
            self.portfolio.PortfolioTheta(rate,DataForOneDate)
            self.portfolio.PortfolioHedging(self.portfolio.PrintPortDelta(),DataForOneDate)
            self.portfolio.ExciseOptions(OneDate,DataForOneDate)
            self.portfolio.PortfolioPnL(DataForOneDate)
            self.portfolio.AddPortfolioPnLToNational()
            if self.portfolio.PrintNotional() > 0.0:
                temp = [OneDate,self.portfolio.PrintPortDelta(),self.portfolio.PrintPortGamma(),self.portfolio.PrintPortVega(), self.portfolio.PrintPortTheta(),self.portfolio.VolumeOfCalls(),self.portfolio.VolumeOfPuts(),self.portfolio.VolumeOfCashSpot(),self.portfolio.TotalPortfolioPnL(),self.portfolio.PrintNotional()]
                self.output.append(temp)
            else:
                temp = [OneDate,self.portfolio.PrintPortDelta(),self.portfolio.PrintPortGamma(),self.portfolio.PrintPortVega(), self.portfolio.PrintPortTheta(),self.portfolio.VolumeOfCalls(),self.portfolio.VolumeOfPuts(),self.portfolio.VolumeOfCashSpot(),self.portfolio.TotalPortfolioPnL(),self.portfolio.PrintNotional()]
                self.output.append(temp)
                break

def main():
    CashinHand = 1000000
    BaseRate = 0.01
    myBook = Portfolio(CashinHand,BaseRate)

    myBookBT = Backtest(myBook,0.25,25,0.01)
    myBookBT.BT()
    #print(myBookBT.output)
    thefile = open('output.txt', 'w')
    for item in myBookBT.output:
        thefile.write("%s\n" % item)
    thefile.close()

if __name__ == '__main__':
    main()
