import requests
from bs4 import BeautifulSoup



def SinhagiriScrapper(link):
    """
    perpose : this is for scrappe data from sinhagiri website - product page
    output : False : scrape is not successfull | productData = scrape is successfull
    """
    pageResponce = requests.get(link)
    if pageResponce.status_code != 200:
        return False
    elif pageResponce.status_code == 200:
        page = pageResponce.text
        a = BeautifulSoup(page, "html.parser")
        # product code
        c = list(a.select('.product-sku'))
        product_code = c[1].text[11:]
        # product title
        product_title = a.select_one('.product-title').text
        # availability
        availability = True if a.select_one('.bg-success') != None else False
        try:
            dataList = list(a.select('.data'))
            price = dataList[1].text
        except:
            dataList = list(a.select('.selling-price'))
            price = dataList[0].text

        # image
        e = list(a.select_one('.product-slider__main-slider__item'))
        image = e[0].span.img['src']
        print(f'product code : {product_code} | product title : {product_title} | product availability {availability} | price : {price}')
        return {
            'title' : product_title,
            'availability' : availability,
            'code' : product_code,
            'price' : price,
            'image' : image
        }