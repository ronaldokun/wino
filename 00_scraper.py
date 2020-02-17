# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.2.3
#   kernelspec:
#     display_name: wino
#     language: python
#     name: wino
# ---

# +
# default_exp crawler
# -

# # Crawler
# > This repository aims to explore the catalog available at wine.com.br, do some exploratory analysis in it and
# create initially a toy recommendation engine / wine classifier and pricing tool.

import scrapy
from bs4 import BeautifulSoup as soup
from fire import Fire
from nbdev.showdoc import *
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor

prefix = "https://wine.com.br"
url_short = "https://www.wine.com.br/browse.ep?cID=100851&exibirEsgotados=true&listagem=horizontal&sorter=featuredProducts-desc&filters=cVINHOS"
# -

CATALOG = "//article/div[2]"
NEXT = "/html/body/div[6]/div/div[2]/div[2]/div/div[4]/div"

link_extract = LxmlLinkExtractor(restrict_text="Próxima >>")


# Create the Spider class
class WineSpider(scrapy.Spider):
    name = "winespider"

    def start_requests(self):
        yield scrapy.Request(url=url_short, callback=self.parse_page)

    def parse_page(self, response):
        wine_list = response.xpath(CATALOG)
        for block in wine_list:
            yield {
                "wine": block.css('div > a::attr("title")').get(),
                "link": prefix + block.css('div > a::attr("href")').get(),
            }

        next_page = response.xpath(f"//a[./text()='Próxima >>']/@href").get()
        # next_page = response.xpath("//a[contains(text(), 'Próxima')]/@href").get()
        if next_page is not None:
            yield response.follow(next_page, self.parse_page)

    # Second parsing method
    def parse_pages(self, response):
        crs_title = response.xpath('//h1[contains(@class,"title")]/text()')
        crs_title_ext = crs_title.extract_first().strip()
        ch_titles = response.css("p.course__description::text")
        ch_titles_ext = [t.strip() for t in ch_titles.extract()]
        dc_dict[crs_title_ext] = ch_titles_ext


# +
# Initialize the dictionary **outside** of the Spider class
dc_dict = dict()


def crawl():
    # Run the Spider
    process = CrawlerProcess()
    process.crawl(WineSpider)
    process.start()


if __name__ == "__main__":
    Fire(crawl)
# -
