import requests
from bs4 import BeautifulSoup


def get_html(url):
    response = requests.get(url)
    return response.text


def get_dates(html):
    soup = BeautifulSoup(html, 'lxml')
    get_data_div = soup.find('div', class_='row lineNews')
    return get_data_div


def get_every_date(html):
    get_list_movies = html.find_all('div', class_='one')
    list_auto = []
    for movie in get_list_movies:
        # try:
        #     photo = movie.find('img', class_='picture_image').get('data-picture')
        # except:
        #     photo = ""
        try:
            title = movie.find('span').text
        except:
            title = ''


        data = {'title': title.replace('\n', '').strip()}
                # 'photo': photo}
        list_auto.append(data)
    return list_auto


def pars():
    akg_url = 'https://24.kg/sport/'
    html = get_html(akg_url)
    html = get_dates(html)
    list_ = get_every_date(html)
    return list_