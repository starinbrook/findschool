# coding:UTF-8
import urllib
import urllib2
import bs4
from bs4 import BeautifulSoup
import re
import sys
import time

import sys_config
import user_config

reload(sys)
sys.setdefaultencoding('UTF-8')

"""

1、获取http://www.eol.cn/html/g/gxmd/211.shtml 页面上所有211高校的编号school_code

2、拼接'https://gkcx.eol.cn/schoolhtm/specialty/' + school_code + '/' + province_code + '/specialtyScoreDetail_' + year + '_10017.htm'

3、筛选最低录取分数线在给定分数以下的所有学校，并保存到文件

Created on 2017-02-28

@author: starinbrook

"""

# set proxy
def setProxy(enable_proxy):
	if enable_proxy:
		print "set proxy : " + sys_config.PROXY_ADDRESS
		proxy_handler = urllib2.ProxyHandler({"http":sys_config.PROXY_ADDRESS})
		opener = urllib2.build_opener(proxy_handler)
	else:
		null_proxy_handler = urllib2.ProxyHandler({})
		opener = urllib2.build_opener(null_proxy_handler)
	urllib2.install_opener(opener)

# get page content
def get_page_html(url):
	headers = {}
	headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36'
	headers['Connection'] = 'keep-alive'
	request = urllib2.Request(url,headers=headers)
	try:
		response = urllib2.urlopen(request,timeout=30)
		html = response.read()
		return html
	except urllib2.HTTPError,e:
		print e.code
	except urllib2.URLError,e:
		print e.reason
	else :
		print 'OK'

# process page content
def page_process(html,output_fpath):

	soup = BeautifulSoup(html,'html.parser',from_encoding="UTF-8")
	for node in soup.find_all('div',class_='zk_ad_475'):
         school_soup = BeautifulSoup(str(node),'html.parser',from_encoding='UTF-8')
         target_a = school_soup.select('a')
         if target_a:
             for a in target_a:
                 href_str = find_href(str(a))[0]
                 target_href = re.search('schoolSpecailtyMark',href_str,re.M|re.I)
                 if target_href != None:
                     pattern = re.compile(r'\d+')  # 查找数字
                     school_num = pattern.findall(href_str)[0]
                     school_url = sys_config.BASE_URL + school_num + "/" + user_config.setting['province'] + "/specialtyScoreDetail_" + user_config.setting['year'] + "_10017.htm"
                     schhool_html = get_page_html(school_url) # 获取页面文档
                     school_page_process(school_url, schhool_html, output_fpath)  # 处理页面并将结果保存到指定文件

# process school page content
def school_page_process(school_url,html,output_fpath):
    # 输出文件路径
    fout = open(output_fpath, "a")

    soup = BeautifulSoup(html, 'html.parser', from_encoding="UTF-8")

    # 学校基本信息
    school_info_div =  soup.find_all('p', class_='li-school-label')[0]
    school_info_bs = BeautifulSoup(str(school_info_div), 'html.parser', from_encoding='UTF-8')
    school_name = str(school_info_bs.find_all('span')[0])

    # 录取分数线
    score_table = soup.find_all('table', class_='li-admissionLine')[0]
    score_tbody_bs = BeautifulSoup(str(score_table), 'html.parser', from_encoding='UTF-8')
    score_tbody = score_tbody_bs.find_all('tbody')
    score_tr_bs = BeautifulSoup(str(score_tbody), 'html.parser', from_encoding='UTF-8')
    score_tr = score_tr_bs.find_all('tr')
    for node in score_tr:
        score_soup = BeautifulSoup(str(node), 'html.parser', from_encoding='UTF-8')
        target_td = score_soup.select('td')
        #print len(target_td)
        if len(target_td) == 6:
            #major = str(target_td[0])
            min_score_td = target_td[4]
            pattern = re.compile(r'\d+')  # 查找数字
            min_score = pattern.findall(str(min_score_td))[0]
            if int(min_score) <= int(user_config.setting['score']):
                print school_name + '，最低分：' + min_score
                fout.write(school_name + "\n")
                fout.write(school_url + "\n")
                fout.write('最低分：' + min_score + "\n")
                fout.write('--------------------------------------------------------------------------------------\n\n');
                break
            else:
                print school_name + ' NO'
    fout.flush()
    fout.close()

# get href from string
def find_href(str):
	return re.findall(r"(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')" ,str)

def main():
	setProxy(sys_config.ENABLE_PROXY) # 设置代理
	output_fpath = "./outputs/%s" % user_config.setting["output_fname"]
	url = sys_config.REQUEST_URL
	html = get_page_html(url) # 获取页面文档
	page_process(html,output_fpath) # 处理页面并将结果保存到指定文件

if __name__ == '__main__':
	main()
