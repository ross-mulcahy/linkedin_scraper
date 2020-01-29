""" filename: script.py """

#https://www.linkedin.com/pulse/how-easy-scraping-data-from-linkedin-profiles-david-craven/

import parameters
import csv
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from parsel import Selector
from pprint import pprint
import pymongo
import certifi
import urllib3

http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',ca_certs=certifi.where())


client = pymongo.MongoClient("mongodb+srv://"+mongo_db_user+":"+mongo_db_password"@"+mongo_db_url+"?retryWrites=true&w=majority&ssl_cert_reqs=CERT_NONE")
db = client.linkedin
collection = db.people

serverStatusResult=db.command("serverStatus")
pprint(serverStatusResult)

def strip_list_noempty(mylist):
    newlist = (item.strip() if hasattr(item, 'strip') else item for item in mylist)
    return [item for item in newlist if item != '']

# function to ensure all key data fields have a value
def validate_field(field):# if field is present pass
	if field:pass
	# if field is not present print text
	else:
		field = 'No results'

	return field

driver = webdriver.Chrome(chrome_driver)
driver.get('https://www.linkedin.com/login')

#writer = csv.writer(open(parameters.file_name, 'w'))

# writerow() method to the write to the file object
#writer.writerow(['Name','Job Title','Company','College', 'Location','URL'])

username = driver.find_element_by_id('username')
username.send_keys(parameters.linkedin_username)
sleep(0.5)

password = driver.find_element_by_id('password')
password.send_keys(parameters.linkedin_password)
sleep(0.5)

sign_in_button = driver.find_element_by_xpath('//*[@type="submit"]')
sign_in_button.click()
sleep(0.5)

initial=100

while(initial<200):

	driver.get('https://www.linkedin.com/search/results/people/?keywords=customer%20success%20manager&origin=SWITCH_SEARCH_VERTICAL&page='+str(initial))
	print('https://www.linkedin.com/search/results/people/?keywords=customer%20success%20manager&origin=SWITCH_SEARCH_VERTICAL&page='+str(initial))
	sleep(2)

	#search_query = driver.find_element_by_name('q')
	#search_query.send_keys(parameters.search_query)
	#sleep(0.5)

	#search_query.send_keys(Keys.RETURN)
	#sleep(3)
	

	actions = ActionChains(driver)
	for _ in range(8):
		actions.send_keys(Keys.SPACE).perform()
		sleep(1)

	sleep(2)

	sel1 = Selector(text=driver.page_source)

	linkedin_urls = sel1.xpath("//ul[@class='search-results__list list-style-none ']/li/div/div[@class='search-result__wrapper']/div[@class='search-result__info pt3 pb4 ph0']/a/@href").getall()
	print(linkedin_urls)
	pprint(linkedin_urls)
	#linkedin_urls = [url.get_attribute("href") for url in linkedin_urls]
	#pprint(linkedin_urls)
	#exit()

	#linkedin_urls
	sleep(0.5)

	initial=initial+1
	# For loop to iterate over each URL in the list
	for linkedin_url in linkedin_urls:

		

		linkedin_url="https://www.linkedin.com"+linkedin_url

		check=0
		check = collection.count_documents({ "url": linkedin_url })

		if(check>0):

			print("Profile already exists")
		else:

			# get the profile URL
			driver.get(linkedin_url)

			# add a 5 second pause loading each URL
			sleep(2)

			actions = ActionChains(driver)
			for _ in range(8):
				actions.send_keys(Keys.SPACE).perform()
				sleep(1)


			sleep(2)	

			#driver.find_element_by_css_selector(".pv-skill-categories-section")	
			
			#driver.find_element_by_css_selector(".pv-profile-section__card-action-bar").click()

			#open_button = driver.find_element_by_xpath("//*[contains(@class, 'pv-profile-section__card-action-bar')]")
			#open_button.click()
			sleep(2)

			# assigning the source code for the webpage to variable sel
			sel = Selector(text=driver.page_source)

			# xpath to extract the text from the class containing the name
			name = sel.xpath("//div[@class='flex-1 mr5']/ul[@class='pv-top-card-v3--list inline-flex align-items-center']/li[@class='inline t-24 t-black t-normal break-words']/text()").get()

			if name:
			   name = name.strip()

			# xpath to extract the text from the class containing the job title
			job_title = sel.xpath("//div[@class='ph5 pb5']/div[@class='display-flex mt2']/div[@class='flex-1 mr5']/h2[@class='mt1 t-18 t-black t-normal']/text()").get()

			if job_title:
			   job_title = job_title.strip()


			# xpath to extract the text from the class containing the company
			company = sel.xpath("//ul[@class='pv-top-card-v3--experience-list']/li[@class='pv-top-card-v3--experience-list-item'][1]/span/text()").get()

			if company:
			   company = company.strip()


			# xpath to extract the text from the class containing the college
			college = sel.xpath("//ul[@class='pv-top-card-v3--experience-list']/li[@class='pv-top-card-v3--experience-list-item'][2]/span/text()").get()

			if college:
			   college = college.strip()


			# xpath to extract the text from the class containing the location
			location = sel.xpath("//ul[@class='pv-top-card-v3--list pv-top-card-v3--list-bullet mt1']/li[@class='t-16 t-black t-normal inline-block']/text()").get()

			if location:
			   location = location.strip()

			# xpath to extract the text from the class containing the location
			skills = sel.xpath("//*[contains(@class, 'pv-skill-category-entity__name-text')]/text()").getall()

			jobs = sel.xpath("//div[@class='pv-entity__summary-info pv-entity__summary-info--background-section mb2']/h3[@class='t-16 t-black t-bold']/text()").getall()

			linkedin_url = driver.current_url

			# validating if the fields exist on the profile
			name = validate_field(name)
			job_title = validate_field(job_title)
			company = validate_field(company)
			college = validate_field(college)
			location = validate_field(location)
			linkedin_url = validate_field(linkedin_url)
			skills = strip_list_noempty(skills)
			jobs = strip_list_noempty(jobs)

			#name = validate_field(name)
			# printing the output to the terminal
			print('\n')
			print('Name: ' + name)
			print('Job Title: ' + job_title)
			print('Company: ' + company)
			print('College: ' + college)
			print('Location: ' + location)
			print('URL: ' + linkedin_url)
			print('\n')

			post = {
				"name" : name,
				"job title" : job_title,
				"company" : company,
				"college" : college,
				"location" : location,
				"url" : linkedin_url,
				"skills" : skills,
				"jobs" : jobs
			}
			try:
				post_id = collection.insert_one(post).inserted_id
				print(post_id)
			except pymongo.errors.DuplicateKeyError:
				# skip document because it already exists in new collection
				print("Already exists in table")
				continue

# terminates the application
driver.quit()
