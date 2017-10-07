import prices

class Mining:
    def __init__(
        self,
        invest_days=3650,
        eth_usd=400.0,
        start_megahash = 0,
        initial_investment = 15000,
        daily_eth_per_megahash = 0.000141,
        reinvest_ratio = 0.7,
        contract_length = 730,
        full_reinvest_til_even = False,
        renew = True):

        self.plans = prices.plans()
        self.invest_days = invest_days
        self.eth_usd = eth_usd
        self.start_megahash = start_megahash
        self.target_megahash = self.lookupHash(initial_investment)['hashrate']
        self.daily_eth_per_megahash = daily_eth_per_megahash
        self.reinvest_ratio = reinvest_ratio
        self.full_reinvest_til_even = full_reinvest_til_even
        self.contract_length = contract_length
        self.renew = renew

        self.contracts = []
        self.paid_off = False
        self.first_buy = True
        self.payoff_days = self.invest_days
        self.megahashpower = self.start_megahash
        self.usd_payout = self.megahashpower * self.daily_eth_per_megahash * self.eth_usd
        self.ether_balance = self.lookupHash(initial_investment)['cost'] / self.eth_usd
        self.reinvest_ether_balance = self.ether_balance
        self.pocket_ether_balance = 0

    def start(self, printout):
        for day in range(0,self.invest_days):
            reinvest_plan = self.lookupHash(self.reinvest_ether_balance * self.eth_usd)
            if self.full_reinvest_til_even:
                if self.paid_off or self.first_buy:
                    self.buy_megahash(day, reinvest_plan)
                    if self.first_buy:
                        self.first_buy = False
            else:
                self.buy_megahash(day, reinvest_plan)
            self.payout(day)
            self.expire(day)
            if printout:
                print '-------------------------------------------------------------'
                print 'DAY', day
                print 'reinvest plan', reinvest_plan['hashrate'], 'MH'
                print 'pocket balance:', self.pocket_ether_balance * self.eth_usd
                print 'reinvest balance:', self.reinvest_ether_balance * self.eth_usd
                print 'number of contracts:', len(self.contracts)
                print 'hashpower (MH):', self.megahashpower

        return {
            'start_balance_USD': self.ether_balance * self.eth_usd,
            'payoff_days': self.payoff_days,
            'num_contracts:': len(self.contracts),
            'reinvest_balance_USD': self.reinvest_ether_balance * self.eth_usd,
            'pocket_balance_USD': self.pocket_ether_balance * self.eth_usd,
            'megahash_power_MHs': self.megahashpower 
            }

    def buy_megahash(self, day, plan):
        if plan['cost'] > 0:
            self.contracts.append({'expires': day + self.contract_length, 'hashrate': plan['hashrate']})
            self.megahashpower += plan['hashrate']
            self.reinvest_ether_balance -= (plan['cost'] / self.eth_usd)

    def payout(self, day):
        payout = self.megahashpower * self.daily_eth_per_megahash
        if self.full_reinvest_til_even:        
            if self.paid_off:
                self.reinvest_ether_balance += (self.reinvest_ratio * payout)
                self.pocket_ether_balance += (payout * (1 - self.reinvest_ratio))
            else:
                self.reinvest_ether_balance += payout
        else:
            self.reinvest_ether_balance += (self.reinvest_ratio * payout)
            self.pocket_ether_balance += (payout * (1 - self.reinvest_ratio))            

        if ((self.pocket_ether_balance >= self.ether_balance) or (self.reinvest_ether_balance > self.ether_balance)) and not self.paid_off:
            self.payoff_days = day
            self.paid_off = True
        return payout

    def expire(self, day):
        if len(self.contracts) > 0:
            oldest_contract = self.contracts[0]
            if oldest_contract['expires'] == day:
                self.contracts = self.contracts[1:]
                self.megahashpower -= oldest_contract['hashrate']
                if self.renew:
                    self.renew_contract(day, oldest_contract)

    def renew_contract(self, day, contract):
        plan = self.lookupHashCost(contract['hashrate'])
        if plan['cost'] <= (self.pocket_ether_balance * self.eth_usd):
            self.pocket_ether_balance -= (plan['cost'] / self.eth_usd)
            self.contracts.append({'expires': day + self.contract_length, 'hashrate': plan['hashrate']})
            self.megahashpower += plan['hashrate']

    def lookupHash(self, usd):
        ret = self.plans[0]
        for plan in self.plans:
            if plan['cost'] <= usd:
                ret = plan
        return ret

    def lookupHashCost(self, hash):
        ret = self.plans[0]
        for plan in self.plans:
            if plan['hashrate'] <= hash:
                ret = plan
        return ret


# optimze the best reinvest ratio
def optimize_reinvest_ratio(investment_period_days, eth_avg_price, initial_investment, daily_payout_eth, contract_length_days):
    print 'Please wait while we optimize for best reinvestment ratio... '
    max_pocket = 0
    best_ratio = 0
    best_payoff = investment_period_days
    for i in range(0, 1000):
        ratio = float(i) / 1000
        mining = Mining(invest_days=investment_period_days, eth_usd=eth_avg_price, initial_investment=initial_investment, daily_eth_per_megahash=daily_payout_eth, reinvest_ratio=ratio, contract_length=contract_length_days).start(False)
        pocket = mining['pocket_balance_USD']
        if pocket > max_pocket:
            max_pocket = pocket
            best_ratio = ratio
            best_payoff = mining['payoff_days']
    return {'best_ratio': best_ratio, 'pocket_balance': max_pocket, 'payoff_days': best_payoff}

def prompt():
    investment_period_years = raw_input('How many years do you want to invest? (1-20): ')
    investment_period_days = int(investment_period_years) * 365
    eth_avg_price = raw_input('What do you think the avg price of ETH will be over that time? ($): ')
    eth_avg_price = float(eth_avg_price)
    initial_investment = raw_input('How much do you want to invest up front? ($): ')
    daily_payout_eth = raw_input('How much ETH is paid out daily on avg by the miner? (ETH): ')
    daily_payout_eth = float(daily_payout_eth)
    contract_length_years = raw_input('What is the contract length in years? (1-5): ')
    contract_length_days = int(contract_length_years) * 365
    print optimize_reinvest_ratio(investment_period_days, eth_avg_price, initial_investment, daily_payout_eth, contract_length_days)

#print Mining().start(printout=True)
prompt()
    