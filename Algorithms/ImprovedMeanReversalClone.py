import numpy as np

def initialize(context):
    # list of tradeable securities. Below: an example
    context.tradeables_list = [sid(3951),sid(1637),sid(2673),sid(351),sid(1221),
                               sid(24),sid(5061),sid(3766),sid(1900)]
    # 30% max drawdown
    context.max_drawdown = 0.3
    context.day_counter = 0
    # Historical price database
    context.database = {}
    for security in context.tradeables_list:
        # Initiate an empty list of prices for each security
        context.database[security] = []

def handle_data(context, data):
    context.day_counter += 1
    for security in context.tradeables_list:
        context.database[security].append(data[security]['price'])
    # We need to collect 30 days of data before we start trading.
    if context.day_counter >= 30: 
        for security in context.tradeables_list:
            # past 10 and past 30 prices, respectively
            past10 = (context.database[security][-10:])[::-1]
            past30 = (context.database[security][-30:])[::-1]
            mean10 = np.mean(past10)
            mean30 = np.mean(past30)
            # has the asset been increasing in value for the last three days?
            trend10p = past10[0]>=past10[1]>=past10[2]>=past10[3]
            # or falling?
            trend10n = past10[0]<=past10[1]<=past10[2]<=past10[3]
            
            # If we hold a security, we want to test if it is time to sell.
            # (Securities even with amount 0 may still be listed in portfolio, so it's
            #  necessary to double-check)
            if security in context.portfolio.positions.keys():
                #and context.portfolio.positions[security].amount > 0:
                # Checking that the 10-day moving average is below the 30-day moving average,
                # and that the price of the security has been falling for four days
                if mean10 < mean30*0.95 and trend10p:
                    order(security, -context.portfolio.positions[security].amount)
                # 8% stop-loss
                elif context.portfolio.positions[security].cost_basis*0.92 >=data[security]['price']:
                    order(security, -context.portfolio.positions[security].amount)
                       
            # If we don't hold a security: check if we should buy it.
            # Check if the 10-day moving average is above the 30-day moving average,
            # and that the price of the security has been rising for four days
            elif mean10>mean30*1.05 and trend10n:
                # But if the security appears to be falling in price long-term,
                # then going for mean-reversion might not be a good idea, so we pass.
                if past30[0]<=past30[5]<=past30[10]<=past30[15]:
                    pass
                elif security not in context.portfolio.positions.keys():
                    # The heuristic below is to prevent investing too much in one security.
                    p = data[security]['price']
                    toInvest = (context.portfolio.cash) * (context.max_drawdown**0.75)
                    numShares = max(0,np.round(toInvest/p))
                    order(security, numShares)

