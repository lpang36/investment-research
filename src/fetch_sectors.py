from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time
import argparse
import os

OUTPUT_FILE = '../data/sector_data.txt'

parser = argparse.ArgumentParser()
parser.add_argument('--reset', action='store_true')
args = parser.parse_args()

if args.reset:
    os.remove(OUTPUT_FILE)
    flag = True
elif os.path.exists(OUTPUT_FILE):
    last_ticker = filter(bool, open(OUTPUT_FILE).read().split('\n'))[-1].split('\t')[0]
    flag = False
else:
    flag = True

driver = webdriver.Chrome()
BASE_URL = 'https://web.tmxmoney.com/company.php?qm_symbol=%s'

for ticker in open('../data/extended_tsx_tickers.txt').read().split('\n'):
    if not flag:
        if last_ticker == ticker:
            flag = True
        continue
    ticker = ticker.split(':')[1]
    r = driver.get(BASE_URL % ticker)
    time.sleep(3)
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        tbl = soup.find('div', class_='companyprofile').table.tbody
        rows = tbl.find_all(recursive=False)[-3:]
        current_data = {}
        for row in rows:
            current_label = None
            for child in row.find_all(recursive=False):
                if 'label' in child.get('class', []):
                    current_label = child.getText().strip()
                elif 'data' in child.get('class', []):
                    current_data[current_label] = child.getText().strip()
        print current_data
        open(OUTPUT_FILE, 'a').write('%s\t%s\n' % (ticker, repr(current_data)))
    except Exception as e:
        print 'Parsing failed for ticker %s, error %s' % (ticker, e)
