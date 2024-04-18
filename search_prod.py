import requests
import Levenshtein
from telegram import InlineKeyboardButton
from typing import Any


def get_design_by_design(title: str, device: str) -> Any:
    if device == 'AirPods':
        url_point = ''.join([
            "https://store.tildacdn.com/api/getproductslist/?storepartuid",
            "=577145591471&recid=332389848&c=1692310007312&getparts=",
            "true&getoptions=true&slice=1&sort%5Bcreated%5D=desc&size=500"])

    elif device == 'MacBook':
        url_point = ''.join([
            "https://store.tildacdn.com/api/getproductslist/",
            "?storepartuid=101261849671&recid=332390199&c=1692309700873&getparts",
            "=true&getoptions=true&slice=1&sort%5Bcreated%5D=desc&size=500"])

    else:
        url_point = ''.join([
            "https://store.tildacdn.com/api/getproductslist/?storepartuid",
            "=488842231311&recid=345443903&c=1691240585349",
            "&getparts=true&getoptions=true&slice=1&size=500"])

    resp = requests.get(url_point)

    title_list = [i['title'] for i in resp.json()["products"]]

    title_similarity = []

    for i, word in enumerate(title_list):
        distance = Levenshtein.distance(title.lower(), word.lower())
        similarity = 1 - (distance / max(len(title), len(word)))
        title_similarity.append((similarity, word, i))
    title_similarity = sorted(title_similarity, reverse=True)
    if title_similarity[0][0] > 0.79:
        search_list = title_similarity[0]
        return resp.json()["products"][search_list[2]]
    else:
        return False


def get_model_by_design(prod_data: Any, prod_variant: str = 'prod_variants') -> Any:
    if prod_variant in prod_data:
        prod_variants = prod_data[prod_variant].replace('\n', ';').split(';')
        opt_price_list = [i.split('=+') for i in prod_variants]
        return opt_price_list
    else:
        return False


def get_case_type_by_design(prod_data: Any, prod_variant: str = 'prod_variants2') -> Any:
    if prod_variant in prod_data:
        prod_variants = prod_data[prod_variant].replace('\n', ';').split(';')
        opt_price_list = [i.split('=+') for i in prod_variants]
        return opt_price_list
    else:
        return False


def generate_button(var_list: Any, width: int = 3) -> list:
    def row_quantity(list: list, width: int) -> int:
        if len(list) % width == 0:
            return len(list)//width
        else:
            return (len(list)//width) + 1

    rows = row_quantity(var_list, width)
    buttons = []
    index = 0
    for i in range(rows):
        row = []
        for j in range(width):
            if index < len(var_list):
                row.append(InlineKeyboardButton(
                    var_list[index][0].replace('iPhone ', '')
                    .replace('AirPods ', '').replace('Macbook ', ''),
                    callback_data=var_list[index][0]))
                index += 1
        buttons.append(row)

    return buttons


def get_variants_price(prod_data: dict, prod_variant: str, dev: str) -> int:
    null = 0
    if prod_variant in prod_data:
        prod_variants = prod_data[prod_variant].replace('\n', ';').split(';')
        opt_price_list = [i.split('=+') for i in prod_variants]
        for i in opt_price_list:
            if len(i) > 1 and (dev in i):
                new_price = int(i[1])
                return new_price
        return null
    else:
        return null


def get_price(prod_data: dict, order_dict: dict) -> int:
    price = int(float(prod_data['price']))
    price += get_variants_price(prod_data, 'prod_variants', order_dict['model'])
    price += get_variants_price(prod_data, 'prod_variants2', order_dict['prod_case_type'])
    return price


def get_best_list() -> Any:
    url = ''.join([
        "https://store.tildacdn.com/api/getproductslist/?storepartuid=917658598071&recid=",
        "618675692&c=1691857338031&getparts=true&getoptions=true&slice=1&size=30"])
    resp = requests.get(url)
    best_prod_list = resp.json()["products"]
    best_tegs_list = []
    for i in best_prod_list:
        title = i['title'] + "\n"
        price = str(float(i['price'])) + ' грн' + "\n"
        link_for_link = i['editions'][0]['img']
        link = f"<a href='{link_for_link}'>Фото товару</a>"
        best_tegs_list.append(f'{title}{price}{link}')
    return best_tegs_list
