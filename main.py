from ntpath import join
from random import randint
from time import sleep, time
import requests, lxml
from bs4 import BeautifulSoup
import os
import json

headers = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0"
}


def get_data(url):

    r = requests.get(url=url, headers=headers)

    # with open("grades.html", "w", encoding='utf-8') as file:
    #     file.write(r.text)

    with open("grades.html", encoding="utf-8") as file:
        src = file.read()

    soup_main = BeautifulSoup(src, "lxml")
    it = 1
    grades = soup_main.find("div", class_="select-class").find_all("a")

    for grade in grades:
        grade_url = "https://www.okulyk.kz" + grade.get("href")
        grade_no = grade_url.split("/")[-1]
        folder_name = f"grades/{grade_no}"

        req = requests.get(grade_url, headers)

        if os.path.exists(folder_name):
            print("Folder exists")
        else:
            os.mkdir(folder_name)

        with open(f"{folder_name}/{grade_no}.html", "w",
                  encoding="utf-8") as file:
            file.write(req.text)

        with open(f"{folder_name}/{grade_no}.html", encoding='utf-8') as file:
            source = file.read()

        print(f"{it}...")
        it += 1
        sleep(2)

        soup_grade = BeautifulSoup(source, "lxml")
        books = soup_grade.find("div",
                                class_="book-list").find_all("a",
                                                             class_="book")

        grade_data_list = []
        for book in books:
            book_url = book.get("href")

            req_book = requests.get(url=book_url, headers=headers)
            soup_book = BeautifulSoup(req_book.text, "lxml")
            book_title = soup_book.find("h1",
                                        class_="book-title-h1").text.split()
            book_title = " ".join(book_title[:-4])
            t_data = soup_book.find("div", class_="book-info-left").find(
                "table").find("tbody").find_all("td")[:-2]

            book_category = t_data[1].text
            book_year = t_data[9].text
            # book_author = t_data[5].text,
            # book_grade = t_data[3].text,
            # book_publisher = t_data[7].text.strip(),
            try:
                book_pdf = soup_book.find("a",
                                          string="Скачать PDF").get("href")
                book_pdf = f"https://www.okulyk.kz{book_pdf}"
            except Exception:
                book_pdf = "Недоступен"

            if len(t_data) == 12:
                book_page = "-"
                book_lan = t_data[11].text
            elif len(t_data) == 14:
                book_page = t_data[11].text
                book_lan = t_data[13].text

            book_info = {
                "Класс": t_data[3].text,
                "Предмет": book_category,
                "Название": book_title,
                "Авторы": t_data[5].text,
                "Издательство": t_data[7].text.strip(),
                "Год": book_year,
                "Страниц": book_page,
                "Язык": book_lan,
                "PDF": book_pdf,
                "URL": book_url
            }
            grade_data_list.append(book_info)

        with open(f"{folder_name}/{grade_no}.json", "a",
                  encoding='utf-8') as file:
            json.dump(grade_data_list, file, indent=4, ensure_ascii=False)


def main():
    get_data("https://www.okulyk.kz/")


if __name__ == "__main__":
    main()