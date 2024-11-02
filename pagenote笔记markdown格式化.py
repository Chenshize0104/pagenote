# !/user/bin/env python
# -*- coding:utf-8 -*-
# time: 2024/11/2--17:40
__author__ = 'Chenlishize'

'''
项目: 将pagenote笔记格式化，从chrome-extension://hpekbddiphlmlfjebppjhemobaopekmp/web/ext/setting.html#/data/backup导出数据 manual.v9.pagenote.zip， 解压文件，将高亮笔记数据格式化导出到csv文件，合并light和webpage数据到新的csv，提取目标列，格式化为markdown文件。
'''

import json
import csv
import os

path = r"E:\pagenote\manual.v9.pagenote\light"
# 修改当前工作目录为path
os.chdir(path)

# 定义输出CSV文件的名称
output_csv_file = 'output.csv'

# 打开一个新的CSV文件用于写入
with open(output_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
    # 创建CSV写入器，这里需要一个字段名列表作为参数
    # 由于我们还不知道字段名，我们先定义一个空列表
    fieldnames = []

    # 遍历当前目录下的所有文件
    for filename in os.listdir('.'):
        if filename.endswith('.json'):
            # 打开JSON文件
            with open(filename, 'r', encoding='utf-8') as jsonfile:
                # 加载JSON数据
                data = json.load(jsonfile)

                # 检查是否已经定义了字段名
                if not fieldnames:
                    # 使用第一个JSON文件的第一个条目的键作为字段名
                    fieldnames = list(data['items'][0]['list'][0].keys())
                    # 创建CSV写入器
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    # 写入表头
                    writer.writeheader()

                # 遍历JSON数据并写入CSV
                for item in data['items']:
                    for entry in item['list']:
                        writer.writerow(entry)

print(f"所有JSON文件已合并到CSV文件：{output_csv_file}")



###################################################################
path = r"E:\pagenote\manual.v9.pagenote\webpage"
# 修改当前工作目录为path
os.chdir(path)

# 定义输出CSV文件的名称
output_csv_file = 'output.csv'

# 打开一个新的CSV文件用于写入
with open(output_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
    # 创建CSV写入器，这里需要一个字段名列表作为参数
    # 由于我们还不知道字段名，我们先定义一个空列表
    fieldnames = []

    # 遍历当前目录下的所有文件
    for filename in os.listdir('.'):
        if filename.endswith('.json'):
            # 打开JSON文件
            with open(filename, 'r', encoding='utf-8') as jsonfile:
                # 加载JSON数据
                data = json.load(jsonfile)

                # 检查是否已经定义了字段名
                if not fieldnames:
                    # 使用第一个JSON文件的第一个条目的键作为字段名
                    fieldnames = list(data['items'][0]['list'][0].keys())
                    # 创建CSV写入器
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    # 写入表头
                    writer.writeheader()

                # 遍历JSON数据并写入CSV
                for item in data['items']:
                    for entry in item['list']:
                        writer.writerow(entry)

print(f"所有JSON文件已合并到CSV文件：{output_csv_file}")



###################################################################

import pandas as pd
from datetime import datetime
import pytz
import os
path = r"E:\pagenote\manual.v9.pagenote"
# 修改当前工作目录为path
os.chdir(path)

# 读取两个CSV文件
df1 = pd.read_csv('light/output.csv', encoding='utf-8')
df2 = pd.read_csv('webpage/output.csv', encoding='utf-8')
# 对2.csv中的特定列进行重命名
df2.rename(columns={'key': 'key2', 'createAt': 'createAt2', 'updateAt': 'updateAt2'}, inplace=True)

# 执行右侧连接，根据两个DataFrame中的相同列名
# 这里假设两个文件中至少有一个共同的列名，例如 'did'
# 如果有多个共同列名，可以通过on参数指定
# 执行右侧连接，根据多个列名
merged_df = pd.merge(df1, df2, on=['url', 'pageKey', 'did', 'deleted'], how='right')

# 定义一个函数，将Unix时间戳转换为中国时区的年月日时分秒格式
def timestamp_to_datetime(timestamp):
    # 将时间戳转换为datetime对象
    dt = datetime.utcfromtimestamp(int(timestamp)/1000)
    # 设置为中国时区
    china_tz = pytz.timezone('Asia/Shanghai')
    # 转换时区
    dt_china = dt.replace(tzinfo=pytz.utc).astimezone(china_tz)
    # 格式化日期时间
    return dt_china.strftime('%Y-%m-%d %H:%M:%S')

# 应用函数转换时间戳
merged_df['time'] = merged_df['time'].apply(timestamp_to_datetime)
merged_df['createAt'] = merged_df['createAt2'].apply(timestamp_to_datetime)
merged_df['updateAt'] = merged_df['updateAt2'].apply(timestamp_to_datetime)
merged_df['createAt2'] = merged_df['createAt2'].apply(timestamp_to_datetime)
merged_df['updateAt2'] = merged_df['updateAt2'].apply(timestamp_to_datetime)

# 对合并后的DataFrame按照title, x, y列进行排序
# 注意：这里假设title列存在于merged_df中，如果不存在，请替换为实际存在的列名
sorted_df = merged_df.sort_values(by=['createAt2', 'title', 'x', 'y'])

# 将排序后的结果保存到新的CSV文件中
sorted_df.to_csv('merged.csv', index=False)

# 提取'title', 'text', 'url', 'pageKey'列
# 注意：这里假设这些列名在sorted_df中是存在的，如果不存在，请替换为实际存在的列名
extracted_df = sorted_df[['title', 'text', 'url', 'pageKey', 'createAt2', 'updateAt2',]]

# 将提取后的列保存到新的CSV文件中
extracted_df.to_csv('merged2.csv', index=False)

print("light和webpage数据合并完成")



###################################################################

import pandas as pd
import os
path = r"E:\pagenote\manual.v9.pagenote"
# 修改当前工作目录为path
os.chdir(path)

# 读取CSV文件
df = pd.read_csv('merged2.csv')

# 按照title列去重并合并text列，同时保持其他列不变
# 这里我们使用groupby来合并具有相同title的text，并使用first来获取其他列的第一次出现的值
df_grouped = df.groupby('title').agg({
    'text': lambda x: '\n\n'.join(x),
    'url': 'first',
    'pageKey': 'first',
    'createAt2': 'first',
    'updateAt2': 'first'
}).reset_index()
# print(df_grouped)
# 按照网页高亮创建时间和title排序
df_grouped = df_grouped.sort_values(by=['createAt2', 'title'])

# 构建Markdown格式的字符串
markdown_content = ""
for index, row in df_grouped.iterrows():
    title = row['title']
    text = row['text']
    # url = df_grouped[df_grouped['title'] == title]['url'].iloc[0]  # 假设每个标题对应的URL是相同的
    url = row['url']
    createAt2 =  row['createAt2']
    updateAt2 = row['updateAt2']
    # 确保每一行text都以'> *'开头，包括第一行，删除text行之间的空行
    lines = [line for line in text.split('\n') if line]  # 移除空行
    formatted_text = '\n'.join('> * ' + line for line in lines)
    markdown_content += f"## [{title}]({url}) [create: {createAt2}, update: {updateAt2}]\n{formatted_text}\n\n\n\n"

# 保存到Markdown文件
with open('pagenote.md', 'w', encoding='utf-8') as file:
    file.write(markdown_content)

print("markdown文件已生成并保存为pagenote.md")



###################################################################
###################################################################

# 最终效果如下：
# ## [Ecosystem restoration strengthens pollination network resilience and function | Nature](https://www.nature.com/articles/nature21071#Sec2) [create: 2024-10-31,update: 2024-10-31]

# > * To account for the temporal and spatial variation across a long tropical flowering season, we collected eight monthly pollination networks from eight dwarf forest plant communities on discrete, mid-altitude inselbergs (64 networks; Fig. 1 and Extended Data Table 1) on the tropical island of Mahé, Seychelles.
# > * Binary networks consist of bars (plant and animal species) and links (interactions), in which the widths of the bars and links represent the abundance of flowers and animals and a measure of visitation strength, respectively (Fig. 1).
# > * We collected interaction network data from eight discrete inselberg (steep-sided monolithic outcrops) plant communities on the granitic island of Mahé, Seychelles (Fig. 1; Western Indian Ocean Biodiversity Hotspot), for eight consecutive months between September 2012 and April 2013 (the full flowering season; Extended Data Table 1).

# ## [Pollinators contribute to the maintenance of flowering plant diversity | Nature](https://www.nature.com/articles/s41586-021-03890-9#Bib1) [create: 2024-10-25,update: 2024-10-25]

# > * To account for variation in the number of sampled styles among species, we standardized pollen data to the same number of styles (n = 54) across species, which outperforms standardization based on rarefaction in preventing information loss and detecting differences among samples (that is, pollen loads of individual species on stigmas)47.


