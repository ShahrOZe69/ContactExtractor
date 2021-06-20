from selenium import webdriver
import requests
import re
import time
import pandas as pd
from bs4 import BeautifulSoup

PATH="D:\Py\Selenium\chromedriver.exe"

option = webdriver.ChromeOptions()
chrome_prefs = {}
option.experimental_options["prefs"] = chrome_prefs
option.add_argument('--disable-gpu')
option.add_argument('--headless')
chrome_prefs["profile.default_content_settings"] = {"images": 2}
chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
driver = webdriver.Chrome(PATH,chrome_options=option)

def open_txt(txt):
	file =open(txt,encoding='utf-8').readlines()
	contents=[i.strip() for i in file]
	return contents

def getPageSource(link):
	try:
		driver.set_page_load_timeout(120)
		driver.get(link)
		driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
	except Exception as e:
		print(e)
		return 'DEAD'
	return driver.page_source	


def extractSocialMedias(page_source,domain):
	social_media={}
	soup = BeautifulSoup(page_source,features='lxml')
	links=soup.find_all(href=True)
	for link in links:
		if 'linkedin.com/' in link['href']:
			social_media['LinkedIn']=link['href']
		if 'twitter.com/' in link['href']:
			social_media['Twitter']=link['href']	
		if 'facebook.com/' in link['href']:
			social_media['Facebook']=link['href']
	#second Search		
	for link in links:
		if '/linkedin' in link['href'] and 'LinkedIn' not in social_media.keys():
			social_media['LinkedIn']=domain+link['href']
		if '/twitter' in link['href'] and 'Twitter' not in social_media.keys():
			social_media['Twitter']=domain+link['href']
		if '/facebook' in link['href'] or '/fb' in link['href'] and 'Facebook' not in social_media.keys():
			social_media['Facebook']=domain+link['href']
	return social_media		






def extractEmail(page_source,domain):
	email_dic={}
	soup = BeautifulSoup(page_source,features='lxml')
	links=soup.find_all(href=True)
	for link in links:
		if 	'mailto:'in link['href'] and 'Email' not in email_dic.keys() and '%' not in link['href']:
			if domain in link['href']:
				email_dic['Email']=link['href'][7:]
				return email_dic		
	for link in links:
		if 	'mailto:'in link['href'] and 'Email' not in email_dic.keys() and '%' not in link['href']:
			if link['href'][7:] !='':
				email_dic['Email'] = link['href'][7:]
				return email_dic			
	#third Search
	if not 'Email' in email_dic.keys():
		email=re.search(r'[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}',str(page_source))
		if email:
			email_dic['Email']=email.group().strip()		
	return email_dic				




def getContactLink(page_source,domain):
	soup = BeautifulSoup(page_source,features='lxml')
	links=soup.find_all(href=True)
	for link in links:
		if 'contact' in link['href'].lower() and '#' not in link['href']:
			if domain not in link['href']:
				link['href']=f'http://www.{domain}'+link['href'][link['href'].find('/'):]	
			return link['href']
				
def extractPhoneNumber(page_source):
	tel={}
	soup = BeautifulSoup(page_source,features='lxml')
	links=soup.find_all(href=True)
	for link in links:
		if 'tel:' in link['href'] or 'Tel:' in link['href']:
			if link['href'][4:] !='':
				tel['Telephone']=link['href'][4:]
				return tel
	#second search using Regex
	if 'Telephone' not in tel.keys():
		Regex=r'\s*(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(?: *x(\d+))?\s*'
		tel_num=re.search(Regex,soup.text)
		if tel_num:
			tel['Telephone']=tel_num.group().strip()
		return tel			


def extractContacts(page_source,domain):
	contacts={}
	contacts['Name']=''.join(domain.split('.')[:-1])
	contacts['URL']=f'http://{domain}'
	contact_link=getContactLink(page_source,domain)	
	contacts.update(extractSocialMedias(page_source,domain))
	contacts.update(extractEmail(page_source,domain))
	contacts.update(extractPhoneNumber(page_source))
	if contact_link:
		source=getPageSource(contact_link)
		contacts.update(extractSocialMedias(source,domain))
		contacts.update(extractEmail(source,domain))
		contacts.update(extractPhoneNumber(source))			
	return contacts
print(extractContacts(getPageSource('http://toza.co'),'toza.co'))	
domains = open_txt('websiteList.txt')
results=[]
for domain in domains[100:200]:
	source=getPageSource(f'http://{domain}')
	if source!='DEAD':
		result=extractContacts(source,domain)
	else:
		continue	
	print(result)
	if result:
		results.append(result)
df=pd.DataFrame(results)
df.to_excel('contactsRevised2.xlsx',index=False)

driver.quit()
