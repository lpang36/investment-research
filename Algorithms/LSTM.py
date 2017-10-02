from keras.models import Sequential
from keras.layers import LSTM
import numpy as np
import pandas
import warnings

warnings.filterwarnings("ignore")

def load_all(filename):
	return pandas.read_csv(filename)

def load_one(df,ticker):
	return df.loc[df['ticker']==ticker][['volume','close.day','close.week','close.month']]

def load_all_spec(df,column='close.day',sample=-1):
	if sample<0:
		return df[column]
	else:
		tickers = np.random.choice(df.ticker.unique(),size=sample).tolist()
		all_spec = []
		for ticker in tickers:
			all_spec.append(df.loc[df['ticker']==ticker][column])
		return all_spec

def load_one_spec(df,ticker,column='close.day'):
	return df.loc[df['ticker']==ticker][column]

def train(df,ticker=None,oneFlag=False,specFlag=False,column='close.day',sample=64):
	dfset=[]
	input = []
	data_dim=0
	if oneFlag and specFlag:
		dfset = load_one_spec(df,ticker,column)
		data_dim = 1
	elif oneFlag:
		dfset = load_one(df,ticker)
		data_dim = 4
	else:
		dfset = load_all_spec(df,column,sample)
		data_dim = 1
	if oneFlag or specFlag:
		input = np.transpose(dfset.as_matrix())
	else:
		max = 0
		for ticker in dfset:
			if len(ticker.index)>max:
				max = len(ticker.index)
		input = np.zeros((0,max))
		for ticker in dfset:
			new_row = np.reshape(ticker.as_matrix(),(1,-1))
			zeros = np.zeros((1,max-np.shape(new_row)[1]))
			input = np.concatenate((input,np.concatenate((zeros,new_row),1)),0)
	print(np.shape(input))
	input = np.reshape(input,(np.shape(input)[0],np.shape(input)[1],1))
	timesteps = np.shape(input)[1]
	train_size = int(timesteps*0.75)
	model = Sequential()
	model.add(LSTM(32,return_sequences=True,input_shape=(None,1)))
	model.add(LSTM(32,return_sequences=True))
	model.add(LSTM(data_dim,return_sequences=True))
	model.compile(loss='mean_squared_error',
              optimizer='rmsprop',
              metrics=['accuracy'])
	x_train = input[:,0:train_size-1,:]
	y_train = input[:,1:train_size,:]
	x_val = input[:,0:timesteps-1,:]
	y_val = input[:,1:timesteps,:]
	model.fit(x_train,y_train,batch_size=32,epochs=10,validation_data=(x_val,y_val))
	
df = load_all("/home/lpang/Documents/GitHub/InvestmentResearch/Data/periods.csv")
train(df)
