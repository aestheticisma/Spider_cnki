from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import re
import csv

###########################################################################
##################************变量说明************##########################
# self.author_name 作者姓名(str)                                          ##
# self.organization 所属机构名称(str)                                     ##
# self.work_direction 作者研究方向(str)                                   ##
# self.same_author 同名作者基本信息(list)	包括姓名、机构名、研究方向          ##
# self.author_concern_areas 作者关注领域(list)                            ##
# self.the_highest_cited_list 最高被引文章(list)                          ##
# self.the_highest_download_list 最高下载文章(list)                       ##
# self.literature_all_list 全部文章(dict)                                 ##
# self.same_college_people_list 相同机构合作者(list) 元素为(人名，机构)元组  ##
# self.diff_college_people_list 不同机构合作者(list) 元素为(人名，机构)元组  ##
# self.fonds_list 获得的支持基金(list)                                    ##
# writes_contents #最后的储存字典(dict) 将其写入文件中                      ##
##################************变量说明************##########################
###########################################################################

file_dir = '/home/dutir/zhangfan2/spider/code'
# author_list = ["林鸿飞", "刁宇峰", "卢湖川", "刘挺"]
# author_list = ["刁宇峰", "杨亮", "刘挺", "卢湖川"]
author_list = ["刁宇峰"]
cnki_search_url = 'https://www.cnki.net/'

#从左至右分别为：发表在期刊上的文献、发表在外刊上的文献、发表在报纸上的文献、发表在会议上的文献、发表在博硕上的文献、曾参考的文献、合作作者、获得的支持基金
type_str = ['//dd[@id="lcatalog_1"]/a', '//dd[@id="lcatalog_Wwjd"]/a', '//dd[@id="lcatalog_4"]/a', '//dd[@id="lcatalog_3"]/a', '//dd[@id="lcatalog_2"]/a', '//dd[@id="lcatalog_Cckf"]/a', '//dt[@id="lcatalog_AuCos"]/a', '//dt[@id="lcatalog_AuFunds"]/a']
frame_str = ["framecatalog_1", "framecatalog_Wwjd", "framecatalog_4", "framecatalog_3", "framecatalog_2", "framecatalog_Cckf", "framecatalog_AuCos", "framecatalog_AuFunds"]

class cnki_author_spider(object):
	def __init__(self, browser, author):
		self.browser = browser
		#最大化窗口
		self.browser.maximize_window()
		#获取网址
		self.browser.get(cnki_search_url)
		# 修改为搜索作者
		self.browser.find_element_by_class_name('sort-icon').click()
		self.browser.find_element_by_xpath('.//a[text()="作者"]').click()
		# 输入搜索内容
		search_input = self.browser.find_element_by_class_name('search-input')
		search_input.clear()
		search_input.send_keys(author)
		search_input.send_keys(Keys.RETURN) # 回车键
		# download_page(browser)

	def open_author_page(self):
		# 知网存在框架源代码 需要新的网址
		# self.browser.get(cnki_next_page)
		self.browser.switch_to.frame('iframeResult')
		time.sleep(2)
		# 找到第2个font （需要点击的作者名在font标签里）
		self.browser.find_element_by_xpath('//td[@class="author_flag"]/a/font').click()
		
		self.browser.switch_to.default_content()

		# 打开新标签页需要切换控制权
		self.window = self.browser.window_handles
		self.browser.switch_to.window(self.window[1])

	def input_next_one(self, author):
		self.browser.switch_to.window(self.window[0])
		search_input = self.browser.find_element_by_class_name('rekeyword')
		search_input.clear()
		search_input.send_keys(author)

		search_input.send_keys(Keys.RETURN) # 回车键
		time.sleep(3)

	def get_all_sameauthor_url(self):
		self.sameauthor_url = []
		# self.browser.find_element_by_xpath('//div[@class="sameName"]/ul/li/b/a').click()
		self.sameauthor_url.append(self.browser.current_url)
		temp_code = re.findall(r'\d+', self.sameauthor_url[0])[0]
		index = self.sameauthor_url[0].find(temp_code)
		self.sameauthor_url[0] = self.sameauthor_url[0][:index+8]
		#self.sameauthor_url[1] = re.findall(r'\d{8}',self.sameauthor_url[0])[0]

		# # 点击没有新标签页 还是当前标签页因此不需要切换页面
		# self.output_contents()
		# self.write_to_file()
		a = self.browser.find_elements_by_xpath('//div[@class="sameName"]/ul/li/b/a')
		for a_tag in a:
			#print(a_tag.get_attribute("onclick"))
			self.sameauthor_url.append(re.findall(r'\d+', a_tag.get_attribute("onclick"))[0])
		print(self.sameauthor_url)
		for code in self.sameauthor_url[1:]:
			url = 'https://kns.cnki.net/kcms/detail/knetsearch.aspx?sfield=au&skey=' + self.author_name + '&code=' + code
			print(self.sameauthor_url[0])
			self.browser.get(url)
			self.output_contents()
			self.write_to_file()

		


		# 作者姓名
	def contents_author_name(self):
		self.author_name = self.browser.find_element_by_class_name('name').text
		print("%s\n姓名爬取完成！" % self.author_name)
		# 机构名称
	def contents_organization(self):
		self.organization = self.browser.find_element_by_xpath('//p[@class="orgn"]/a').text
		print("机构名称爬取完成！")
		# 研究方向
	def contents_work_direction(self):
		self.work_direction = self.browser.find_element_by_class_name('doma').text
		self.work_direction = re.split(';', self.work_direction)[:-1]
		print("研究方向爬取完成！")

		# 同名作者及其机构、研究方向
	def contents_same_name_author(self):
		self.same_author_name_list = []
		self.same_author_college_list = []
		self.same_author_interests_list = []
		name_dir = '//div[@class="sameName"]/ul/li/b/a'
		college_dir = '//div[@class="sameName"]/ul/li/span/a'
		interests_dir = '//div[@class="sameName"]/ul/li/em'
		# 有同名作者的情况
		try:
			temp_list_1 = self.browser.find_elements_by_xpath(name_dir)
			temp_list_2 = self.browser.find_elements_by_xpath(college_dir)
			temp_list_3 = self.browser.find_elements_by_xpath(interests_dir)
			for i in range(len(temp_list_1)):
				self.same_author_name_list.append(temp_list_1[i].text)
				self.same_author_college_list.append(temp_list_2[i].text)
				self.same_author_interests_list.append(re.split(';', temp_list_3[i].text)[:-1])
			self.same_author = []
			for i in range(len(self.same_author_name_list)):
				self.same_author.append((self.same_author_name_list[i], self.same_author_college_list[i], self.same_author_interests_list[i]))
		# 无同名作者的情况
		except:
			self.same_author = []
		# self.same_author["author_name"] = self.same_author_name_list
		# self.same_author["author_college"] = self.same_author_college_list
		# self.same_author["author_work_direction"] = self.same_author_interests_list
		print("相同姓名作者基本信息爬取完成！")

		# 作者关注领域
	def contents_author_concern_areas(self):
		# 获取关注领域内容需要切换至iframe[0]
		# self.iframe = self.browser.find_elements_by_tag_name('iframe')[0]
		# self.browser.switch_to.frame(self.iframe)
		self.author_concern_areas = []
		self.browser.switch_to.frame('frame1')
		# 有关注领域时
		try:
			self.interests_list = self.browser.find_elements_by_xpath('//div[@class="listcont"]/ul/*/a')
			for i in self.interests_list:
				self.author_concern_areas.append(i.text)
		except:
			self.author_concern_areas = []
		# 返回原frame
		self.browser.switch_to.default_content()
		print("关注领域爬取完成！")

		# 最高被引文章
	def contents_the_highest_cited(self):
		# 获取最高被引内容需要切换至iframe[1]
		self.the_highest_cited_list = []
		self.iframe = self.browser.find_elements_by_tag_name('iframe')[1]
		self.browser.switch_to.frame(self.iframe)
		try:
			temp_list = self.browser.find_elements_by_xpath('//div[@class="essayBox"]/*/ul/li')
			for i in temp_list:
				self.the_highest_cited_list.append(i.text)
		except:
			self.the_highest_cited_list = []
		# 返回原frame
		self.browser.switch_to.default_content()
		print("最高被引文章爬取完成！")

		# 最高下载文章
	def contents_the_highest_download(self):
		# 获取最高下载内容需要切换至iframe[1]
		# self.iframe = self.browser.find_elements_by_tag_name('iframe')[1]
		# self.browser.switch_to.frame(self.iframe)
		self.the_highest_download_list = []
		self.browser.switch_to.frame(1)
		try:
			temp_list = self.browser.find_elements_by_xpath('//div[@class="essayBox border"]/*/ul/li')
			for i in temp_list:
				self.the_highest_download_list.append(i.text)
		except:
			self.the_highest_download_list = []
		# 返回原frame
		self.browser.switch_to.default_content()
		print("最高下载文章爬取完成！")

		# 复用函数 
		# 对有数据的论文发表类型（如中文期刊、外刊、报纸等）的论文名称等
		# 保存到一个列表里返回
	def literature_all(self, kinds_name):
		store_list = []
		page_num_str = self.browser.find_element_by_xpath('//b[@class="titleTotle"]/span').text
		page_num = int(page_num_str)
		temp_list = self.browser.find_elements_by_xpath('//ul[@class="bignum"]/li')
		for i in temp_list:
			store_list.append(i.text)
		print("%s 第1页爬取完成！" % kinds_name)
		time.sleep(2)
		# 计算需要点击count次“下一页”
		if page_num % 10 == 0:
			count = page_num // 10 - 1
		else:
			count = page_num // 10
		for i in range(count):
			# if i == 0:
			# 	self.browser.find_element_by_xpath('//span[@id="CJFQ"]/a[@text="下一页"]').click()
			# else:
			# 	self.browser.find_element_by_xpath('//span[@id="CJFQ"]/a[@text="下一页"]').click()
			self.browser.find_element_by_link_text('下一页').click()
			time.sleep(2)
			temp_list = self.browser.find_elements_by_xpath('//ul[@class="bignum"]/li')
			for j in temp_list:
				store_list.append(j.text)
			print("%s 第%d页爬取完成" % (kinds_name, (i+2)))
		# for i in store_list:
		# 	print(i)
		return store_list
		# 作者文献 
		# 从 发表在期刊的文献————曾参考文献
	def contents_literature(self, type_str, frame_str, kinds_name):
		# literature_list = []
		# 点击 type_str 如“发表在期刊上的文献”
		self.browser.find_element_by_xpath(type_str).click()
		# 等待页面完全渲染
		time.sleep(1)
		# 切换至相应的iframe
		self.browser.switch_to.frame(frame_str)
		time.sleep(2)
		is_exit = ""
		is_exit_2 = ""
		try:
			is_exit = self.browser.find_element_by_xpath('//b[@class="titleTotle"]').text
		except:
			is_exit_2 = self.browser.find_element_by_xpath('//div[@class="essayBox"]').text

		if(is_exit == "未找到相关数据" or is_exit_2 == "外文期刊" or is_exit_2 =="曾参考的文献"):
			print(kinds_name + ' '+ "未找到相关数据")
			self.literature_list = []
			#返回原frame
			self.browser.switch_to.default_content()
		else:
			self.literature_list = self.literature_all(kinds_name)
			#返回原frame
			self.browser.switch_to.default_content()
			# print(self.literature_list)

		# 合作者：包括同机构和不同机构的合作者
		# 同机构：is_same = 1
		# 不同机构： is_same = 0
	def contents_cooperator(self, type_str, frame_str, is_same):
		self.browser.find_element_by_xpath(type_str).click()
		# 等待页面完全渲染
		time.sleep(1)
		# 切换至相应的iframe
		self.browser.switch_to.frame(frame_str)
		time.sleep(1)

		# self.cooperator_dict = {}
		if is_same == 1:
			self.same_college_people_list = []
			is_same_dir = '//ul[@class="col8"]/li'
			temp_list = self.browser.find_elements_by_xpath(is_same_dir)
			for i in temp_list:
				self.same_college_people_list.append((i.text, self.organization))
			print("相同机构合作者爬取完成！")
		else:
			self.diff_college_people_list = []
			self.people_list = []
			self.college_list = []
			is_same_name_dir = '//ul[@class="authInfo col3"]/li/b'
			is_same_college_dir  = '//ul[@class="authInfo col3"]/li/span/a'
			temp_list = self.browser.find_elements_by_xpath(is_same_name_dir)
			for i in temp_list:
				self.people_list.append(i.text)
			temp_list = self.browser.find_elements_by_xpath(is_same_college_dir)
			for i in temp_list:
				self.college_list.append(i.text)

			# （人名，机构名）组成二元组 放入列表中储存
			for i in range(len(self.people_list)):
				self.diff_college_people_list.append((self.people_list[i], self.college_list[i]))
			# self.cooperator_dict["author_name"] = self.people_list
			# self.cooperator_dict["author_college"] = self.college_list
			print("不同机构合作者爬取完成！")
		self.browser.switch_to.default_content()
		#注意：此处未设置判断 若其无合作者会报错
		# temp_list = self.browser.find_elements_by_xpath(is_same_dir)
		# for i in temp_list:
		# 	self.people_list.append(i.text)

	def contents_fonds(self, type_str, frame_str):
		self.browser.find_element_by_xpath(type_str).click()
		# 等待页面完全渲染
		time.sleep(1)
		# 切换至相应的iframe
		self.browser.switch_to.frame(frame_str)
		time.sleep(1)
		self.fonds_list = []
		fonds_dir = '//div[@class="listcont"]/ul/li'
		temp_list = self.browser.find_elements_by_xpath(fonds_dir)
		for i in temp_list:
			self.fonds_list.append(i.text)
		print("支持基金爬取完成！")
		self.browser.switch_to.default_content()

	def quit(self):
		self.browser.quit()

	def write_to_file(self):
		writes_contents = {}
		writes_contents["author_name"] = self.author_name
		writes_contents["author_college"] = self.organization
		writes_contents["author_work_direction"] = self.work_direction
		writes_contents["same_author"] = self.same_author
		writes_contents["author_concern_areas"] = self.author_concern_areas
		writes_contents["the_highest_cited"] = self.the_highest_cited_list
		writes_contents["the_highest_download"] = self.the_highest_download_list
		writes_contents["literature"] = self.literature_all_list
		writes_contents["same_college_cooperator"] = self.same_college_people_list
		if self.flag == 0:
			writes_contents["diff_college_cooperator"] = self.diff_college_people_list
		# 不同合作者爬取失败的情况
		# 此处吐槽知网的前端工程师，每个页面你设计的要一样嘛！！！
		else:
			writes_contents["diff_college_cooperator"] = []
		writes_contents["fonds"] = self.fonds_list
		# print(self.same_college_people_list)
		# print(self.diff_college_people_list)
		# print(self.same_author)
		print("**********字典转文件操作完成！************")
		print("**********作者%s爬取完成！************" % self.author_name)
		print(writes_contents)
		# with open(file_dir+self.author_name+'_'+self.organization+'.txt', 'w') as f:
		# 	for key, value in writes_contents.items():
		# 		f.write(key,value)


	def output_contents(self):
		self.literature_all_list = {}
		self.flag = 0
		# 打印作者姓名
		self.contents_author_name()
		# 打印机构名称
		self.contents_organization()
		# 打印研究方向
		self.contents_work_direction()
		# 打印同名作者及其机构、兴趣
		self.contents_same_name_author()
		# 打印作者关注领域
		self.contents_author_concern_areas()
		# 打印最高被引
		self.contents_the_highest_cited()
		# 打印最高下载
		self.contents_the_highest_download()
		# 打印发表文献
		self.contents_literature(type_str[0], frame_str[0], "发表在期刊上的文献")
		self.literature_all_list["literature_in_magazine"] = self.literature_list
		# 打印外刊文献
		self.contents_literature(type_str[1], frame_str[1], "外刊期刊文献")
		self.literature_all_list["literature_in_foreign"] = self.literature_list
		# 打印报纸文献
		self.contents_literature(type_str[2], frame_str[2], "发表在报纸上的文献")
		self.literature_all_list["literature_in_newspaper"] = self.literature_list
		# 打印会议文献
		self.contents_literature(type_str[3], frame_str[3], "发表在会议上的文献")
		self.literature_all_list["literature_in_meetings"] = self.literature_list
		# 打印博硕文献
		self.contents_literature(type_str[4], frame_str[4], "发表在博硕上的文献")
		self.literature_all_list["literature_in_doctor"] = self.literature_list
		# 打印曾参考的文献
		self.contents_literature(type_str[5], frame_str[5], "曾参考的文献")
		self.literature_all_list["literature_in_reference"] = self.literature_list
		#print(self.literature_all_list)
		# 合作作者：分为同机构和不同机构
		# 同机构
		self.contents_cooperator(type_str[6], frame_str[6], 1)
		# 不同机构
		try:
			self.contents_cooperator(type_str[6], frame_str[6], 0)
		except:
			self.flag = 1
			print("不同机构合作者爬取失败...此处设为空列表...")

		# 打印获得的支持基金
		self.contents_fonds(type_str[7], frame_str[7])

if __name__ == '__main__':
	chrome_options= webdriver.ChromeOptions()
	chrome_options.add_argument('--no-sandbox')
	chrome_options.add_argument('--disable-gpu')
	chrome_options.add_argument('--headless')
	chrome_options.add_argument('--log-level=3')
	browser = webdriver.Chrome(chrome_options=chrome_options)
	driver = cnki_author_spider(browser,author_list[0])
	driver.open_author_page()
	driver.output_contents()
	driver.write_to_file()
	driver.get_all_sameauthor_url()
	for author in author_list[1:]:
		try:
			print('\n')
			driver.input_next_one(author)
			driver.open_author_page()
			driver.output_contents()
			driver.write_to_file()
			driver.get_all_sameauthor_url()
		except:
			print("该作者条目爬取失败，即将跳过爬取该作者...\n")
			time.sleep(1)
			# 12.13 记录下都有哪些作者爬取失败
			continue
	driver.quit()







