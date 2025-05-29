import schedule
import time
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from bs4 import BeautifulSoup
import requests
from bson import ObjectId
from random import randint


load_dotenv()

# database init 
mongo = MongoClient(os.getenv('mongo'))
cluster = mongo['price_platform']
product = cluster['product']
tracks = cluster['tracks']

# brevo email service
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = os.getenv('bravo')
api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))



# send scrape summery for admin 
def ScrapSummery(produtctCount, successfullScrape, failedScrape, priceChange, priceChangeUpdate, priceChangeUpdateMissing, startTime, endTime):
    sender = {"name":"gayashan gamage","email":"gayashan.randimagamage@gmail.com"}
    to = [{"name":"gamage","email":"s92065811@ousl.lk"}]
    subject = 'Sinhagiri scrape summery'
    headers = {"Some-Custom-Name":"unique-id-1234"}
    param = {'start_time' : startTime, 'end_time' : endTime, 'product_count' : produtctCount, 'successfully_scraped' : successfullScrape, 'failed_scraped' : failedScrape, 'price_change' : priceChange, 'update_price_change' : priceChangeUpdate, 'unfinished_price_change' : priceChangeUpdateMissing}
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, headers=headers, sender=sender, subject=subject, template_id=5, params=param)
    api_instance.send_transac_email(send_smtp_email)
    print('email change')


# scrape product 
# return price and availability only
def ProductScrape(link):
    """
    1 - unseccssfull scrape 
    """
    b = requests.get(link)
    if b.status_code != 200:
        return 0
    else:
        a = BeautifulSoup(b.text, "html.parser")
        
        # availability
        availability = a.select_one('.bg-success').text
        # price 
        try:
            b = list(a.select('.data'))
            price = b[1].text
        except:
            b = list(a.select('.selling-price'))
            price = b[0].text

        # convert text price in to int
        newPrice = ''
        for i in price:
            if(i.isnumeric()):
                newPrice += i

        # return new data
        return {
            'availability' : availability,
            'price' : int(newPrice),
            }


# scrape all product and update acordingly 
def ScrapProduct():
    # get all product from database
    allProduct = list(product.find({}, {'link' : 1, 'price' : 1}))
    # scrap summery data
    startTime = datetime.now()
    produtctCount = len(allProduct)
    successfullScrape = 0
    failedScrape = 0
    priceChange = 0
    priceChangeUpdate = 0
    priceChangeUpdateMissing = 0

    # iterate over all product
    for item in allProduct:
        print('scrapping ...')
        item['_id'] = str(item['_id'])
        
        # scrap product
        currentData = ProductScrape(item['link'])
        # check scrap output
        if currentData == 0:
            failedScrape += 1
            continue
        else:
            successfullScrape += 1
            # compaire product details
            if item['price'] != currentData['price'] :
                priceChange += 1
                update = product.update_one({'_id' : ObjectId(item['_id'])}, { '$set' : {'price' : currentData['price'], 'last update' : datetime.now(), 'availability' : currentData['availability']}})
                if update.modified_count == 1:
                    priceChangeUpdate += 1
                else:
                    priceChangeUpdateMissing += 1
        
        # waiting time
        sleepTime = randint(8, 20)
        time.sleep(sleepTime)

    endTime = datetime.now()
    # send scrape summery 
    ScrapSummery(produtctCount, successfullScrape, failedScrape, priceChange, priceChangeUpdate, priceChangeUpdateMissing, startTime.strftime('%H:%M:%S'), endTime.strftime('%H:%M:%S'))



# get all product ( except untrack and alredy notified ) and check price match
def PriceMatch():
    # get all track products 
    allTrackes = tracks.find({})
    
    # analytics variables 
    userCount = len(allTrackes)
    mailSentCount = 0
    priceMatchCount = 0
    priceMatchProducts = []

    # type conversion 
    for item in allTrackes:
        item['_id'] = str(item['_id'])
        # for i in item:
        #     i['product_id'] = str(i['product_id'])
        
        # get current product price if mail-send is false
        if(i['send'] == False):
            productDetails = product.find_one({'_id' : i['product_id']}, {'last update' : 0, '_id' : 0})
            # check whether price is eaqul or not
            if(productDetails['price'] == i['price']):
                priceMatchCount += 1
                priceMatchProducts.append(productDetails)

        if(len(priceMatchProducts) >= 1):
            mailSentCount += 1
            PriceUpdateMail()

    UserMailSummery(userCount, priceMatchCount, mailSentCount)


# send mail for users 
def PriceUpdateMail():
    pass


# send email summery for admin
def UserMailSummery():
    pass


# schedule function 
# schedule.every().day.at("15:50").do(ScrapProduct)
# schedule.every().day.at("11:00").do(PriceMatch)

# run schedule functions 
# while True:
#     schedule.run_pending()

PriceMatch()