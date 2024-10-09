from bs4 import BeautifulSoup
import requests


class WikiLib:
    def __init__(self, url: str):
        self.URL = url
        page = requests.get(self.URL)
        self.soup = BeautifulSoup(page.text, "html.parser")

    def get_name(self):
        name = self.soup.find(class_="mw-page-title-main")
        return name.text

    def get_text(self):
        strings = ""
        for el2 in self.soup.findAll("p"):
            strings += el2.text
        return strings

    def get_picture(self):
        try:
            img = self.soup.find("img", class_="mw-file-element")
            img_link = "https:" + img['src']
            return img_link
        except:
            return "Not image"

    def get_infobox(self):
        strs = ""
        for i in self.soup.findAll("tbody"):
            strs += i.text
        return strs


    def get_main_picture(self):
        try:
            img_div = self.soup.find("td", class_="infobox-image")
            img = img_div.find("img", class_="mw-file-element")
            img_link = "https:" + img['src']
            return img_link
        except:
            return "Not image"

    def get_all_pictures(self):
        try:
            pics = []
            for i in self.soup.findAll("img" , class_="mw-file-element"):
                link = "https:" + i['src']
                if type(link) is str:
                    pics.append(link)
                else:
                    pass
            return pics
        except:
            return "Not images"

    def get_links(self):
        for i in self.soup.findAll("a", class_="external text"):
            print(i.text)
            print(self.soup.find("a", class_="external text").get('href'))

    def get_self_link(self, lang):
        self_link = self.soup.find("li", class_="selected mw-list-item")
        link = self_link.find("a")
        if lang == 1:
            return "https://ru.wikipedia.org/" + link.get('href')
        elif lang == 0:
            return "https://en.wikipedia.org/" + link.get('href')
