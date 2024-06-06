AlwaysStandBruteForceSettings = {
    'Initial Money' : 1000,
    'Simulation Amount' : 10,
    'Bet Amount' : 100
}

AlwaysHitBruteForceSettings = {
    'Initial Money' : 1000,
    'Simulation Amount' : 10,
    'Threshold' : 17,
    'Bet Amount' : 100
}

RandomHitStandBruteForceSettings = {
    'Initial Money' : 1000,
    'Simulation Amount' : 10,
    'Bet Amount' : 100
}

BasicStrategyWithCountingSettings = {
    'Initial Money' : 1000,
    'Simulation Amount' : 10,
    'Doubleing Allowed' : True,
    'Minimum Bet' : 100,
    'Maximum Bet' : 2000
}

BasicStrategyWithoutCountingSettings = {
    'Initial Money' : 1000,
    'Simulation Amount' : 10,
    'Doubleing Allowed' : True,
    'Bet Amount' : 100
}

HistoricalDataSettings = {
    'Initial Money' : 1000,
    'Simulation Amount' : 10,
    'Data Source' : "etc/blackjack_simulator.csv",
    'Database Path' : 'src/historical_data/historical_data.db',
    'Doubleing Allowed' : False,
    'Bet Amount' : 100
}

RLSettings = {
    'Initial Money' : 1000,
    'Simulation Amount' : 10,
    'Bet Amount' : 100,
    "Q Table Path" : "src/reincforment_learing/q_table.pkl",
    "Alpha" : 0.1,
    "Gamma" : 0.9,
    "Epsilon" : 0.1,
    "Number of Episodes" : 1000000
}
