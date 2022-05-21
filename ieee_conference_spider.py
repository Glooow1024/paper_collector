# !/usr/bin/python
# -*- coding:utf-8 -*-
###########################################################
# 爬虫：抓取ICRA会议文章列表、摘要、关键词                    
#                                                        
# 根据不同的会议，需要修改的部分包括：
# - 会议ID（只适用于IEEE的会议）
#
# 更新版本：
# - 2021/04/17 创建
# - 2022/03/18 修改个别变量名
###########################################################

import re
import os
import json
import time
import requests
import pandas as pd
import logging
from urllib.request import urlretrieve
from urllib.parse import quote
from bs4 import BeautifulSoup
from selenium import webdriver


class IEEESpider:
    def __init__(self):
        self.flag_running = False


    def search_conferenceID():
        """
        Open IEEE website and search the conferenceID.
        """
        from selenium.webdriver.chrome.options import Options
        global driver
        chrome_options = Options()
        web_driver='E:\\SAST\\spider\\paper_collector\\chromedriver'
        driver=webdriver.Chrome(executable_path=web_driver, chrome_options=chrome_options)
        browse_url = 'https://ieeexplore.ieee.org/browse/conferences/title'
        driver.get(browse_url)


    def get_issueNumber(self, conferenceID):
        """
        Get the issueNumber from the website.
        """
        conferenceID = str(conferenceID)
        gheaders = {
            'Referer': 'https://ieeexplore.ieee.org/xpl/conhome/'+conferenceID+'/proceeding',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
        }
        md_url = 'https://ieeexplore.ieee.org/rest/publication/home/metadata?pubid='+conferenceID
        md_res = requests.get(md_url, headers = gheaders)
        md_dic = json.loads(md_res.text)
        issueNumber = str(md_dic['currentIssue']['issueNumber'])
        return issueNumber


    def get_article_info(self, conferenceID, saveFileName, logger):
        """
        Collect the published paper data, and save into the csv file "saveFileName".
        """
        # 获取issueNumber
        issueNumber = str(self.get_issueNumber(conferenceID))
        conferenceID = str(conferenceID)
        logger.info('┏--------------------------------------------------------------------┐')
        logger.info(('║ ConferenceID : ' + conferenceID).ljust(69) + '║')
        logger.info(('║ issueNumber  : ' + issueNumber).ljust(69) + '║')
        logger.info(('║ Save to file : ' + saveFileName).ljust(69) + '║')
        logger.info('└--------------------------------------------------------------------┘')

        """logger.info('TEST!')
        for i in range(100):
            if not self.flag_running:
                continue
            logger.info(i)
            time.sleep(1)
        logger.info('BYE-BYE!')
        return """

        # 记录论文数据
        dataframe = pd.DataFrame({})
        paper_title = []
        paper_author = []
        paper_year = []
        paper_citation = []
        paper_abstract = []
        paper_ieee_kwd = []

        # 从第一页开始下载
        pageNumber = 38
        count = 0
        while(self.flag_running):
            # 获取会议文章目录
            toc_url = 'https://ieeexplore.ieee.org/rest/search/pub/'+conferenceID+'/issue/'+issueNumber+'/toc'
            payload = '{"pageNumber":'+str(pageNumber)+',"punumber":"'+conferenceID+'","isnumber":'+issueNumber+'}'
            headers = {
                'Host': 'ieeexplore.ieee.org',
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
                'Referer': 'https://ieeexplore.ieee.org/xpl/conhome/'+conferenceID+'/proceeding?pageNumber='+str(pageNumber),
            }
            toc_res = requests.post(toc_url, headers = headers, data=payload)
            toc_dic = json.loads(toc_res.text)
            try:
                articles = toc_dic['records']
            except KeyError:
                break
            else:
                for article in articles:
                    title = article['highlightedTitle']
                    paper_link = 'https://ieeexplore.ieee.org' + article['htmlLink']
                    paper_info = requests.get(url=paper_link, headers=headers, timeout=10)
                    soup = BeautifulSoup(paper_info.text, 'lxml')                  # 解析
                    # 正则表达式 创建模式对象
                    pattern = re.compile(r'xplGlobal.document.metadata=(.*?)"};', re.MULTILINE | re.DOTALL)
                    script = soup.find("script", text=pattern)                     # 根据模式对象进行搜索
                    try:
                        res_dic = pattern.search(script.string).group(1)+'"}'      # 配合search找到字典，匹配结尾字符串，降低文章摘要中也出现这种字符串的概率
                        # 解析异常，一般是因为文章 abstract 中出现了字符串 '"};'
                        json_data = json.loads(res_dic)                            # 将json格式数据转换为字典
                    except Exception as e:
                        print(pattern.search(script.string).group(0))
                        print(res_dic)
                    # 保存文章信息
                    paper_title.append(title)
                    paper_year.append(json_data['publicationYear'])
                    #print(json_data.keys())
                    #a = input('input anything...')
                    if 'author' in json_data.keys():
                        paper_author.append(json_data['author'])
                    else:
                        paper_author.append(None)
                    if 'abstract' in json_data.keys():
                        paper_abstract.append(json_data['abstract'])
                    else:
                        paper_abstract.append(None)
                    if 'keywords' in json_data.keys():
                        paper_ieee_kwd.append(json_data['keywords'][0]['kwd'])       # ieee有三种 key words
                    else:
                        paper_ieee_kwd.append(None)
                    count=count+1
                    #link = 'https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&arnumber='+article['articleNumber']+'&ref='
                    #alf.write(title.replace('\n','')+'>_<'+link+'\n')
                
                # 写入csv文件
                dataframe = pd.DataFrame({'title':paper_title, 'year':paper_year, 'abstract':paper_abstract, 'key words':paper_ieee_kwd})
                dataframe.to_csv(saveFileName, index=True, sep=',')
                #print('Page ', pageNumber, ', total ', count, 'papers.')
                logger.info('Page {}, total {} papers.'.format(pageNumber, count))
                pageNumber = pageNumber+1
                # 停一下防禁ip
                time.sleep(3)

        # 写入csv文件
        dataframe = pd.DataFrame({'title':paper_title, 'year':paper_year, 'abstract':paper_abstract, 'key words':paper_ieee_kwd})
        dataframe.to_csv(saveFileName, index=True, sep=',')
        logger.info('All work done!')
        logger.info('='*70)
        return


# start
if __name__ == "__main__":
    ############################################################
    ###############    根据要爬的网址自行修改   ################
    save_file_path = 'E:\\spider\\paper_collector\\'   # 保存目录
    save_file_name = 'ICRA_2019_1.csv'
    conference_ID  = 8780387                                  # 会议 ID
    IEEE_root_url  = 'https://ieeexplore.ieee.org'
    ############################################################

    sp = IEEESpider()
    sp.get_article_info(conference_ID, save_file_path + save_file_name)
