from fastapi import FastAPI
from fastapi.responses import JSONResponse
from bs4 import BeautifulSoup
import requests

app = FastAPI()

@app.post('/', summary="get price from webpage")
async def trackPrice(link : str):
    b = requests.get(link).text
    a = BeautifulSoup(b, "html.parser")
    c = a.select_one('.selling-price')
    d = c.span.text
    price = ''

    for item in d:
        if item.isnumeric():
            price += item
    
    return JSONResponse(status_code=200, content={'link' : price})