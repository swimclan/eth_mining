
class Mining:
    def __init__(self):
        self.invest_days = 1460
        self.eth_usd = 210.0
        self.eth_cost_per_megahash = 30 / self.eth_usd
        self.start_megahash = 0
        self.target_megahash = 150
        self.daily_eth_per_megahash = 0.00051376
        self.reinvest_ratio = 0.8
        self.contract_length = 730
        self.contracts = []
        self.paid_off = False
        self.renew = True

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
        print 'start balance (USD):', self.ether_balance * self.eth_usd
        print '# contracts:', len(self.contracts)
        print 'reinvest balance (USD):', self.reinvest_ether_balance * self.eth_usd
        print 'pocket balance (USD):', self.pocket_ether_balance * self.eth_usd
        print 'megahash power (MH/s):', self.megahashpower

    def buy_megahash(self, day):
        self.contracts.append(day + self.contract_length)
        self.megahashpower += self.target_megahash
        self.reinvest_ether_balance -= (self.eth_cost_per_megahash * self.target_megahash)

    def payout(self, day):
        payout = self.megahashpower * self.daily_eth_per_megahash
        self.reinvest_ether_balance += (self.reinvest_ratio * payout)
        self.pocket_ether_balance += (payout * (1 - self.reinvest_ratio))
        if (self.pocket_ether_balance >= self.ether_balance) and not self.paid_off:
            print 'Recouped initial investment on day:', day
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




Mining().start()
