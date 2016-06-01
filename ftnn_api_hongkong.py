#!/usr/bin/python2.6
# -*- coding: utf-8 -*-
'''
Created on 2015年8月26日
@author: futu
'''

#如果这个分钟内没有一笔成交，这个是

import socket
import json
import string
import sys
from time import sleep
import time
import os
import pandas as pd

def MA(MA_x,Latest_Value):
    global file_souji_fengzhong
    df_tmp=pd.read_csv(file_souji_fengzhong,index_col=0)
    value_tmp=(df_tmp.ix[:,3].tail(MA_x-1).sum()+Latest_Value)/MA_x
    return value_tmp

# 上一分钟信息
LastMinute=None
file_souji_tmp="c:\\9\\ftnn_souji_700.csv"
file_souji_all="c:\\9\\ftnn_souji_all_700.csv"
file_souji_fengzhong="c:\\9\\ftnn_souji_700_fengzhong.csv"

df_4=pd.DataFrame()
df_5=pd.DataFrame()
df_6=pd.DataFrame()

#futnn plubin会开启本地监听服务端
# 请求及发送数据都是jason格式, 具体详见插件的协议文档
host="localhost"
port=11111


local_date=time.strftime('%Y-%m-%d',time.localtime(time.time()-24*60*60))

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect((host,port))

#需要确认电脑时区是香港时区
while (time.localtime(time.time()-24*60*60)<time.strptime(local_date+" "+"12:00:01", "%Y-%m-%d %H:%M:%S") \
        and time.localtime(time.time()-24*60*60)>time.strptime(local_date+" "+"09:30:00", "%Y-%m-%d %H:%M:%S")) \
    or ( time.localtime(time.time()-24*60*60)>time.strptime(local_date+" "+"13:00:00", "%Y-%m-%d %H:%M:%S") and\
        time.localtime(time.time()-24*60*60)<time.strptime(local_date+" "+"16:00:01", "%Y-%m-%d %H:%M:%S") ):
    #发送报价请求，Market为2表示是美股
    req = {'Protocol':'1001', 'ReqParam':{'Market':'1','StockCode':'00700'},'Version':'1'}
    #req = {'Protocol':'1001', 'ReqParam':{'Market':'1','StockCode':'00700'},'Version':'1'}
    #req = {'Protocol':'1001', 'ReqParam':{'Market':'1','StockCode':'01585'},'Version':'1'}
    str_1 = json.dumps(req) + "\n"
    print str_1
    s.send(str_1)
    rsp = ""
    while True:
        buf = s.recv(1024)
        rsp = rsp + buf
        #找到"\n"就认为结束了
        try:
            rsp.index('\n')
            break;
        except Exception, e:
            print "recving..."
    print rsp

    rsp_current_price_str=rsp.split(',')[4]
    current_price=rsp_current_price_str.split('"')[3]

    #输出的时间是按秒计算的，现在距离0点0分0秒多长时间
    rsp_current_time_str=rsp.split(',')[11]
    current_time=rsp_current_time_str.split('"')[3]
    current_hour=int(current_time)/3600
    current_minute=(int(current_time)-current_hour*3600)/60
    current_second=int(current_time)-current_hour*3600-current_minute*60

    actual_minute=time.strftime("%M",time.localtime(time.time()-24*60*60))

    print current_hour
    print current_minute
    print current_second
    print current_price
    print "------"
    print actual_minute

    if actual_minute==LastMinute or LastMinute==None:
        if os.path.exists(file_souji_tmp)==False:
            f=open(file_souji_tmp,"w")
            print>>f,"Date,Price"
            f.close()

        if os.path.exists(file_souji_all)==False:
            f=open(file_souji_all,"w")
            print>>f,"Date,Price"
            f.close()

        if os.path.exists(file_souji_fengzhong)==False:
            f=open(file_souji_fengzhong,"w")
            print>>f," ,open,high,low,close,MA5,MA10,MA20,MA30,MA60,MA120"
            f.close()

        f=open(file_souji_tmp,"a")
        print>>f,local_date+" "+str(current_hour)+":"+str(current_minute)+":"+str(current_second)+","+str(current_price)
        f.close()

    else:
        df_1=pd.read_csv(file_souji_tmp)
        df_4=pd.read_csv(file_souji_all)
        df_4=df_4.append(df_1,ignore_index=True)
        df_4.to_csv(file_souji_all,index=False)

        df_1.index=pd.tseries.index.DatetimeIndex(df_1.ix[:,0])
        df_2=df_1.ix[:,1]
        df_3=df_2.resample('1min',how='ohlc')
        print df_3.ix[0]
        print "------"
        print df_3
        print "------"
        print actual_minute

        '''
        df_5=pd.read_csv(file_souji_fengzhong,index_col=0)
        df_5=df_5.append(df_3.ix[0])
        MA5_tmp=MA(5,df_3.ix[0,3])
        MA10_tmp=MA(10,df_3.ix[0,3])
        MA20_tmp=MA(20,df_3.ix[0,3])
        MA30_tmp=MA(30,df_3.ix[0,3])
        MA60_tmp=MA(60,df_3.ix[0,3])
        MA120_tmp=MA(120,df_3.ix[0,3])
        df_5.to_csv(file_souji_fengzhong)
        '''

        df_5=pd.read_csv(file_souji_fengzhong,index_col=0)
        #df_tmp=df_3.ix[0]


        if len(df_5)==0 or df_3.head(1).index!=pd.tseries.index.DatetimeIndex(df_5.tail(1).index):
            df_tmp=df_3.head(1)
        else:
            df_tmp=df_3.tail(1)

        #df_tmp=df_3.tail(1)

        MA5_tmp=MA(5,df_tmp.ix[0,3])
        MA10_tmp=MA(10,df_tmp.ix[0,3])
        MA20_tmp=MA(20,df_tmp.ix[0,3])
        MA30_tmp=MA(30,df_tmp.ix[0,3])
        MA60_tmp=MA(60,df_tmp.ix[0,3])
        MA120_tmp=MA(120,df_tmp.ix[0,3])

        df_tmp['MA5']=MA5_tmp
        df_tmp['MA10']=MA10_tmp
        df_tmp['MA20']=MA20_tmp
        df_tmp['MA30']=MA30_tmp
        df_tmp['MA60']=MA60_tmp
        df_tmp['MA120']=MA120_tmp
        df_5=df_5.append(df_tmp)

        df_5.to_csv(file_souji_fengzhong)

        os.remove(file_souji_tmp)
        #caculate_zhibiao(df_3.ix[0,0],)
        #caculate_MACD(df_3)

    LastMinute=actual_minute
    sleep(0.5)
