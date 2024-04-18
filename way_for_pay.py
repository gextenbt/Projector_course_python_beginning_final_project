import requests
import hmac

import os
import dotenv
dotenv.load_dotenv()


# створення Підпису запиту merchantSignature
def hmac_md5(key: str, s: str) -> str:
    return hmac.new(key.encode('utf-8'), s.encode('utf-8'), 'MD5').hexdigest()


API_ENDPOINT = "https://api.wayforpay.com/api"


def get_wfp_link(orderReference: str, productName: str, productPrice: int | float) -> str:
    # Данні для створення запиту https://wiki.wayforpay.com/uk/view/608996852
    key = str(os.getenv("SECRETKEY_WFP"))
    merchantAccount = str(os.getenv("merchantAccount"))
    orderDate = 1691366400
    merchantDomainName = str(os.getenv("merchantDomainName"))
    # orderReference = "12dew34560000111" # берем з ордеру
    # productName = "Iphone case" # берем з ордеру
    productCount = 1  # берем з ордеру
    # productPrice = 1000 # берем з ордеру
    amount = productPrice
    currency = "UAH"

    s_invoice = f'{merchantAccount};{merchantDomainName};{orderReference};'\
        f'{orderDate};{amount};{currency};{productName};{productCount};{productPrice}'
    merchantSignature = hmac_md5(key, s_invoice)

    data = {
        "transactionType": "CREATE_INVOICE",
        "merchantAccount": merchantAccount,
        "merchantDomainName": merchantDomainName,
        "merchantSignature": merchantSignature,
        "apiVersion": 1,
        # "serviceUrl": "http://serviceurl.com",
        "orderReference": orderReference,
        "orderDate": orderDate,
        "amount": amount,
        "currency": currency,
        "productName": [productName],
        "productPrice": [productPrice],
        "productCount": [productCount],
        }
    resp = requests.post(url=API_ENDPOINT, json=data)
    return resp.json()['invoiceUrl']
