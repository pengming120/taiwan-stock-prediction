from sklearn.decomposition import PCA 
import pandas as pd
import numpy as np
from sklearn.svm import SVC
from sklearn import preprocessing
import csv
from collections import OrderedDict
import matplotlib.pyplot as plt


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
    all_class_dir = get_dir_from_txt('C:\\Users\\Peng\\Desktop\\畢業專題\\十年資料\\所有類型資料夾.txt')
    for category in all_class_dir:
        company_dir = get_dir_from_txt('C:\\Users\\Peng\\Desktop\\畢業專題\\十年資料\\' + category + '\\所有公司.txt')
        for company in company_dir:
            filePath = 'C:\\Users\\Peng\\Desktop\\畢業專題\\十年資料\\%s\\%s\\%s.csv'%(category, company, company)
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
        if((itemKeys[j] == '年月日') or (itemKeys[j] == '證券代號') or (itemKeys[j] == '證券名稱')
            or (itemKeys[j] == '漲跌(+/-)') or (row[itemKeys[j]] == '') or (row[itemKeys[j]] == '--') or (row[itemKeys[j]] == '-')):
            items[j].append(row[itemKeys[j]])
        else: items[j].append(float(row[itemKeys[j]].replace(',', ''))) #如果不是上面條件數字裡面不會有','就可以直接append

def get_discard_reserve_data(stock_data, company_keys):
    discard_reserve_data = OrderedDict({})
    for key in company_keys:
        discard_reserve_data[key] = []
        numberDays = len(stock_data[key]['年月日'])
        
        discard = 0
        while True:
            if(stock_data[key]['年月日'][discard][:4] == '2009'):
                discard = discard + 1
            else: break
        reserve = numberDays - discard
        
        discard_reserve_data[key].append(discard)
        discard_reserve_data[key].append(reserve)
    return discard_reserve_data


def get_feature(discard_reserve_data):
    feature = OrderedDict({})
    all_class_dir = get_dir_from_txt('C:\\Users\\Peng\\Desktop\\畢業專題\\十年資料\\所有類型資料夾.txt')
    for category in all_class_dir:
        company_dir = get_dir_from_txt('C:\\Users\\Peng\\Desktop\\畢業專題\\十年資料\\' + category + '\\所有公司.txt')
        for company in company_dir:
            discard = discard_reserve_data[company][0]
            #去掉2016的data
            filePath = 'C:\\Users\\Peng\\Desktop\\畢業專題\\十年資料\\%s\\%s\\%sfeature.csv'%(category, company, company)
            feature[company] = pd.read_csv(filePath, engine='python', usecols = range(1,7), skiprows = range(1, discard + 1 - 5))
    return feature

def predict(total_x, total_y):
    svm = SVC(kernel = 'rbf', probability = True, gamma = 'auto')    ####
    predict_y = np.array([])
    s = 10    #train:test =s-1:1
    testAmount = round(len(total_x)/s)    #這裡控制train:test比例
    for i in range(s):
        if(i == s-1):
            train_x = total_x[:(i*testAmount)]
            train_y = total_y[:(i*testAmount)]
            test_x = total_x[(i*testAmount):]
            svm.fit(train_x, train_y)
            predict_y = np.append(predict_y, svm.predict(test_x))
        else:
            train_x = np.delete(total_x, range((i*testAmount), (i*testAmount) + testAmount), axis = 0)
            train_y = np.delete(total_y, range((i*testAmount), (i*testAmount) + testAmount), axis = 0)
            test_x = total_x[(i*testAmount):(i*testAmount) + testAmount]
            svm.fit(train_x, train_y)
            predict_y = np.append(predict_y, svm.predict(test_x))
    return predict_y.astype(np.int16)


def x_axis(feature_pair):
    x = []
    feature_pair = np.array(feature_pair)
    for i in range(6):
        feature_pair[:,i] = preprocessing.scale(feature_pair[:,i])
    reserve_K = feature_pair[:,0]
    reserve_D = feature_pair[:,1]
    reserve_SMA10 = feature_pair[:,2]
    reserve_RSI = feature_pair[:,3]
    reserve_MACD = feature_pair[:,4]
    reserve_rise_fall = feature_pair[:,5]
    for i in range(5):
        x.append(reserve_rise_fall[4 - i:len(feature_pair) - i].reshape(-1, 1))
        x.append(reserve_K[4 - i:len(feature_pair) - i].reshape(-1, 1))
        x.append(reserve_D[4 - i:len(feature_pair) - i].reshape(-1, 1))
        x.append(reserve_SMA10[4 - i:len(feature_pair) - i].reshape(-1, 1))
        x.append(reserve_RSI[4 - i:len(feature_pair) - i].reshape(-1, 1))
        x.append(reserve_MACD[4 - i:len(feature_pair) - i].reshape(-1, 1))
    x = np.concatenate(x, axis = 1)
    return np.delete(x,len(x)-1, axis = 0)

def gen_mask(total_y):
    return (total_y >= 0.1) | (total_y <= -0.1)
     

def y_axis(rise_fall):
    total_y = np.array([])
    for i in range(len(rise_fall) - 5): total_y = np.append(total_y, sum(rise_fall[i + 1:i + 6]))
    return total_y

    #return preprocessing.scale(np.delete(rise_fall,[0,1,2,3],axis=0))
    #return np.delete(rise_fall,[0,1,2,3],axis=0)

def y_clf(total_y):
    y = total_y.copy()
    mini = min(y)
    divide = []
    for i in range(2000):
        if(sum(y <= (mini + i*0.05)) >= ((1/4)*len(y))):
            divide.append(mini + i*0.05)
            break
    divide.append(0)
    for i in range(2000):
        if(sum(y <= (mini + i*0.05)) >= ((3/4)*len(y))):
            divide.append(mini + i*0.05)
            break
    y[(total_y >= mini) & (total_y < divide[0])] = 1
    y[(total_y >= divide[0]) & (total_y < divide[1])] = 2
    y[(total_y >= divide[1]) & (total_y < divide[2])] = 3
    y[(total_y >= divide[2]) & (total_y <= max(y))] = 4
    y = y.astype(int)
    print(divide)
    return y

stock_data = read_all_data() #OrderedDict{'公司名稱':data, ...}
company_keys = list(stock_data.keys()) #['1101台泥', '1102亞泥', ...]


#算每個公司每年的資料筆數 => {'公司名稱':[2016年資料筆數, 2017年資料筆數]}
discard_reserve_data = get_discard_reserve_data(stock_data, company_keys) 

feature = get_feature(discard_reserve_data)

SVMclf = OrderedDict({})

predict_matrix = np.zeros((4, 4), dtype = np.int32)

df1 = pd.DataFrame(index = company_keys,
                   columns = ['class1 precision', 'class1 recall', 'class2 precision', 'class2 recall', 'class3 precision', 'class3 recall', 'class4 precision', 'class4 recall', ])

for key in company_keys:
    SVMclf[key] = []
    total_x = x_axis(feature[key].values)
    
    total_y = y_axis(np.array(feature[key]['一天漲跌(開盤價-收盤價)']))
    mask = gen_mask(total_y)
    
    total_y = total_y[mask]
    total_x = total_x[mask]
    
    y = y_clf(total_y)
    del total_y
    
    result = predict(total_x, y)
    
    df1.loc[key][0] = round(sum(np.logical_and(y == 1, result == 1)) / sum(result == 1), 3)
    df1.loc[key][1] = round(sum(np.logical_and(y == 1, result == 1)) / sum(y == 1), 3)
    df1.loc[key][2] = round(sum(np.logical_and(y == 2, result == 2)) / sum(result == 2), 3)
    df1.loc[key][3] = round(sum(np.logical_and(y == 2, result == 2)) / sum(y == 2), 3)
    df1.loc[key][4] = round(sum(np.logical_and(y == 3, result == 3)) / sum(result == 3), 3)
    df1.loc[key][5] = round(sum(np.logical_and(y == 3, result == 3)) / sum(y == 3), 3)
    df1.loc[key][6] = round(sum(np.logical_and(y == 4, result == 4)) / sum(result == 4), 3)
    df1.loc[key][7] = round(sum(np.logical_and(y == 4, result == 4)) / sum(y == 4), 3)
    
    
    for i in range(len(y)):
        predict_matrix[y[i] - 1][result[i] - 1] += 1
    
    
    correctPercentage = sum((result == y)) / len(y)
    print(correctPercentage)
    SVMclf[key].append(correctPercentage)    #[[每個x對應預測的y], 正確率]
    SVMclf[key].append(result)
    

#計算相關統計資料
df2 = pd.DataFrame(index = company_keys,
                  columns = ['K平均值', 'K標準差', 'D平均值', 'D標準差', 'SMA平均值', 'SMA標準差', 'RSI平均值', 'RSI標準差', 'MACD平均值', 'MACD標準差', '(一天漲跌)平均值', '(一天漲跌)標準差', ])
for key in company_keys:
    for i in range(6):
        df2.loc[key][i*2] = round(feature[key].values[:,i].mean(), 3)
        df2.loc[key][i*2+1] = round(feature[key].values[:,i].std(), 3)
df2.index.name = ''

output = pd.concat([df1, df2], axis = 1)

output.to_csv('C:\\Users\\Peng\\Desktop\\相關統計資料.csv', encoding='utf_8_sig')