# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.2
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
from fire import Fire
from nbdev.showdoc import *
from scrapy.crawler import CrawlerProcess
from functools import partial
from bs4 import BeautifulSoup as soup

CATALOG = "//article"
NEXT = "/html/body/div[6]/div/div[2]/div[2]/div/div[4]/div"
prefix = "https://wine.com.br"
#url_short = "https://www.wine.com.br/browse.ep?cID=100851&exibirEsgotados=true&listagem=horizontal&sorter=featuredProducts-desc&filters=cVINHOS"
url_short = "https://www.wine.com.br/browse.ep?cID=100851&exibirEsgotados=false&pn=1&listagem=horizontal&sorter=featuredProducts-desc&filters=cVINHOS" 
url_next = "https://www.wine.com.br/browse.ep?cID=100851&exibirEsgotados=false&pn={page}&listagem=horizontal&sorter=featuredProducts-desc&filters=cVINHOS"


class CatalogClassic(scrapy.Spider):
    name = "catalog_classic"
    #url = url_short
    i=1

    def start_requests(self):
        yield scrapy.Request(url=url_short, callback=self.parse_page)

    def parse_page(self, response, count=i):
        wine_list = response.xpath(CATALOG)
        for block in wine_list:
            yield {
                "wine": block.css('div > a::attr("title")').get(),
                "link": prefix + block.css('div > a::attr("href")').get(),
                "país": block.xpath('div[2]/div[1]/div/span').get()
            }
        #/html/body/div[5]/div/div[2]/div[2]/div/div[3]/ul/li[1]/article/div[2]/div[2]/div[1]/div/span
        #next_page = response.xpath(f"//a[./text()='Próxima >>']/@href").get()
        count +=1
        next_page = url_next.format(page=count)
        parse_next = partial(self.parse_page, count=count)
        if count <= 431:
            yield response.follow(next_page, parse_next)
        

    # Second parsing method
    def parse_pages(self, response):
        crs_title = response.xpath('//h1[contains(@class,"title")]/text()')
        crs_title_ext = crs_title.extract_first().strip()
        ch_titles = response.css("p.course__description::text")
        ch_titles_ext = [t.strip() for t in ch_titles.extract()]
        dc_dict[crs_title_ext] = ch_titles_ext


#export
class CatalogFaster(scrapy.Spider):
    name = "catalog"
    start_urls = [url_short] + [url_next.format(page=i) for i in range(2, 85)]
    

    def parse(self, response):
        wine_list = response.xpath(CATALOG)
        for block in wine_list:
            tag = soup(block.get(), 'lxml')
            key = []
            val = []
            
            title = tag.find('h2')
            
            if title:
                key.append("Nome")
                val.append(title.string)

            precos = tag.find_all(class_='Price-raw')        

            if len(precos) >= 2:
                precos = sorted(list(set([float(p.string) for p in precos])))
                key.append('Preço_Sócio')
                val.append(precos[0])
                key.append('Preço_Normal')
                val.append(precos[1])
            #elif len(precos) == 2:
            #    precos = sorted([float(p.string) for p in precos])
#                 key.append('Preço_Sócio')
#                 val.append(precos[0])
#                 key.append('Preço_Normal')
#                 val.append(precos[1])
                
            
                
            avaliação = tag.find("evaluation-tag")
            
           # print(f"Avaliação: {avaliação.attrs}")
            if avaliação:
                key.append("Pontuação")
                val.append(float(avaliação[':evaluation']))
                

            rating = tag.find('a', class_='Rating-count', string=True)
            
            if rating:
                key.append("Avaliações")
                rating = rating.string.replace("(", "")
                rating = rating.replace(")", "")
                val.append(rating)
        
            yield dict(zip(key, val))
    # Second parsing method
    def parse_pages(self, response):
        crs_title = response.xpath('//h1[contains(@class,"title")]/text()')
        crs_title_ext = crs_title.extract_first().strip()
        ch_titles = response.css("p.course__description::text")
        ch_titles_ext = [t.strip() for t in ch_titles.extract()]
        dc_dict[crs_title_ext] = ch_titles_ext


# +
def crawl():
    # Run the Spider
    process = CrawlerProcess()
    process.crawl(CatalogFaster)
    process.start()


if __name__ == "__main__":
    Fire(crawl)
