import requests
from bs4 import BeautifulSoup

res = requests.get("https://books.toscrape.com/")
soup = BeautifulSoup(res.text,"html.parser")

categorias = soup.find("ul",class_="nav nav-list").find("li").find_all("li")
lista_categorias = []

for li in categorias:
    lista_categorias.append(li.text.strip())
    print(li.text.strip())

