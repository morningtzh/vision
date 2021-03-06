#!/usr/bin/python -u
# -*- coding: UTF-8 -*- 
# Author: Arnold Huang
# Date: 9/1/2017
# Version History: 9/1/2017  Initial version
#                  9/4/2017  Update according to the Jind's comments except NAV
#                  9/21/2017 Update the script to add nav.
# E-mail: fugaohx@163.com
# Weixin: fugaohx
# Comment:

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import datetime
import re
import urllib.request, urllib.error, urllib.parse
#import lxml.html
#Croc
import requests
import simplejson
import sys
#import os
import hashlib
import random
#
def get_x_sign(url, len = 32):
    random_value = random.sample(["0","1","2","3","4","5","6","7","8","9"], 1)
    curtime =  str(time.time()).replace('.', '') + random_value[0]
    target = str("%f")%(float(curtime)*1.01)
    target = target[0:13]
    sha256 = hashlib.sha256()
    sha256.update(target.encode('utf-8'))
    target_sha256 = sha256.hexdigest().upper()
    x_sign = curtime + target_sha256[0:len]
    #
    #time.sleep(0.01)
    #newtime =  str(time.time()).replace('.', '') + random_value[0]
    n = str(random.random()) + str(random.randint(1000,9999))
    userAgent = "5011866453736630323913253736"
    target = str(n) + curtime + url + userAgent
    sha256.update(target.encode('utf-8'))
    target_sha256 = sha256.hexdigest().upper()
    x_request_id = target_sha256[-20:]
    return x_sign, x_request_id
    
#common download function that download common html
def common_download(url, retry=10):
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)' 
    request = urllib.request.Request(url, user_agent)
    def get_html():
        response = urllib.request.urlopen(request)
        time.sleep(0.5)
        html = response.read()
        return html
    for try_times in range(retry):
        try:
            html = get_html()
            break
        except:
            if try_times < retry - 1:
                continue
            else:
                print("Network error!")
                sys.exit()
    return html
        
#get all fund ids
def get_funds(retry = 10):
    headers = {"Accept" : "application/json",
        "Accept-Encoding" : "gzip, deflate, br",
        "Accept-Language" : "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
        "Connection" : "keep-alive",
        "Host" : "qieman.com",
        "Referer" : "https://qieman.com/longwin/index",
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36",
        "x-aid" : "GA1.2.999152452.1516692587",
        "x-request-id" : "",
        "x-sign" : "",
        }
    funds_pattern = re.compile('"fund":({.*?})')
    while retry > 0:
        retry -= 1
        headers["x-sign"], headers["x-request-id"] = get_x_sign(headers["Referer"])
        return_data = requests.get("https://qieman.com/pmdj/v2/long-win/plan", headers=headers)
        fundlists = funds_pattern.findall(return_data.text)
        funds = []
        for fund in fundlists:
            fund = simplejson.loads(fund)
            if len(fund['fundCode']) == 6: 
                funds.append(fund['fundCode'])
        if len(funds) == 0 and retry !=0:
            time.sleep(1)
            continue
        elif len(funds) == 0 and retry == 0:
            print("无法获取基金列表，请重新运行程序！")
            sys.exit()
        else:
            break
    funds.remove('001061')
    funds.remove('000614')
    funds.remove('501018')
    return funds

def cal_time(date1,date2):
    date1 = time.strptime(date1,"%Y-%m-%d %H:%M:%S")
    date2 = time.strptime(date2,"%Y-%m-%d %H:%M:%S")
    date1 = datetime.datetime(date1[0], date1[1], date1[2], date1[3], date1[4], date1[5])
    date2 = datetime.datetime(date2[0], date2[1], date2[2], date2[3], date2[4], date2[5])
    return (date2-date1).days

def get_fhsp_records(fundid, sdate):
    html = common_download("http://fund.eastmoney.com/f10/fhsp_"+fundid+".html")
    text = "".join(html.split())
    fhsp_pattern = re.compile(r"<td>(\d{4}-\d{2}-\d{2})</td><td>每份派现金(\d*\.\d{4})元</td>")
    tmp = fhsp_pattern.findall(text)
    retval=[]
    for i in range(0, len(tmp)):
        delta = cal_time(sdate, tmp[i][0]+" 15:00:00" )
        if delta > 0 :
            retval.append(tmp[i])
    
    retval.reverse()
    return retval

def get_history_price_by_fund(fundid, starttime):
    enddate = time.strftime('%Y-%m-%d',  time.localtime(time.time()))
    startdate = starttime.split(" ")[0]
    delta_days = cal_time(startdate+" 00:00:00", enddate+" 00:00:00")
    html = common_download("http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code="+fundid+"&page=1&per="+str(delta_days)+"&sdate=" + startdate+ "&edate=" + enddate)
    html = html.split("<tr>")
    history = []
    history_pattern = re.compile(r"<td>(\d{4}-\d{2}-\d{2})</td><td class='tor bold'>(\d*.\d{4})</td>.*")
    for i in range(2, len(html)):
        history.append( history_pattern.findall(html[i]) )
    return history

#get the price that ChinaETF bought
def get_raw_price(fundid):
    headers = {"Accept" : "application/json",
        "Accept-Encoding" : "gzip, deflate, br",
        "Accept-Language" : "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "Connection" : "keep-alive",
        "Host" : "qieman.com",
        "Referer" : "",
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36",
        "x-aid" : "GA1.2.999152452.1516692587",
        "x-request-id" : "",
        "x-sign" : ""}
    headers["Referer"] = "https://qieman.com/longwin/funds/" + fundid
    headers["x-sign"], headers["x-request-id"] = get_x_sign(headers["Referer"])
       
    return_data = requests.get("https://qieman.com/pmdj/v2/long-win/plan/history?fundCode=%s" %(fundid), headers=headers)  
    price_pattern = re.compile('"fund":\{(.*?0)\}') 
    datalists = price_pattern.findall(return_data.text)
    buyrecord = []
    sellrecord = []
    for datalist in datalists:
        mydata = []
        datalist = '{' + datalist.replace('}','') + '}'
        datalist = simplejson.loads(datalist)
        if datalist["orderCode"] == '022' and datalist["nav"] is not None:
            mynavDate = time.strftime("%Y-%m-%d", time.localtime(datalist["adjustTxnDate"]/1000))
            mydata.append(mynavDate)
            mydata.append(datalist["nav"])
            mydata.append(datalist["tradeUnit"])
            buyrecord.append(mydata)
        elif datalist["orderCode"] == '024':
            sellrecord.append(datalist["tradeUnit"])
    prices = [] 
    if len(buyrecord) != 0:
        firstbuydate = str(buyrecord[-1][0])+" 15:00:00"
        history = get_history_price_by_fund(fundid, firstbuydate)
        fhs = get_fhsp_records(fundid,firstbuydate)         
        for item in buyrecord:
            buydate = str(item[0])
            buyprice = float(item[1])
            rate = []
            for fh in fhs:
                fhdate = str(fh[0])
                fhmoney = float(fh[1])   

                #if fh date is before buy date, not to calt nav rate
                if cal_time(buydate+" 15:00:00", fhdate+" 15:00:00") < 0  :
                    continue

                #to find the net on that day
                for net in history:
                    #find it!
                    if net[0][0] == fhdate:
                        net_that_day = float(net[0][1])
                        rate.append((net_that_day + fhmoney)/net_that_day)
                        break
            navrate=1
            if len(fhs)>0:
                for r in rate:
                    navrate = navrate * r
            prices.append(("%.4f" % buyprice, "%.4f" % navrate)) 

        prices.sort()
       
        #sellrecord = re.findall(unicode(r"卖出(\d*)份", 'utf8'),text)
        sellrecordcount = len(sellrecord)
        sellcount = 0
        if(sellrecordcount != 0):
            for i in sellrecord:
                sellcount = sellcount+int(i)
            for i in range(1, sellcount+1):
                prices.pop()
        return prices
    else:
        return False

#get current price from eastmoney
def get_current_price(fundid, retry = 10):
    '''
    html = common_download("http://gu.qq.com/jj"+fundid+"?pgv_ref=fi_smartbox&_ver=2.0")
    tree = lxml.html.fromstring(html)
    c_price_pattern = re.compile(r"单位净值：<span>(\d*\.\d{4})")
    gu_price_pattern = re.compile("最新估值")
    if len(gu_price_pattern.findall(html))>0:
        span = tree.cssselect('span#main5')[0]
        fundprice = span.text_content()
        if fundprice == "--": 
            span = tree.cssselect('span#main0')[0]
            fundprice = span.text_content()
    else:
        span = c_price_pattern.findall(html)
        if len(span) > 0:
           fundprice = "".join(span[0])
        else:
           fundprice = "--"
    
    span = tree.cssselect('span.col_1')[0]
    fundname = span.text_content()
    '''
    headers = {
        "Accept" : "*/*", 
        "Accept-Encoding" : "gzip, deflate",
        "Accept-Language" : "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
        "Cache-Control" : "no-cache",
        "Connection" : "keep-alive",
        "Host" : "fundgz.1234567.com.cn",
        "Pragma" : "no-cache",
        "Referer" : "",
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
    }
    for retry_times in range(0, retry+1):
        try:
            random_value = random.sample(["0","1","2","3","4","5","6","7","8","9"], 1)
            curtime =  str(time.time()).replace('.', '') + random_value[0]    
            return_data = requests.get("http://fundgz.1234567.com.cn/js/%s.js?rt=%s" %(fundid, curtime), headers=headers)
            raw_data = re.findall('jsonpgz\((.*)\)', return_data.text)
            if len(raw_data) != 0: 
                break
            else:
                continue
        except:
            if retry_times < retry:
                time.sleep(1)
                continue
            else:
                print("\x1b[2J")
                print("Network error!")
                sys.exit() 
    data = simplejson.loads(raw_data[0])
    '''
    data = {u'fundcode': u'000478', 
             u'name': u'\\u5efa\\u4fe1\\u4e2d\\u8bc1500\\u6307\\u6570\\u589e\\u5f3a', #名称
             u'dwjz': u'2.4543', #当前净值
             u'rzzl': u'-1.0403', #当前增长率
             u'gsz': u'2.4611', #估算净值
             u'gszzl': u'0.14', #估算增长率
             u'jzrq': u'2017-11-01', #净值日期
             u'gztime': u'2017-11-02 14:52' #估值时间
    }
    '''
    #fundname = data['name']
    #fundprice = data['gsz']
    #return fundname, fundprice
    return data['name'], data['gsz']


#analyze all fund price to give suggestion
def find_all_funds_prices(retrytimes=3):
    qieman_funds = get_funds()
    prices = []
    suggestionAll = ""
    today_nav = 0;
    def fund_analyst():
        suggestion = ""
 
        for fundid in qieman_funds:
            #fundid = "".join(fund)
            prices_and_rate = get_raw_price(fundid)
            if prices_and_rate is not False:
                qieman_funds.remove(fundid)
                name, current_price = get_current_price(fundid)
                print(("\n正在分析基金(%s)%s..." % (fundid, name)))
                eda_prices=[]
                if(current_price != "--"):
                    count = 0
                    price_in_history = []
                    for item in prices_and_rate:
                        price = float(item[0])
                        rate = float(item[1])
                        
                        #########
                        eda_prices.append(price)
                        ########
                        todaynav = float(current_price) * rate 
                        if todaynav < price :
                            print(("现 %s 复权价格%.4f低于历史购入复权净值: %.4f" % (name, todaynav, price) ))
                            count = count+1
                    ####
                    if ( len(eda_prices) > 0 ): 
                        min_price = min(eda_prices)
                        max_price = max(eda_prices)
                        max_to_min = max_price / min_price
                        print(("最高最低价格比值为%.2f : 1" % max_to_min ))                    
                        if ( max_to_min <  1.0100   ):
                           print("该品种适用于梭哈策略")
                     ####
                    def average(seq): 
                        return float(sum(seq)) / len(seq)
                    if (len(eda_prices)>0):
                        if ( current_price < average(eda_prices)  ):
                            suggestion += ("梭哈：(%s) %s %d份\n" % (fundid, name, len(eda_prices) ))
                        else:
                            if(count>0):
                                suggestion += ("空仓补仓：(%s) %s %d份\n" % (fundid, name, count))
        return suggestion
    suggestionAll = fund_analyst()
    retry = 0
    while retry < retrytimes:
        if len(qieman_funds) != 0:
            suggestionAll = suggestionAll + fund_analyst()
            retry += 1
        else:
            break
    if len(qieman_funds) != 0:
        print("因数据异常,以下基金未做分析，如有需要，请重新运行本程序：")
        for fundid in qieman_funds:
            #fundid = "".join(fund)
            name, current_price = get_current_price(fundid)
            print("(%s) %s" %(fundid, name))
              
    print("================================================\n")
    print("\n注意\n    1. 以下建议只做参考，作者Arnold Huang不为任何后果负责!!!")
    print("    2. 本程序仅提供基于空仓情况下的投资建议，已持仓部分基金的同学请检查持仓情况后做相应操作。")
    print("    3. 此程序的输出只作为参考，QDII指数基金有可能覆盖不全的情况.")
    print("    4. 投资有风险，买基需谨慎!!!\n")
    print(suggestionAll)
    print("================================================")


time_start = time.time()
find_all_funds_prices(10)
time_end = time.time()
print("运行时间： %.2fsec" %(time_end - time_start))
