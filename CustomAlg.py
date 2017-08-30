# Import the libraries we will use here.
from quantopian.algorithm import attach_pipeline, pipeline_output
from quantopian.pipeline import Pipeline
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.factors import Returns
from quantopian.pipeline import factors,filters,classifiers
from quantopian.pipeline.classifiers.morningstar import Sector
'''
def customUniverse():
    return filters.make_us_equity_universe(
        target_size=2000,
        rankby=factors.AverageDollarVolume(window_length=200),
        mask=filters.default_us_equity_universe_mask(),
        groupby=classifiers.morningstar.Sector(),
        max_group_weight=0.3,
        smoothing_func=lambda f: f.downsample('month_start'),
    )
'''
def initialize(context):
    """
    Called once at the start of the program. Any one-time
    startup logic goes here.
    """
    # Define context variables that can be accessed in other methods of
    # the algorithm.
    context.long_leverage = 0.5
    context.short_leverage = -0.5
    context.returns_lookback = 2
    context.sector = Sector()

    # Rebalance on the first trading day of each week at 11AM.
    schedule_function(rebalance,
                      date_rules.every_day(),
                      time_rules.market_close(minutes=1))
    '''
    # Record tracking variables at the end of each day.
    schedule_function(record_vars,
                      date_rules.every_day(),
                      time_rules.market_close(minutes=1))
    '''
    set_commission(commission.PerShare(cost=0, min_trade_cost=10))

    # Create and attach our pipeline (dynamic stock selector), defined below.
    attach_pipeline(make_pipeline(context), 'mean_reversion_example')


def make_pipeline(context):
    """
    A function to create our pipeline (dynamic stock selector). The pipeline is 
    used to rank stocks based on different factors, including builtin factors, 
    or custom factors that you can define. Documentation on pipeline can be 
    found here:
    https://www.quantopian.com/help#pipeline-title
    """

    # Filter for stocks in the Q1500US universe. For more detail, see this post:
    # https://www.quantopian.com/posts/the-q500us-and-q1500us
    # universe = Q1500US()
    
    # Create a Returns factor with a 5-day lookback window for all 
    # securities in our Q1500US Filter.
    recent_returns = Returns(window_length=context.returns_lookback,mask=filters.default_us_equity_universe_mask(minimum_market_cap=0))

    # Define high and low returns filters to be the bottom 10% and top 10% of
    # securities in the high dollar-volume group.
    low_returns = recent_returns.bottom(50)
    target_sector = context.sector.eq(101)

    # Add a filter to the pipeline such that only high-return and low-return
    # securities are kept.
    securities_to_trade = (low_returns&target_sector)

    # Create a pipeline object with the defined columns and screen.
    pipe = Pipeline(
        columns={
            'low_returns': low_returns,
        },
        screen = securities_to_trade
    )

    return pipe

def before_trading_start(context, data):
    """
    Called every day before market open. This is where we get the securities
    that made it through the pipeline.
    """

    # Pipeline_output returns a pandas DataFrame with the results of our factors
    # and filters.
    context.output = pipeline_output('mean_reversion_example')

    # Sets the list of securities we want to long as the securities with a 'True'
    # value in the low_returns column.
    context.long_secs = context.output[context.output['low_returns']][0:1]

    # A list of the securities that we want to order today.
    context.security_list = context.long_secs.index.tolist()

    # A set of the same securities, sets have faster lookup.
    # context.security_set = set(context.security_list)

def compute_weights(context):
    """
    Compute weights to our long and short target positions.
    """

    # Set the allocations to even weights for each long position, and even weights
    # for each short position.
    # long_weight = context.long_leverage / len(context.long_secs)
    
    return 1

def rebalance(context,data):
    """
    This rebalancing function is called according to our schedule_function settings.
    """

    long_weight = compute_weights(context)

    # For each security in our universe, order long or short positions according
    # to our context.long_secs and context.short_secs lists.
    for stock in context.security_list:
        if data.can_trade(stock):
            if stock in context.long_secs.index:
                order_target_percent(stock, long_weight)

    # Sell all previously held positions not in our new context.security_list.
    for stock in context.portfolio.positions:
        if data.can_trade(stock):
            order_target_percent(stock, 0)

    # Log the long and short orders each week.
    log.info("This week's longs: "+", ".join([long_.symbol for long_ in context.long_secs.index]))

def record_vars(context, data):
    """
    This function is called at the end of each day and plots certain variables.
    """
'''
    # Check how many long and short positions we have.
    longs = shorts = 0
    for position in context.portfolio.positions.itervalues():
        if position.amount > 0:
            longs += 1
        if position.amount < 0:
            shorts += 1

    # Record and plot the leverage of our portfolio over time as well as the
    # number of long and short positions. Even in minute mode, only the end-of-day
    # leverage is plotted.
    record(leverage = context.account.leverage, long_count=longs, short_count=shorts)
'''

