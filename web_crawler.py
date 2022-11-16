import requests
import json
import csv
import time
import datetime
import os

intervalYear = []
intervalMonth = []
outPutFile = [0]*2
outPutWriter = [0]*2
className = []
companyName = []
companyCode = []

'''
#選擇要爬多久的資料
def SelectIntervalTime(intervalYear, intervalMonth):
    nowTime = datetime.datetime.now()
    for i in range(6):
        intervalMonth.append(nowTime.month - 1 - i)
    intervalMonth.reverse()
    for i in range(1):
        intervalYear.append(nowTime.year - i)
'''
        
#回傳平年或閏年的日曆
def CommonORLeapYear(year):
    commonYearCalender = {1:31, 2:28, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}
    leapYearCalender = {1:31, 2:29, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}
    #nowTime = datetime.datetime.now()
    if ((year%4 == 0 and year%100 != 0 ) or (year%400 == 0)):
        return leapYearCalender
    else:
       return commonYearCalender

#回傳動態的URL   
def DynamicURL(typeNumber, year, month , day):
    if(typeNumber <= 9):
        strClassCode = "0" + str(typeNumber)
    else:
        strClassCode = str(typeNumber)
    strYear = str(year)
    if(month <= 9):
        strMonth = "0"+str(month)
    else:
        strMonth = str(month)
    if(day <= 9):
        strDay = '0'+str(day)
    else:
        strDay = str(day)
    time.sleep(3)
    changeTime = int(time.time() * 1000)
    URL = "http://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&date=" + strYear + strMonth + strDay + "&type=" + strClassCode + "&_=" + str(changeTime)
    return URL

#判斷是否為假日
def NotSatSun(judgement):
    if(judgement == 'OK'):
        return True
    else:
        return False

#選擇各類別的n家公司    
def SelectClassCompany(outPutFile, className, companyName, companyCode, outPutWriter, py_dict):
    x = py_dict['title'].index('(')
    y = py_dict['title'].index(')')
    className.append(py_dict['title'][x+1:y])
    for i in range(len(outPutWriter)):
        companyName.append(py_dict['data1'][i][1])
        companyCode.append(py_dict['data1'][i][0])
    CreatClassFolder(className, companyName, companyCode)
    CreatCompanyFolder(className,companyName,companyCode)
    CreatCompanyFile(className, companyName, companyCode, outPutFile, outPutWriter, py_dict)

#建立票類別的資料夾    
def CreatClassFolder(className,companyName,companyCode):
    if(not os.path.exists("C:\\Users\\Peng\\Desktop\\畢業專題\\近兩年各類股票每日資訊\\"+className[len(className)-1])):
        os.makedirs("C:\\Users\\Peng\\Desktop\\畢業專題\\近兩年各類股票每日資訊\\"+className[len(className)-1])
    else: print('dir:%d already exist'%(className[len(className)-1]))
 
#建立公司資料夾    
def CreatCompanyFolder(className,companyName,companyCode):
    for i in range(len(outPutWriter)):
        if(not os.path.exists('C:\\Users\\Peng\\Desktop\\畢業專題\\近兩年各類股票每日資訊\\%s\\%s%s'
            %(className[len(className)-1], companyCode[len(companyCode)-2+i], companyName[len(companyName)-2+i]))):
            os.makedirs('C:\\Users\\Peng\\Desktop\\畢業專題\\近兩年各類股票每日資訊\\%s\\%s%s'
                %(className[len(className)-1], companyCode[len(companyCode)-2+i], companyName[len(companyName)-2+i]))
        else:
            print('dir: %d, %d already exist'%(companyCode[len(companyCode)-2+i], companyName[len(companyName)-2+i]))
    
    
#建議各個公司的csv檔       
def CreatCompanyFile(className, companyName, companyCode, outPutFile, outPutWriter, py_dict):
    count = 0
    for i in range(len(outPutWriter)):
        if(not os.path.isfile("C:\\Users\\Peng\\Desktop\\畢業專題\\近兩年各類股票每日資訊\\%s\\\%s%s\\%s%s.csv"
            %(className[len(className)-1], companyCode[len(companyCode)-2+i], companyName[len(companyName)-2+i], companyCode[len(companyCode)-2+i], companyName[len(companyName)-2+i]))):
            outPutFile[i] = open("C:\\Users\\Peng\\Desktop\\畢業專題\\近兩年各類股票每日資訊\\%s\\\%s%s\\%s%s.csv"
                %(className[len(className)-1], companyCode[len(companyCode)-2+i], companyName[len(companyName)-2+i], companyCode[len(companyCode)-2+i], companyName[len(companyName)-2+i]),'w',newline = '')
            outPutWriter[i] = csv.writer(outPutFile[i])
            if(count == 0):
                py_dict['fields1'].insert(0, "日期")
                outPutWriter[i].writerow(py_dict['fields1'])
                count += 1
            else:
                outPutWriter[i].writerow(py_dict['fields1'])
        else:
            print('file: %d, %d already exist'%(companyCode[len(companyCode)-2+i], companyName[len(companyName)-2+i]))
            
#寫進CSV檔
def WriteInCSV(outPutWriter, py_dict, companyName, companyCode):
    nowName = [companyName[len(companyName) - 2], companyName[len(companyName) - 1]]
    nowCode = [companyCode[len(companyCode) - 2], companyCode[len(companyCode) - 1]]
    for i in range(len(outPutWriter)):
        for j in range(len(py_dict)):
            if(nowName[i]==py_dict['data1'][j][1] and nowCode[i]==py_dict['data1'][j][0]):
                py_dict['data1'][j].insert(0, py_dict['date'])
                outPutWriter[i].writerow(py_dict['data1'][j])
                py_dict['data1'][j].pop(0)
                break
            if(nowCode[i] < py_dict['data1'][j][0]):
                break
#主程式
#SelectIntervalTime(intervalYear, intervalMonth)
intervalYear = [2016, 2017]
intervalMonth = list(range(1, 13))
for typeNumber in range(1, 32):
    count = 0
    for year in intervalYear:
        calender = CommonORLeapYear(year)
        for month in intervalMonth:
            for day in range(1, calender[month]+1):
                URL = DynamicURL(typeNumber, year, month , day)
                res = requests.get(URL, headers = {'User-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'})
                py_dict = json.loads(res.text)
                if(NotSatSun(py_dict['stat'])):
                    if(count == 0):
                        SelectClassCompany(outPutFile, className, companyName, companyCode, outPutWriter, py_dict)
                        WriteInCSV(outPutWriter, py_dict, companyName, companyCode)
                        count += 1
                    else:
                        WriteInCSV(outPutWriter, py_dict, companyName, companyCode)
    for end in range(len(outPutWriter)):
        outPutFile[end].close()