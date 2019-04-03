import re
import os

DATA_DIR = '../data/'

def parse_tickers(in_file, out_file, exchange):
  for i, line in enumerate(in_file):
    if '\t' not in line:
      continue
    for ticker in re.split('\s+', line)[::-1]:
      if ticker and ticker == ticker.upper():
        out_file.write('%s:%s\n' % (exchange, ticker))
        break
        
parse_tickers(open(os.path.join(DATA_DIR, 'tsx_raw.txt')), open(os.path.join(DATA_DIR, 'tsx_tickers.txt'), 'w'), 'TSX')
parse_tickers(open(os.path.join(DATA_DIR, 'tsxv_raw.txt')), open(os.path.join(DATA_DIR, 'tsxv_tickers.txt'), 'w'), 'TSXV')