#!/usr/bin/env python
# -*- coding: utf-8 -*-
#



import requests
import jsonpath
import json
import re
from time import sleep
import pymysql
import threading
from time import ctime
import csv
# import ippool



class MyThread(threading.Thread):
    def __init__(self,key,first,end,space):
        threading.Thread.__init__(self)
        self.key = key
        self.first = first
        self.end = end
        self.space = space

    def run(self):
        self.search(self.key,self.first,self.end,self.space)


    # 爬取数据
    def search(self,key,first,end,space):
        url = "https://s.taobao.com/search"
        header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0"}
        regex = "g_page_config = (.*?\}\});"
        # q=ippool.ippools()

        # while(len(q)>0):
        #     proxies=q.pop()
        #     print(proxies)


        for i in range((int(first)-1)*44, end*44, space):
            d = {"q": key, "bcoffset": "4", "ntoffset": "4", "p4ppushleft": "1%2C48", "s": i}

            try:
                print("开始爬取")
                data = requests.get(url, params=d, headers=header,timeout=2)

                dt = re.findall(regex, data.text)
                try:
                    js = json.loads(dt[0])
                    name = jsonpath.jsonpath(js, "$..raw_title")
                    nid = jsonpath.jsonpath(js, "$..nid")
                    price = jsonpath.jsonpath(js, "$..view_price")
                    comment = jsonpath.jsonpath(js, "$..comment_count")
                    is_tm = jsonpath.jsonpath(js, "$..isTmall")

                    links = self.deal_links(is_tm, nid)

                    self.save_datas(nid, name, links,price,comment, self.key)
                except Exception as e:
                    with open("log.txt","a")as f:
                        f.wrtie(e)
                        f.wrtie(data.url)
                        f.wrtie(text)
                    continue
            except Exception as e:
                with open("log.txt", "a")as f:
                    f.wrtie(e)
                    f.wrtie(data.url)
                    f.wrtie(text)
                continue

    # 对商品详情页链接进行处理
    def deal_links(self,is_tm, nid):
        links = []
        for i in range(len(is_tm)):
            if is_tm[i] is True:
                link = "https://detail.tmall.com/item.htm?id=" + nid[i]
                links.append(link)
            else:
                link = "https://item.taobao.com/item.htm?id=" + nid[i]
                links.append(link)
        return links

    # 数据写入csv文件
    def save_datas(self,nid, name, links, price, comment, key):
        title=key+".csv"

        lock.acquire()
        with open(title,"a",newline='') as f:
            w = csv.writer(f)
            for i in range(len(name)):
               w.writerow([nid[i],name[i],links[i],price[i],comment[i],key])
        lock.release()




if __name__ == '__main__':
    key=input("输入需要获取的商品类型:")
    num=input("请输入需要获取的页数:")

    mark=True
    while(mark):
        try:
            num=int(num)
            while(num > 100):
                num=input("页数不能大于100页，请重新输入：")
                num=int(num)
            mark=False
        except Exception as e :
            num=input("请输入数字")

    print(ctime())

    title = key + ".csv"
    with open(title, "w",newline='') as f:
        w = csv.writer(f)
        w.writerow(["nid", "name", "link", "price", "comment", "type"])

    lock=threading.Lock()
    one=MyThread(key,"1",num,44)
    one.start()
    one.join()

    print(ctime())



