import numpy as np
import csv
from collections import OrderedDict
import os
from scipy import stats


#return a list
def get_dir_from_txt(path):
    F = open(path,'r')
    dir_name = []
    while True:
        line = F.readline()
        if not line: break
        dir_name.append(line.split('\n')[0])
    return dir_name

def read_all_data():
    stock_data = OrderedDict({})
    all_class_dir = get_dir_from_txt('C:\\Users\\Peng\\Desktop\\畢業專題\\測試資料\\所有類型資料夾.txt')
    for category in all_class_dir:
        company_dir = get_dir_from_txt('C:\\Users\\Peng\\Desktop\\畢業專題\\測試資料\\' + category + '\\所有公司.txt')
        for company in company_dir:
            filePath = 'C:\\Users\\Peng\\Desktop\\畢業專題\\測試資料\\%s\\%s\\%s.csv'%(category, company, company)
            inputFile = open(filePath, newline='', encoding = 'utf-8')
            stock_data[company] = get_stock_data(inputFile)
    return stock_data
            
def get_stock_data(inputFile):
    #沒有開盤價就直接不讀取該天所有資料
    oneData = OrderedDict({})
    rows = csv.DictReader(inputFile)
    first = True
    itemKeys = []
    items = []
    for row in rows:
        if(first):
            itemKeys = list(row.keys())
            for i in itemKeys: items.append([])
            first = False
        if(row['開盤價'] != '-'): charAdjust(itemKeys, items, row)
    for i in range(len(itemKeys)): oneData[itemKeys[i]] = np.array(items[i])   
    return oneData

def charAdjust(itemKeys, items, row):
    for j in range(len(itemKeys)):
        if((itemKeys[j] == '?年月日') or (itemKeys[j] == '證券代號') or (itemKeys[j] == '證券名稱')
            or (itemKeys[j] == '漲跌(+/-)') or (row[itemKeys[j]] == '') or (row[itemKeys[j]] == '--') or (row[itemKeys[j]] == '-')):
            items[j].append(row[itemKeys[j]])
        else: items[j].append(float(row[itemKeys[j]].replace(',', ''))) #如果不是上面條件數字裡面不會有','就可以直接append
'''
def get_each_year_data(stock_data, company_keys):
    each_year_data = OrderedDict({})
    for key in company_keys:
        each_year_data[key] = []
        numberDays = len(stock_data[key]['?年月日'])
        if(numberDays%2 == 0): timesLimit = numberDays//2 - 1    
        else: timesLimit = numberDays//2
        if(stock_data[key]['?年月日'][numberDays//2][:4] == '2016'):
            for j in range(timesLimit):    #設定最多只會檢查這麼多次(從中間開始檢查)
                if(stock_data[key]['?年月日'][numberDays//2 + (j+1)][:4] == '2017'):
                    each_year_data[key].append(numberDays//2 + (j+1))#2016的天數
                    each_year_data[key].append(numberDays - (numberDays//2 + (j+1)))#2017的天數
                    break
        elif(stock_data[key]['?年月日'][numberDays//2][:4] == '2017'):
            for j in range(timesLimit):
                if(stock_data[key]['?年月日'][numberDays//2 - (j+1)][:4] == '2016'):
                    each_year_data[key].append(numberDays//2 - j)#2016的天數
                    each_year_data[key].append(numberDays - (numberDays//2 - j))#2017的天數
                    break
    return each_year_data
'''
def get_discard_reserve_data(stock_data, company_keys):
    discard_reserve_data = OrderedDict({})
    for key in company_keys:
        discard_reserve_data[key] = []
        numberDays = len(stock_data[key]['?年月日'])
        
        discard = 0
        while True:
            if(stock_data[key]['?年月日'][discard][:4] == '2009'):
                discard = discard + 1
            else: break
        reserve = numberDays - discard
        
        discard_reserve_data[key].append(discard)
        discard_reserve_data[key].append(reserve)
    return discard_reserve_data


def get_KD(stock_data, company_keys):
    KD = OrderedDict({})
    for key in company_keys:
        KD[key] = {}
        RSV = get_RSV(key, stock_data)
        K = get_K(key, stock_data, RSV)
        D = get_D(key, stock_data, K)
        KD[key]['RSV'] = RSV
        KD[key]['K'] = K
        KD[key]['D'] = D
    return KD

def get_RSV(key, stock_data):
    nineDayLowest = np.array([False] * 8)
    nineDayHighest = np.array([False] * 8)
    RSV = np.array([False] * 8)
    for i in range(8, len(stock_data[key]['?年月日'])):
        nineDayLowest = np.append(nineDayLowest, min(stock_data[key]['最低價'][i - 8:i + 1]))
        nineDayHighest = np.append(nineDayHighest, max(stock_data[key]['最高價'][i - 8:i + 1]))
    RSV = np.append(RSV, ((stock_data[key]['收盤價'][8:] - nineDayLowest[8:]) / (nineDayHighest[8:] - nineDayLowest[8:]))*100)
    return RSV

def get_K(key, stock_data, RSV):
    K = np.array([False] * 7 + [50])
    for i in range(8, len(stock_data[key]['?年月日'])):
        todayK = (2/3.) * K[i-1] + (1/3.) * RSV[i]
        K = np.append(K, todayK)
    return K
        
def get_D(key, stock_data, K):
    D = np.array([False] * 7 + [50])
    for i in range(8, len(stock_data[key]['?年月日'])):
        todayD = (2/3.) * D[i-1] + (1/3.) * K[i]
        D = np.append(D, todayD)
    return D
'''        
def PrintMaxMinKDToCSV(company_keys):
    FKMaxMin = open('C:\\Users\\Peng\\Desktop\\畢業專題\\十年資料\\KMaxMin.csv', 'w', newline = '')
    FDMaxMin = open('C:\\Users\\Peng\\Desktop\\畢業專題\\十年資料\\DMaxMin.csv', 'w', newline = '')
    for i in range(len(company_keys)):
        writerK = csv.writer(FKMaxMin)
        writerD = csv.writer(FDMaxMin)
        MaxK = max(KD[company_keys[i]]['K'][7:])
        MaxD = max(KD[company_keys[i]]['D'][7:])
        miniK = min(KD[company_keys[i]]['K'][7:])
        miniD = min(KD[company_keys[i]]['D'][7:])
        writerK.writerow([MaxK, miniK])
        writerD.writerow([MaxD, miniD])
    FKMaxMin.close()
    FDMaxMin.close()
'''

def get_SMA(stock_data, company_keys, t):
    SMAx = OrderedDict({})
    for key in company_keys:
        SMAx[key] = np.array([False] * (t - 1))
        for j in range((t - 1), len(stock_data[key]['?年月日'])):
            SMAx[key] = np.append(SMAx[key], stock_data[key]['收盤價'][j - (t - 1):j + 1].sum() / float(t))
    return SMAx
                
def get_RSI(stock_data, company_keys):
    RSI = OrderedDict({})
    for key in company_keys:
        RSI[key] = np.array([False] * 9)
        for j in range(9, len(stock_data[key]['?年月日'])):
            rs = get_RS(stock_data[key], j)
            if(rs == 'infinity'):
                rsi = 100
                RSI[key] = np.append(RSI[key], rsi)
            else:
                rsi = 100 * (rs / float((1 + rs)))
                RSI[key] = np.append(RSI[key], rsi)
    return RSI
                
def get_RS(oneData, day):
    rise = float(0)
    fall = float(0)
    for i in range(9):
        if(oneData['收盤價'][i + (day - 8)] - oneData['收盤價'][i + (day - 9)] > 0):
            rise += (oneData['收盤價'][i + (day - 8)] - oneData['收盤價'][i + (day - 9)])
        elif(oneData['收盤價'][i + (day - 8)] - oneData['收盤價'][i + (day - 9)] < 0):
            fall += abs(oneData['收盤價'][i + (day - 8)] - oneData['收盤價'][i + (day - 9)])
    if((fall/9.) == 0):
        return 'infinity'
    else:
        return ((rise/9.) / (fall/9.))
                
def get_MACD(stock_data, company_keys):
    MACD = OrderedDict({})
    EMA12 = OrderedDict({})
    EMA26 = OrderedDict({})
    DIFF = OrderedDict({})
    for key in company_keys:
        #P = priceDemand(stock_data[key])
        EMA12[key] = get_EMAx(stock_data[key]['收盤價'], 12)
        EMA26[key] = get_EMAx(stock_data[key]['收盤價'], 26)
        #EMA12[key] = get_EMAx(P, 12)    priceDemand
        #EMA26[key] = get_EMAx(P, 26)    priceDemand
        DIFF[key] = np.array([False] * 25)
        DIFF[key] = np.append(DIFF[key], EMA12[key][25:] - EMA26[key][25:])
        MACD[key] = get_DIFFEMA(DIFF[key], 9)
    return MACD
'''    
def priceDemand(oneData):
    x = np.array([])
    for i in range(len(oneData['?年月日'])):
        x = np.append(x, (oneData['最高價'][i] + oneData['最低價'][i] + 2*oneData['收盤價'][i])/4.)
    return x
'''

def get_EMAx(x, t):
    oneEMA = np.array([False] * (t - 1))
    oneEMA = np.append(oneEMA, sum(x[:t])/float(t))
    for i in range(t, len(x)):
        value = oneEMA[i - 1] + (2/float(t+1)) * (x[i] - oneEMA[i - 1])
        oneEMA = np.append(oneEMA, value)
    return oneEMA

def get_DIFFEMA(x,t):
    oneEMA = np.array([False] * 33)
    oneEMA = np.append(oneEMA, sum(x[25:34])/9.)
    for i in range((t+25), len(x)):
        value = oneEMA[i - 1] + (2/float(t+1)) * (x[i] - oneEMA[i - 1])
        oneEMA = np.append(oneEMA, value)
    return oneEMA

def get_rise_fall(stock_data, company_keys, each_year_data):
    rise_fall = OrderedDict({})
    for key in company_keys:
        rise_fall[key] = (stock_data[key]['收盤價'] - stock_data[key]['開盤價'])
    return rise_fall
    
def write_feature_in_csv(stock_data, KD, SMA10, RSI, MACD, rise_fall):
    all_class_dir = get_dir_from_txt('C:\\Users\\Peng\\Desktop\\畢業專題\\測試資料\\所有類型資料夾.txt')
    for category in all_class_dir:
        company_dir = get_dir_from_txt('C:\\Users\\Peng\\Desktop\\畢業專題\\測試資料\\' + category + '\\所有公司.txt')
        for company in company_dir:
            feature_file = open('C:\\Users\\Peng\\Desktop\\畢業專題\\測試資料\\' + category + '\\'+ company +'\\' + company + 'feature.csv', 'w', newline = '')
            feature_file = csv.writer(feature_file)
            feature_file.writerow(['年月日', 'K', 'D', 'SMA10', 'RSI', 'MACD', '一天漲跌(開盤價-收盤價)'])
            feature_pair = get_feature_pair(company, stock_data, KD, SMA10, RSI, MACD, rise_fall)
            for i in feature_pair: feature_file.writerow(i)
                    
def get_feature_pair(key, stock_data, KD, SMA10, RSI, MACD, rise_fall):
    x = []
    x.append(stock_data[key]['?年月日'].reshape(-1, 1))
    x.append(KD[key]['K'].reshape(-1, 1))
    x.append(KD[key]['D'].reshape(-1, 1))
    x.append(SMA10[key].reshape(-1, 1))
    x.append(RSI[key].reshape(-1, 1))
    x.append(MACD[key].reshape(-1, 1))
    x.append(rise_fall[key].reshape(-1, 1))
    return np.concatenate(x, axis = 1)
    
def print_ttest(company_keys, each_year_data, KD, SMA10, RSI, MACD, rise_fall):
    a = []
    b = []
    for key in company_keys:
        discard = each_year_data[key][0]
        reserve = each_year_data[key][1]
        for i in range(reserve - 1):
            if(rise_fall[key][i + discard + 1] > 0):
                a.append(MACD[key][i + discard])
            else:
                b.append(MACD[key][i + discard])
    print(stats.ttest_ind(a, b))
    x = 1
     
    
#讀檔
stock_data = read_all_data() #OrderedDict{'公司名稱':data, ...}
company_keys = list(stock_data.keys()) #['1101台泥', '1102亞泥', ...]

#算每個公司每年的資料筆數 => {'公司名稱':[2016年資料筆數, 2017年資料筆數]}
discard_reserve_data = get_discard_reserve_data(stock_data, company_keys) 

#KD => {'公司名稱':{'K':data, 'D':data}}
KD = get_KD(stock_data, company_keys)

#簡單均線 => {'公司名稱':data}
SMA10 = get_SMA(stock_data, company_keys, 10)

#RSI => {'公司名稱':data}
RSI = get_RSI(stock_data, company_keys)

#MACD => {'公司名稱':data}
MACD = get_MACD(stock_data, company_keys)

#每天的漲跌 => {'公司名稱':data}
rise_fall = get_rise_fall(stock_data, company_keys, discard_reserve_data)

#寫feature進csv檔案
write_feature_in_csv(stock_data, KD, SMA10, RSI, MACD, rise_fall)

#print_ttest(company_keys, discard_reserve_data, KD, SMA10, RSI, MACD, rise_fall)