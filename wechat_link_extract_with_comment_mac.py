#!/usr/bin/python
# -*- coding: UTF-8 -*-

# 使用说明：
# * 在 Terminal 中运行：python wechat_link_extract.py csv_file_path
# * 生成文件：wechat_link_extract.csv，提取出的链接表格；wechat_ken_recommend.csv，道长发的内容

# 依赖 pandas 库，需要先安装，官方安装教程： https://pandas.pydata.org/docs/getting_started/install.html
# TLDR，在 Terminal 中运行：pip install pandas

import pandas as pd
from xml.dom.minidom import parse
import xml.dom.minidom
from datetime import datetime
import csv
import re
import sys

csv_file = str(sys.argv[1])
csv_content = pd.read_csv(csv_file, header=0, usecols=["msgCreateTime", "msgContent", "messageType", "msgStatus"])

cur_year = 2000
cur_month = 0
cur_day = 0
idx = 0

# 提取链接
df = csv_content
df = df[(df["messageType"].isin([1, 49]))] # 链接内容
df = df[(df["msgStatus"].isin([2, 3]))] # 道长发的

url_list = [] # 用于链接去重
rows = [] # [序号，标题，链接，推荐语，日期]
recommend_str = ""
recommend_date = ""

with open('wechat_link_extract_with_comment.csv', 'w') as f:
    writer = csv.writer(f, delimiter=',')

    for index, row in df.iterrows():
        # 更新年月
        date = datetime.fromtimestamp(row["msgCreateTime"])
        if date.year != cur_year or date.month != cur_month: 
            cur_year = date.year
            cur_month = date.month
            idx = 1
            rows.append(["", "", "", "", ""])
            # writer.writerow([])

        if row["messageType"] == 1:
            recommend_str = row["msgContent"]
            recommend_date = "{year}{month:02d}{day:02d}".format(year = date.year, month = date.month, day = date.day)

            # print(recommend_date)
            # print(recommend_str)

            # 推荐语在链接的后面
            if rows[-1][-1] == recommend_date:
                rows[-1][-2] = rows[-1][-2] + "\n" +recommend_str

            #     print("*******")
            #     print(rows)
            # print("")
            # print("---------------------")
            # print("")
        else:
            m = re.search(r'(<msg.*?</msg>)', row["msgContent"], re.IGNORECASE | re.DOTALL | re.MULTILINE)
            if m:
                dom = xml.dom.minidom.parseString(m.group(1))
                ele = dom.documentElement
                type = int(ele.getElementsByTagName("type").item(0).firstChild.data)

                # 链接类型
                if type == 5:
                    title = ele.getElementsByTagName("title").item(0).firstChild.data 
                    url = ele.getElementsByTagName("url").item(0).firstChild.data 
                    if url not in url_list:
                        url_list.append(url)
                        seq = "{year}{month:02d}{idx:02d}".format(year = date.year, month = date.month, idx = idx)
                        date_str = "{year}{month:02d}{day:02d}".format(year = date.year, month = date.month, day = date.day)
                        rows.append([seq, title, url, "", date_str])

                        # writer.writerow([seq, title, url])
                        idx += 1
                # 聊天记录类型
                elif type == 19:
                    recorditem = ele.getElementsByTagName("recorditem").item(0).firstChild.data 
                    inner_dom = xml.dom.minidom.parseString(recorditem)
                    inner_ele = inner_dom.documentElement
                    data_item = inner_ele.getElementsByTagName("dataitem")

                    for data in data_item:
                        # 检查有没有链接内容
                        if len(data.getElementsByTagName("weburlitem")) > 0:
                            web_url_item = data.getElementsByTagName("weburlitem").item(0)
                            if len(web_url_item.getElementsByTagName("title")) > 0 and len(web_url_item.getElementsByTagName("link")) > 0:
                                data_title = web_url_item.getElementsByTagName("title").item(0).firstChild.data
                                data_link = web_url_item.getElementsByTagName("link").item(0).firstChild.data
                                if data_title != None and data_link != None and data_link not in url_list:
                                    url_list.append(data_link)
                                    seq = "{year}{month:02d}{idx:02d}".format(year = date.year, month = date.month, idx = idx)
                                    date_str = "{year}{month:02d}{day:02d}".format(year = date.year, month = date.month, day = date.day)
                                    rows.append([seq, data_title, data_link, "", date_str])
                                    # writer.writerow([seq, data_title, data_link])
                                    idx += 1

            # # 推荐语在链接的前面
            # if rows[-1][-1] == recommend_date:
            #     rows[-1][-2] = recommend_str
            #     recommend_date = ""
            #     recommend_str = ""


    for row in rows:
        writer.writerow(row)



# # 提取推荐语
# df = csv_content
# df = df[(df["messageType"] == 1)] # 文字内容
# df = df[(df["msgStatus"].isin([2, 3]))] # 道长发的

# with open('wechat_ken_recommend.csv', 'w') as f:
#     writer = csv.writer(f, delimiter=',')

#     for index, row in df.iterrows():
#         # 更新年月
#         date = datetime.fromtimestamp(row["msgCreateTime"])
#         if date.year != cur_year or date.month != cur_month: 
#             cur_year = date.year
#             cur_month = date.month
#             idx = 1
#             writer.writerow([])
        
#         seq = "{year}{month:02d}{idx:02d}".format(year = date.year, month = date.month, idx = idx)
#         writer.writerow([seq, row["msgContent"]])
#         idx += 1