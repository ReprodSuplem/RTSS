import pandas as pd
import os
import re
from functools import reduce
from matplotlib import pyplot as plt
import seaborn as sns
import numpy as np


def alter(file, old_str, new_str):
	file_data = ''
	with open(file, "r", encoding = "utf-8") as f:
		for line in f:
			if old_str in line:
				line = line.replace(old_str, new_str)
			file_data += line
	with open(file, "w", encoding = "utf-8") as f:
		f.write(file_data)
 

class logInfo:
	def __init__(self, ipHpNum, satHpNum):
		rootPath = os.getcwd()
		self.ipHpNum = ipHpNum
		self.satHpNum = satHpNum
		self.ipPath = rootPath + "/ip/hp{}".format(ipHpNum)
		self.satPath = rootPath + "/maxsat/hp{}".format(satHpNum)
		self.ipDirList = os.listdir(self.ipPath)
		self.satDirList = os.listdir(self.satPath)

	def ipInfoGenerate(self):
		if os.path.exists("ipInfo{}.txt".format(self.ipHpNum)):
			os.remove("ipInfo{}.txt".format(self.ipHpNum))
		for ipDirName in self.ipDirList:
			ipLogPath = self.ipPath + "/" + ipDirName
			ipLogList = os.listdir(ipLogPath)
			for ipLogName in ipLogList:
				ipLogfile = open(ipLogPath + "/" + ipLogName)
				for line in ipLogfile.readlines()[::-1]:
					ipInfo = line.split()
					if ipInfo[0:2] == ['Solution', 'time']:
						with open("ipInfo{}.txt".format(self.ipHpNum), "a+") as txtf:
							txtf.write(',path:'+ipLogPath+',name:'+ipLogName+',time:'+ipInfo[3]+'\n')
					if ipInfo[0:1] == ['z']:
						with open("ipInfo{}.txt".format(self.ipHpNum), "a+") as txtf:
							txtf.write(',z:'+ipInfo[1])
				ipLogfile.close()
		with open("ipInfo{}.txt".format(self.ipHpNum), "r+") as txtf:
			content = txtf.read()
			txtf.seek(0, 0)
			txtf.write(',z,path,name,time\n'+content)
		with open("ipInfo{}.txt".format(self.ipHpNum), "r+") as txtf:
			for line in txtf.readlines():
				if re.match(r"(,z)", line) == None:
					alter("ipInfo{}.txt".format(self.ipHpNum), line, ',z:'+line)

	def satInfoGenerate(self):
		if os.path.exists("satInfo{}.txt".format(self.satHpNum)):
			os.remove("satInfo{}.txt".format(self.satHpNum))
		for satDirName in self.satDirList:
			satLogPath = self.satPath + "/" + satDirName
			satLogList = os.listdir(satLogPath)
			for satLogName in satLogList:
				satLogfile = open(satLogPath + "/" + satLogName)
				for line in satLogfile.readlines():
					satInfo = line.split()
					if satInfo[1:3] == ['Latest', 'Answer']:
						with open("satInfo{}.txt".format(self.satHpNum), "a+") as txtf:
							txtf.write(',path:'+satLogPath+',name:'+satLogName+',z:'+satInfo[4])
					if satInfo[0:3] == ['s', 'OPTIMUM', 'FOUND']:
						with open("satInfo{}.txt".format(self.satHpNum), "a+") as txtf:
							txtf.write(',optimum found')
					if satInfo[0:2] == ['s', 'UNSATISFIABLE']:
						with open("satInfo{}.txt".format(self.satHpNum), "a+") as txtf:
							txtf.write(',unsatisfiable')
					if satInfo[0:2] == ['s', 'UNKNOWN']:
						with open("satInfo{}.txt".format(self.satHpNum), "a+") as txtf:
							txtf.write(',unknown')
					if satInfo[2:5] == ['Number', 'of', 'variables:']:
						with open("satInfo{}.txt".format(self.satHpNum), "a+") as txtf:
							txtf.write(',numOfVar:'+satInfo[5])
					if satInfo[2:5] == ['Number', 'of', 'clauses:']:
						with open("satInfo{}.txt".format(self.satHpNum), "a+") as txtf:
							txtf.write(',numOfCla:'+satInfo[5])
					if satInfo[1:3] == ['CPU', 'time']:
						with open("satInfo{}.txt".format(self.satHpNum), "a+") as txtf:
							txtf.write(',time:'+satInfo[4]+'\n')
				satLogfile.close()
		with open("satInfo{}.txt".format(self.satHpNum), "r+") as txtf:
			content = txtf.read()
			txtf.seek(0, 0)
			txtf.write(',var,cla,ifFeasible,path,name,z,time\n'+content)
		with open("satInfo{}.txt".format(self.satHpNum), "r+") as txtf:
			for line in txtf.readlines():
				if re.search(r"(unsatisfiable)", line) or re.search(r"(unknown)", line):
					lineHead = line.split('z:')[0]
					lineTail = line.split(',')[-1]
					alter("satInfo{}.txt".format(self.satHpNum), line, lineHead+'z:,'+lineTail)


def ipDataFrame(ipHpNum):
	dfIp = pd.read_csv("ipInfo{}.txt".format(ipHpNum), sep = ",")
	dfIp = dfIp[['z', 'path', 'name', 'time']]
	ipPathLabel = dfIp['path'].str.extract(r"(\d+)v-(\d+)_(\d+)")
	ipPathLabel = ipPathLabel[0]+'T'+'-['+ipPathLabel[1]+','+ipPathLabel[2]+']P'
	dfIp.loc[:, 'path'] = ipPathLabel
	dfIp = dfIp.sort_values(by = ['path', 'name'])
	dfIp = dfIp.reset_index(drop = True)
	dfIp['z'] = dfIp['z'].str.extract(r"(\d+)")
	dfIp['name'] = dfIp['name'].str.extract(r"(\d+-\d+)")
	dfIp['time'] = dfIp['time'].str.extract(r"(\d+.\d+)").astype(float)
	return dfIp


def satDataFrame(satHpNum):
	dfSat = pd.read_csv("satInfo{}.txt".format(satHpNum), sep = ",")
	dfSat = dfSat[['var', 'cla', 'z', 'path', 'name', 'time']]
	satPathLabel = dfSat['path'].str.extract(r"(\d+)v-(\d+)_(\d+)")
	satPathLabel = satPathLabel[0]+'T'+'-['+satPathLabel[1]+','+satPathLabel[2]+']P'
	dfSat.loc[:, 'path'] = satPathLabel
	dfSat = dfSat.sort_values(by = ['path', 'name'])
	dfSat = dfSat.reset_index(drop = True)
	dfSat['var'] = dfSat['var'].str.extract(r"(\d+)")
	dfSat['cla'] = dfSat['cla'].str.extract(r"(\d+)")
	dfSat['name'] = dfSat['name'].str.extract(r"(\d+-\d+)")
	dfSat['z'] = dfSat['z'].str.extract(r"(\d+)")
	dfSat['time'] = dfSat['time'].str.extract(r"(\d+.\d+)").astype(float)
	return dfSat

def table1(datafme):
	timeMean = datafme['time'].mean()
	lenOfDf = len(datafme)
	return "({0}){1}".format(lenOfDf, timeMean)


if __name__ == "__main__":
	for i in range(1, 3):
		logToTxt = logInfo(ipHpNum = i, satHpNum = i)
		logToTxt.ipInfoGenerate()
		logToTxt.satInfoGenerate()


	# summarize data to csv
	dfIpHp1 = ipDataFrame(1)
	dfIpHp2 = ipDataFrame(2)
	dfSatHp1 = satDataFrame(1)
	dfSatHp2 = satDataFrame(2)
	df = [dfIpHp1, dfIpHp2, dfSatHp1, dfSatHp2]
	df_merge = reduce(lambda left, right: pd.merge(left, right, on = ['path','name']), df)
	df_merge.columns = ['opt_ipHp1', 'group', 'instance', 'time_ipHp1', 'opt_ipHp2', 'time_ipHp2', \
	'variables_satHp1', 'clauses_satHp1', 'opt_satHp1', 'time_satHp1', \
	'variables_satHp2', 'clauses_satHp2', 'opt_satHp2', 'time_satHp2']
	df_merge = df_merge[['group', 'instance', 'opt_ipHp1', 'time_ipHp1', 'opt_ipHp2', 'time_ipHp2', \
	'variables_satHp1', 'clauses_satHp1', 'opt_satHp1', 'time_satHp1', \
	'variables_satHp2', 'clauses_satHp2', 'opt_satHp2', 'time_satHp2']]
	df_merge.to_csv("allLogInfo.csv", index = False)


	# if z != None and time < 597 s
	ip_hp1 = dfIpHp1[(dfIpHp1['z'].isna() == False) & (dfIpHp1['time'] < 597)]
	ip_hp1 = ip_hp1.sort_values(by = 'time')
	ip_hp2 = dfIpHp2[(dfIpHp2['z'].isna() == False) & (dfIpHp2['time'] < 597)]
	ip_hp2 = ip_hp2.sort_values(by = 'time')
	sat_hp1 = dfSatHp1[(dfSatHp1['z'].isna() == False) & (dfSatHp1['time'] < 597)]
	sat_hp1 = sat_hp1.sort_values(by = 'time')
	sat_hp2 = dfSatHp2[(dfSatHp2['z'].isna() == False) & (dfSatHp2['time'] < 597)]
	sat_hp2 = sat_hp2.sort_values(by = 'time')


	# figure 1
	sns.set_style('whitegrid')
	figure, axes = plt.subplots(1, 5, figsize = (24, 4))
	axes[0].set_title('10T-[1,4]P')
	sns.lineplot(x = range(len(ip_hp1[ip_hp1['path'] == '10T-[01,04]P'])), y = 'time', \
		data = ip_hp1[ip_hp1['path'] == '10T-[01,04]P'], ax = axes[0], label = 'ip-hp1', marker = '^')
	df_tmp = pd.DataFrame(ip_hp1[ip_hp1['path'] == '10T-[01,04]P'])['time']
	df_tmp.index = range(1,len(df_tmp)+1)
	#df_tmp.to_csv("ip-hp1@10T-01_04P.dat")
	sns.lineplot(x = range(len(ip_hp2[ip_hp2['path'] == '10T-[01,04]P'])), y = 'time', \
		data = ip_hp2[ip_hp2['path'] == '10T-[01,04]P'], ax = axes[0], label = 'ip-hp2', marker = 'o')
	df_tmp = pd.DataFrame(ip_hp2[ip_hp2['path'] == '10T-[01,04]P'])['time']
	df_tmp.index = range(1,len(df_tmp)+1)
	#df_tmp.to_csv("ip-hp2@10T-01_04P.dat")
	sns.lineplot(x = range(len(sat_hp1[sat_hp1['path'] == '10T-[01,04]P'])), y = 'time', \
		data = sat_hp1[sat_hp1['path'] == '10T-[01,04]P'], ax = axes[0], label = 'sat-hp1', marker = 'p')
	df_tmp = pd.DataFrame(sat_hp1[sat_hp1['path'] == '10T-[01,04]P'])['time']
	df_tmp.index = range(1,len(df_tmp)+1)
	#df_tmp.to_csv("sat-hp1@10T-01_04P.dat")
	sns.lineplot(x = range(len(sat_hp2[sat_hp2['path'] == '10T-[01,04]P'])), y = 'time', \
		data = sat_hp2[sat_hp2['path'] == '10T-[01,04]P'], ax = axes[0], label = 'sat-hp2', marker = 's')
	df_tmp = pd.DataFrame(sat_hp2[sat_hp2['path'] == '10T-[01,04]P'])['time']
	df_tmp.index = range(1,len(df_tmp)+1)
	#df_tmp.to_csv("sat-hp2@10T-01_04P.dat")
	axes[0].set_yticks(np.arange(0, 1.2, 0.2))

	axes[1].set_title('10T-[7,10]P')
	sns.lineplot(x = range(len(ip_hp1[ip_hp1['path'] == '10T-[07,10]P'])), y = 'time', \
		data = ip_hp1[ip_hp1['path'] == '10T-[07,10]P'], ax = axes[1], marker = '^')
	df_tmp = pd.DataFrame(ip_hp1[ip_hp1['path'] == '10T-[07,10]P'])['time']
	df_tmp.index = range(1,len(df_tmp)+1)
	#df_tmp.to_csv("ip-hp1@10T-07_10P.dat")
	sns.lineplot(x = range(len(ip_hp2[ip_hp2['path'] == '10T-[07,10]P'])), y = 'time', \
		data = ip_hp2[ip_hp2['path'] == '10T-[07,10]P'], ax = axes[1], marker = 'o')
	df_tmp = pd.DataFrame(ip_hp2[ip_hp2['path'] == '10T-[07,10]P'])['time']
	df_tmp.index = range(1,len(df_tmp)+1)
	#df_tmp.to_csv("ip-hp2@10T-07_10P.dat")
	sns.lineplot(x = range(len(sat_hp1[sat_hp1['path'] == '10T-[07,10]P'])), y = 'time', \
		data = sat_hp1[sat_hp1['path'] == '10T-[07,10]P'], ax = axes[1], marker = 'p')
	df_tmp = pd.DataFrame(sat_hp1[sat_hp1['path'] == '10T-[07,10]P'])['time']
	df_tmp.index = range(1,len(df_tmp)+1)
	#df_tmp.to_csv("sat-hp1@10T-07_10P.dat")
	sns.lineplot(x = range(len(sat_hp2[sat_hp2['path'] == '10T-[07,10]P'])), y = 'time', \
		data = sat_hp2[sat_hp2['path'] == '10T-[07,10]P'], ax = axes[1], marker = 's')
	df_tmp = pd.DataFrame(sat_hp2[sat_hp2['path'] == '10T-[07,10]P'])['time']
	df_tmp.index = range(1,len(df_tmp)+1)
	#df_tmp.to_csv("sat-hp2@10T-07_10P.dat")
	axes[1].set_yticks(np.arange(0, 600, 200))

	axes[2].set_title('20T-[1,4]P')
	sns.lineplot(x = range(len(ip_hp1[ip_hp1['path'] == '20T-[01,04]P'])), y = 'time', \
		data = ip_hp1[ip_hp1['path'] == '20T-[01,04]P'], ax = axes[2], marker = '^')
	df_tmp = pd.DataFrame(ip_hp1[ip_hp1['path'] == '20T-[01,04]P'])['time']
	df_tmp.index = range(1,len(df_tmp)+1)
	#df_tmp.to_csv("ip-hp1@20T-01_04P.dat")
	sns.lineplot(x = range(len(ip_hp2[ip_hp2['path'] == '20T-[01,04]P'])), y = 'time', \
		data = ip_hp2[ip_hp2['path'] == '20T-[01,04]P'], ax = axes[2], marker = 'o')
	df_tmp = pd.DataFrame(ip_hp2[ip_hp2['path'] == '20T-[01,04]P'])['time']
	df_tmp.index = range(1,len(df_tmp)+1)
	#df_tmp.to_csv("ip-hp2@20T-01_04P.dat")
	sns.lineplot(x = range(len(sat_hp1[sat_hp1['path'] == '20T-[01,04]P'])), y = 'time', \
		data = sat_hp1[sat_hp1['path'] == '20T-[01,04]P'], ax = axes[2], marker = 'p')
	df_tmp = pd.DataFrame(sat_hp1[sat_hp1['path'] == '20T-[01,04]P'])['time']
	df_tmp.index = range(1,len(df_tmp)+1)
	#df_tmp.to_csv("sat-hp1@20T-01_04P.dat")
	sns.lineplot(x = range(len(sat_hp2[sat_hp2['path'] == '20T-[01,04]P'])), y = 'time', \
		data = sat_hp2[sat_hp2['path'] == '20T-[01,04]P'], ax = axes[2], marker = 's')
	df_tmp = pd.DataFrame(sat_hp2[sat_hp2['path'] == '20T-[01,04]P'])['time']
	df_tmp.index = range(1,len(df_tmp)+1)
	#df_tmp.to_csv("sat-hp2@20T-01_04P.dat")
	axes[2].set_yticks(np.arange(0, 2, 0.5))

	axes[3].set_title('20T-[7,10]P')
	sns.lineplot(x = range(len(ip_hp1[ip_hp1['path'] == '20T-[07,10]P'])), y = 'time', \
		data = ip_hp1[ip_hp1['path'] == '20T-[07,10]P'], ax = axes[3], marker = '^')
	df_tmp = pd.DataFrame(ip_hp1[ip_hp1['path'] == '20T-[07,10]P'])['time']
	df_tmp.index = range(1,len(df_tmp)+1)
	#df_tmp.to_csv("ip-hp1@20T-07_10P.dat")
	sns.lineplot(x = range(len(ip_hp2[ip_hp2['path'] == '20T-[07,10]P'])), y = 'time', \
		data = ip_hp2[ip_hp2['path'] == '20T-[07,10]P'], ax = axes[3], marker = 'o')
	df_tmp = pd.DataFrame(ip_hp2[ip_hp2['path'] == '20T-[07,10]P'])['time']
	df_tmp.index = range(1,len(df_tmp)+1)
	#df_tmp.to_csv("ip-hp2@20T-07_10P.dat")
	sns.lineplot(x = range(len(sat_hp1[sat_hp1['path'] == '20T-[07,10]P'])), y = 'time', \
		data = sat_hp1[sat_hp1['path'] == '20T-[07,10]P'], ax = axes[3], marker = 'p')
	df_tmp = pd.DataFrame(sat_hp1[sat_hp1['path'] == '20T-[07,10]P'])['time']
	df_tmp.index = range(1,len(df_tmp)+1)
	#df_tmp.to_csv("sat-hp1@20T-07_10P.dat")
	sns.lineplot(x = range(len(sat_hp2[sat_hp2['path'] == '20T-[07,10]P'])), y = 'time', \
		data = sat_hp2[sat_hp2['path'] == '20T-[07,10]P'], ax = axes[3], marker = 's')
	df_tmp = pd.DataFrame(sat_hp2[sat_hp2['path'] == '20T-[07,10]P'])['time']
	df_tmp.index = range(1,len(df_tmp)+1)
	#df_tmp.to_csv("sat-hp2@20T-07_10P.dat")
	axes[3].set_yticks(np.arange(0, 610, 200))

	axes[4].set_title('50T-[1,4]P')
	sns.lineplot(x = range(len(ip_hp1[ip_hp1['path'] == '50T-[01,04]P'])), y = 'time', \
		data = ip_hp1[ip_hp1['path'] == '50T-[01,04]P'], ax = axes[4], marker = '^')
	df_tmp = pd.DataFrame(ip_hp1[ip_hp1['path'] == '50T-[01,04]P'])['time']
	df_tmp.index = range(1,len(df_tmp)+1)
	#df_tmp.to_csv("ip-hp1@50T-01_04P.dat")
	sns.lineplot(x = range(len(ip_hp2[ip_hp2['path'] == '50T-[01,04]P'])), y = 'time', \
		data = ip_hp2[ip_hp2['path'] == '50T-[01,04]P'], ax = axes[4], marker = 'o')
	df_tmp = pd.DataFrame(ip_hp2[ip_hp2['path'] == '50T-[01,04]P'])['time']
	df_tmp.index = range(1,len(df_tmp)+1)
	#df_tmp.to_csv("ip-hp2@50T-01_04P.dat")
	sns.lineplot(x = range(len(sat_hp1[sat_hp1['path'] == '50T-[01,04]P'])), y = 'time', \
		data = sat_hp1[sat_hp1['path'] == '50T-[01,04]P'], ax = axes[4], marker = 'p')
	df_tmp = pd.DataFrame(sat_hp1[sat_hp1['path'] == '50T-[01,04]P'])['time']
	df_tmp.index = range(1,len(df_tmp)+1)
	#df_tmp.to_csv("sat-hp1@50T-01_04P.dat")
	sns.lineplot(x = range(len(sat_hp2[sat_hp2['path'] == '50T-[01,04]P'])), y = 'time', \
		data = sat_hp2[sat_hp2['path'] == '50T-[01,04]P'], ax = axes[4], marker = 's')
	df_tmp = pd.DataFrame(sat_hp2[sat_hp2['path'] == '50T-[01,04]P'])['time']
	df_tmp.index = range(1,len(df_tmp)+1)
	#df_tmp.to_csv("sat-hp2@50T-01_04P.dat")
	axes[4].set_yticks(np.arange(0, 9, 2))

	for i in range(5):
		axes[i].set_xlabel('#Instances solved')
		axes[i].set_ylabel('Runtime')

	plt.savefig("figure1.png")


	# table 1
	colIpHp1, colIpHp2, colSatHp1, colSatHp2 = [], [], [], []

	colIpHp1.append(table1(ip_hp1[ip_hp1['path'] == '10T-[01,04]P']))
	colIpHp1.append(table1(ip_hp1[ip_hp1['path'] == '10T-[07,10]P']))
	colIpHp1.append(table1(ip_hp1[ip_hp1['path'] == '20T-[01,04]P']))
	colIpHp1.append(table1(ip_hp1[ip_hp1['path'] == '20T-[07,10]P']))
	colIpHp1.append(table1(ip_hp1[ip_hp1['path'] == '50T-[01,04]P']))

	colIpHp2.append(table1(ip_hp2[ip_hp2['path'] == '10T-[01,04]P']))
	colIpHp2.append(table1(ip_hp2[ip_hp2['path'] == '10T-[07,10]P']))
	colIpHp2.append(table1(ip_hp2[ip_hp2['path'] == '20T-[01,04]P']))
	colIpHp2.append(table1(ip_hp2[ip_hp2['path'] == '20T-[07,10]P']))
	colIpHp2.append(table1(ip_hp2[ip_hp2['path'] == '50T-[01,04]P']))

	colSatHp1.append(table1(sat_hp1[sat_hp1['path'] == '10T-[01,04]P']))
	colSatHp1.append(table1(sat_hp1[sat_hp1['path'] == '10T-[07,10]P']))
	colSatHp1.append(table1(sat_hp1[sat_hp1['path'] == '20T-[01,04]P']))
	colSatHp1.append(table1(sat_hp1[sat_hp1['path'] == '20T-[07,10]P']))
	colSatHp1.append(table1(sat_hp1[sat_hp1['path'] == '50T-[01,04]P']))

	colSatHp2.append(table1(sat_hp2[sat_hp2['path'] == '10T-[01,04]P']))
	colSatHp2.append(table1(sat_hp2[sat_hp2['path'] == '10T-[07,10]P']))
	colSatHp2.append(table1(sat_hp2[sat_hp2['path'] == '20T-[01,04]P']))
	colSatHp2.append(table1(sat_hp2[sat_hp2['path'] == '20T-[07,10]P']))
	colSatHp2.append(table1(sat_hp2[sat_hp2['path'] == '50T-[01,04]P']))

	dfTable1 = pd.DataFrame([colIpHp1, colIpHp2, colSatHp1, colSatHp2], \
		index = ['ip-hp1', 'ip-hp2', 'sat-hp1', 'sat-hp2'], \
		columns = ['10T-[1,4]P', '10T-[7,10]P', '20T-[1,4]P', '20T-[7,10]P', '50T-[1,4]P']).T
	dfTable1.to_csv("table1.txt")

