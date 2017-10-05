
class Mining:
    def __init__(
        self,
        invest_days=1460,
        eth_usd=300.0,
        usd_cost_per_megahash=30,
        start_megahash = 0,
        target_megahash = 150,
        daily_eth_per_megahash = 0.00051376,
        reinvest_ratio = 0.5,
        contract_length = 730,
        renew = True):

        self.invest_days = invest_days
        self.eth_usd = eth_usd
        self.usd_cost_per_megahash = usd_cost_per_megahash
        self.start_megahash = start_megahash
        self.target_megahash = target_megahash
        self.daily_eth_per_megahash = daily_eth_per_megahash
        self.reinvest_ratio = reinvest_ratio
        self.contract_length = contract_length
        self.renew = renew

        self.contracts = []
        self.paid_off = False
        self.payoff_days = self.invest_days
        self.eth_cost_per_megahash =  float(self.usd_cost_per_megahash) / float(self.eth_usd)
        self.megahashpower = self.start_megahash
        self.usd_payout = self.megahashpower * self.daily_eth_per_megahash * self.eth_usd
        self.ether_balance = self.eth_cost_per_megahash * self.target_megahash
        self.reinvest_ether_balance = self.ether_balance
        self.pocket_ether_balance = 0

    def start(self):
        for day in range(0,self.invest_days):
            if self.reinvest_ether_balance >= (self.eth_cost_per_megahash * self.target_megahash):
                self.buy_megahash(day)
            self.payout(day)
            self.expire(day)

        return {
            'start_balance_USD': self.ether_balance * self.eth_usd,
            'payoff_days': self.payoff_days,
            'num_contracts:': len(self.contracts),
            'reinvest_balance_USD': self.reinvest_ether_balance * self.eth_usd,
            'pocket_balance_USD': self.pocket_ether_balance * self.eth_usd,
            'megahash_power_MHs': self.megahashpower 
            }

    def buy_megahash(self, day):
        self.contracts.append(day + self.contract_length)
        self.megahashpower += self.target_megahash
        self.reinvest_ether_balance -= (self.eth_cost_per_megahash * self.target_megahash)

    def payout(self, day):
        payout = self.megahashpower * self.daily_eth_per_megahash
        self.reinvest_ether_balance += (self.reinvest_ratio * payout)
        self.pocket_ether_balance += (payout * (1 - self.reinvest_ratio))
        if (self.pocket_ether_balance >= self.ether_balance) and not self.paid_off:
            self.payoff_days = day
            self.paid_off = True
        return payout

    def expire(self, day):
        if len(self.contracts) > 0 and self.contracts[0] == day:
            self.contracts = self.contracts[1:]
            self.megahashpower -= self.target_megahash
            if self.renew and (self.pocket_ether_balance >= (self.target_megahash * self.eth_cost_per_megahash)):
                self.renew_contract(day)

    def renew_contract(self, day):
        self.pocket_ether_balance -= (self.target_megahash * self.eth_cost_per_megahash)
        self.contracts.append(day + self.contract_length)
        self.megahashpower += self.target_megahash


# optimze the best reinvest ratio
def optimize_reinvest_ratio(investment_period_days, eth_avg_price, target_hash, daily_payout_eth, contract_length_days):
    print 'Please wait while we optimize for best reinvestment ratio... '
    max_pocket = 0
    for i in range(0, 1000):    
        ratio = float(i) / 1000
        pocket = Mining(invest_days=investment_period_days, eth_usd=eth_avg_price, target_megahash=target_hash, daily_eth_per_megahash=daily_payout_eth, reinvest_ratio=ratio, contract_length=contract_length_days).start()['pocket_balance_USD']
        if pocket > max_pocket:
            max_pocket = pocket
            best_ratio = ratio
    return {'best_ratio': best_ratio, 'pocket_balance': max_pocket}

investment_period_years = raw_input('How many years do you want to invest? (1-20): ')
investment_period_days = int(investment_period_years) * 365
eth_avg_price = raw_input('What do you think the avg price of ETH will be over that time? ($): ')
eth_avg_price = float(eth_avg_price)
target = raw_input('How much do you want to invest up front? ($): ')
target_hash = float(target) / 30
daily_payout_eth = raw_input('How much ETH is paid out daily on avg by the miner? (ETH): ')
daily_payout_eth = float(daily_payout_eth)
contract_length_years = raw_input('What is the contract length in years? (1-5): ')
contract_length_days = int(contract_length_years) * 365

print optimize_reinvest_ratio(investment_period_days, eth_avg_price, target_hash, daily_payout_eth, contract_length_days)
    
