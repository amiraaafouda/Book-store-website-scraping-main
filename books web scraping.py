import csv
import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import re


def StarConversion(value):
    if value == "One":
        return 1
    elif value == "Two":
        return 2
    elif value == "Three":
        return 3
    elif value == "Four":
        return 4
    elif value == "Five":
        return 5


# scrape oe book details############################
def scrape_book_details(driver):
    title = driver.find_element(By.XPATH, "//*[@id='content_inner']/article/div[1]/div[2]/h1")
    price = driver.find_element(By.XPATH, "//*[@id='content_inner']/article/div[1]/div[2]/p[1]")
    stock = driver.find_element(By.XPATH, "//*[@id='content_inner']/article/div[1]/div[2]/p[2]")
    stars = driver.find_element(By.XPATH, "//*[@id='content_inner']/article/div[1]/div[2]/p[3]").get_attribute("class")
    stock = int(re.findall("\d+", stock.text)[0])

    stars = StarConversion(stars.split()[1])

    try:
        description = driver.find_element(By.XPATH, "//*[@id='content_inner']/article/p")
        description = description.text
    except:
        description = None

    upc = driver.find_element(By.XPATH, "//*[@id='content_inner']/article/table/tbody/tr[1]/td")

    tax = driver.find_element(By.XPATH, "//*[@id='content_inner']/article/table/tbody/tr[5]/td")

    category_a = driver.find_element(By.XPATH, "//*[@id='default']/div/div/ul/li[3]/a")

    # all  of our interest into a dictionary r
    r = {
        "Title": title.text,
        "Category": category_a.text,
        "Stock": stock,
        "Stars": stars,
        "Price": price.text,
        "Tax": tax.text,
        "UPC": upc.text,
        "Description": description
    }

    # time.sleep(2)
    return r


def scrape_books_from_1page(driver, books_details):
    incategory = driver.find_elements(By.CLASS_NAME, "product_pod")

    links = []
    for i in range(len(incategory)):
        item = incategory[i]
        # get the href property = each book url
        a = item.find_element(By.TAG_NAME, "h3").find_element(By.TAG_NAME, "a").get_property("href")
        # Append the link to list links
        links.append(a)

    # Lets loop through each link to access the page of each book
    for link in links:
        # get one book url
        driver.get(url=link)

        r = scrape_book_details(driver)
        # append r to all details
        books_details.append(r)


def scrape_books_from_pages(driver):
    books_details = []

    for page in range(1, 51):
        try:
            if page % 5 == 0:
                write_in_csv(books_details)
                books_details = []
            driver.get(f"http://books.toscrape.com/catalogue/category/books_1/page-{page}.html")
            scrape_books_from_1page(driver, books_details)
        except:
            # Lets just close the browser if we run to an error
            driver.close()

    write_in_csv(books_details)
    time.sleep(3)
    driver.close()

def write_in_csv(books_details):
    df = pd.DataFrame(books_details)
    df.to_csv("all_pages.csv", mode='a', header=False)

if __name__ == '__main__':
    ser = Service(r"/home/hadeer/Desktop/ITI/data e&p/chromedriver/chromedriver")
    op = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=ser, options=op)

    scrape_books_from_pages(driver)


