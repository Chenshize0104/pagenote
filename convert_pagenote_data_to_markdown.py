# !/user/bin/env python
# -*- coding:utf-8 -*-
# time: 2024/11/6--12:40
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
output_csv_file = 'light_output.csv'

# 定义字段名列表，初始化为空集合
fieldnames = set()

# 遍历当前目录下的所有文件
for filename in os.listdir('.'):
    if filename.endswith('.json'):
        # 打开JSON文件
        with open(filename, 'r', encoding='utf-8') as jsonfile:
            print(filename)
            # 加载JSON数据
            data = json.load(jsonfile)
            # 更新字段名列表
            for item in data['items']:
                for entry in item['list']:
                    fieldnames.update(entry.keys())

# 将集合转换为列表，并添加文件名字段
fieldnames = ['filename.light'] + sorted(list(fieldnames))

# 打开一个新的CSV文件用于写入
with open(output_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
    # 创建CSV写入器
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # 写入表头
    writer.writeheader()

    # 再次遍历所有JSON文件
    for filename in os.listdir('.'):
        if filename.endswith('.json'):
            # 打开JSON文件
            with open(filename, 'r', encoding='utf-8') as jsonfile:
                print(filename)
                # 加载JSON数据
                data = json.load(jsonfile)
                # 遍历JSON数据并写入CSV
                for item in data['items']:
                    for entry in item['list']:
                        # 创建一个新字典，包含所有字段名和对应的值，缺失的字段用空字符串填充
                        new_entry = {k: entry.get(k, '') for k in fieldnames}
                        new_entry['filename.light'] = filename  # 添加文件名
                        writer.writerow(new_entry)

print(f"所有JSON文件已合并到CSV文件：{output_csv_file}")



###################################################################
path = r"E:\pagenote\manual.v9.pagenote\webpage"
# 修改当前工作目录为path
os.chdir(path)

# 定义输出CSV文件的名称
output_csv_file = 'webpage_output.csv'

# 定义字段名列表，初始化为空集合
fieldnames = set()

# 遍历当前目录下的所有文件
for filename in os.listdir('.'):
    if filename.endswith('.json'):
        # 打开JSON文件
        with open(filename, 'r', encoding='utf-8') as jsonfile:
            print(filename)
            # 加载JSON数据
            data = json.load(jsonfile)
            # 更新字段名列表
            for item in data['items']:
                for entry in item['list']:
                    fieldnames.update(entry.keys())

# 将集合转换为列表，并添加文件名字段
fieldnames = ['filename.webpage'] + sorted(list(fieldnames))

# 打开一个新的CSV文件用于写入
with open(output_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
    # 创建CSV写入器
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # 写入表头
    writer.writeheader()

    # 再次遍历所有JSON文件
    for filename in os.listdir('.'):
        if filename.endswith('.json'):
            # 打开JSON文件
            with open(filename, 'r', encoding='utf-8') as jsonfile:
                print(filename)
                # 加载JSON数据
                data = json.load(jsonfile)
                # 遍历JSON数据并写入CSV
                for item in data['items']:
                    for entry in item['list']:
                        # 创建一个新字典，包含所有字段名和对应的值，缺失的字段用空字符串填充
                        new_entry = {k: entry.get(k, '') for k in fieldnames}
                        new_entry['filename.webpage'] = filename  # 添加文件名
                        writer.writerow(new_entry)

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
df1 = pd.read_csv('light/light_output.csv', encoding='utf-8')
df2 = pd.read_csv('webpage/webpage_output.csv', encoding='utf-8')
# 对2.csv中的特定列进行重命名
df2.rename(columns={'key': 'key2.webpage', 'createAt': 'createAt2.webpage', 'updateAt': 'updateAt2.webpage'}, inplace=True)

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
merged_df['createAt'] = merged_df['createAt2.webpage'].apply(timestamp_to_datetime)
merged_df['updateAt'] = merged_df['updateAt2.webpage'].apply(timestamp_to_datetime)
merged_df['createAt2.webpage'] = merged_df['createAt2.webpage'].apply(timestamp_to_datetime)
merged_df['updateAt2.webpage'] = merged_df['updateAt2.webpage'].apply(timestamp_to_datetime)

# 对合并后的DataFrame按照title, x, y列进行排序
# 注意：这里假设title列存在于merged_df中，如果不存在，请替换为实际存在的列名
sorted_df = merged_df.sort_values(by=['createAt2.webpage','url', 'title', 'sortIndex', 'x', 'y'])

# 将排序后的结果保存到新的CSV文件中
sorted_df.to_csv('merged.csv', index=False)

# 提取'title', 'text', 'url', 'pageKey'列
# 注意：这里假设这些列名在sorted_df中是存在的，如果不存在，请替换为实际存在的列名
# extracted_df = sorted_df[['title', 'text', 'url', 'pageKey', 'sortIndex', 'x', 'y', 'createAt2.webpage', 'updateAt2.webpage',]]
extracted_df = sorted_df[['title', 'text', 'tip', 'url',  'pageKey', 'sortIndex', 'x', 'y', 'createAt2.webpage', 'updateAt2.webpage',]]

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

# 定义一个函数，用于合并text和tip列，并在它们之间添加换行
def merge_text_tip(row):
    # 检查tip是否为非空字符串
    if pd.notnull(row['tip']) and row['tip'] != '':
        # 如果tip不为空，则将text和tip合并，并在它们之间添加换行
        return f"{row['text']}\n\n{row['tip']}"
    else:
        # 如果tip为空或为NaN，则只返回text
        return row['text']

# 应用函数合并text和tip列
df['text_tip'] = df.apply(merge_text_tip, axis=1)
df['text'] = df['text_tip']

# 按照title列去重并合并text列，同时保持其他列不变
# 这里我们使用groupby来合并具有相同title的text，并使用first来获取其他列的第一次出现的值
df_grouped = df.groupby('title').agg({
    'text': lambda x: '\n\n'.join(x),
    'url': 'first',
    'pageKey': 'first',
    'createAt2.webpage': 'first',
    'updateAt2.webpage': 'first'
}).reset_index()
# print(df_grouped)
# 按照网页高亮创建时间和title排序
df_grouped = df_grouped.sort_values(by=['createAt2.webpage', 'title'])

# 构建Markdown格式的字符串
markdown_content = ""
for index, row in df_grouped.iterrows():
    title = row['title']
    text = row['text']
    # url = df_grouped[df_grouped['title'] == title]['url'].iloc[0]  # 假设每个标题对应的URL是相同的
    url = row['url']
    createAt2_webpage =  row['createAt2.webpage']
    updateAt2_webpage = row['updateAt2.webpage']
    # 确保每一行text都以'> *'开头，包括第一行，删除text行之间的空行
    lines = [line for line in text.split('\n') if line]  # 移除空行
    formatted_text = '\n'.join('> * ' + line for line in lines)
    # markdown_content += f"## [{title}]({url}) [create: {createAt2_webpage}, update: {updateAt2_webpage}]\n{formatted_text}\n\n\n"
    markdown_content += f"> [!NOTE] ### [{title}] [create: {createAt2_webpage}, update: {updateAt2_webpage}] ({url})\n{formatted_text}\n\n\n"

# 保存到Markdown文件
# with open('pagenote.md', 'a', encoding='utf-8') as file:
with open('pagenote.md', 'w', encoding='utf-8') as file:
    file.write(markdown_content)

print("markdown文件已生成并保存为pagenote.md")



###################################################################
###################################################################

# 最终效果如下：

# > [!NOTE] ### [Ecosystem restoration strengthens pollination network resilience and function | Nature] [create: 2024-11-06 10:41:55, update: 2024-11-06 12:09:44] (https://www.nature.com/articles/nature21071)
# > * To account for the temporal and spatial variation across a long tropical flowering season, we collected eight monthly pollination networks from eight dwarf forest plant communities on discrete, mid-altitude inselbergs (64 networks; Fig. 1 and Extended Data Table 1) on the tropical island of Mahé, Seychelles.
# > * We collected interaction network data from eight discrete inselberg (steep-sided monolithic outcrops) plant communities on the granitic island of Mahé, Seychelles (Fig. 1; Western Indian Ocean Biodiversity Hotspot), for eight consecutive months between September 2012 and April 2013 (the full flowering season; Extended Data Table 1).
# > * Binary networks consist of bars (plant and animal species) and links (interactions), in which the widths of the bars and links represent the abundance of flowers and animals and a measure of visitation strength, respectively (Fig. 1).
# > * We calculated two distance indices to test for qualitative and quantitative differences in plant–pollinator communities within and across sites and months.


# > [!NOTE] ### [Pollinators contribute to the maintenance of flowering plant diversity | Nature] [create: 2024-10-25 12:56:00, update: 2024-11-03 01:18:34] (https://www.nature.com/articles/s41586-021-03890-9)
# > * To account for variation in the number of sampled styles among species, we standardized pollen data to the same number of styles (n = 54) across species, which outperforms standardization based on rarefaction in preventing information loss and detecting differences among samples (that is, pollen loads of individual species on stigmas)47.


# 在Obsidian中打开食用！
