import requests
from bs4 import BeautifulSoup
import csv


def create_bs(url):
    """Принимает ссылку на сайт и возвращает объект класса bs4"""
    response = requests.get(url=url)
    response.encoding = 'UTF-8'
    tables_soup = BeautifulSoup(response.text, 'html.parser')
    return tables_soup


# получаем ссылки на все товары: категории - страницы - товары, всего 160, без ручной прописки
soup = create_bs('http://parsinger.ru/html/index1_page_1.html')
categories = (link['href'] for link in soup.find('div', class_='nav_menu').find_all('a'))
pages = (link['href'] for category in categories for link in create_bs(url='http://parsinger.ru/html/' + category).find('div', class_='pagen').find_all('a'))
items = (code.find('a')['href'] for page in pages for code in create_bs(url='http://parsinger.ru/html/'+page).find_all('div', class_='sale_button'))


with open('all_items.csv', 'wt', encoding='utf-8') as file:
    writer = csv.writer(file, delimiter=';')
    headers = ['Наименование', 'Артикул', 'Бренд', 'Модель', 'Наличие', 'Цена', 'Старая цена', 'Ссылка на карточку с товаром']
    writer.writerow(headers)  # записали заголовки
    # поехали по товарам, создаём цикл и сразу записываем
    for item in items:
        item_url = 'http://parsinger.ru/html/' + item  # дальше ссылаемся на переменную, удалять не надо
        item_soup = create_bs(url=item_url)
        # генератор списков
        items_info = ([rows.find('p', id='p_header').text] +
                      [rows.find('p', class_='article').text.split(': ')[-1]] +
                      [li.text.split(':')[-1].strip() for li in rows.find_all('li')[:2]] +
                      [rows.find('span', id='in_stock').text.split(': ')[-1]] +
                      [rows.find('span', id='price').text] +
                      [rows.find('span', id='old_price').text] +
                      [item_url]
                      for rows in item_soup.find_all('div', class_='description'))
        for line in items_info:
            writer.writerow(line)
print('Файл all_items.csv создан. Слава Python!')
