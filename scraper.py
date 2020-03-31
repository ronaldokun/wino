# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.4
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
COUNT = 434
#url_short = "https://www.wine.com.br/browse.ep?cID=100851&exibirEsgotados=true&listagem=horizontal&sorter=featuredProducts-desc&filters=cVINHOS"
url_short = "https://www.wine.com.br/browse.ep?cID=100851&exibirEsgotados=true&pn=1&listagem=horizontal&sorter=featuredProducts-desc&filters=cVINHOS" 
url_next = "https://www.wine.com.br/browse.ep?cID=100851&exibirEsgotados=true&pn={page}&listagem=horizontal&sorter=featuredProducts-desc&filters=cVINHOS"

# +
TIPOS = {'Branco', 'Espumante', 'Frisante', 'Licoroso', 'Rosé', 'Tinto'}
PAISES = {'África do Sul', 'Alemanha', 'Argentina', 'Austrália', 'Brasil', 'Chile'
          'China', 'Espanha', 'Estados Unidos', 'França', 'Hungria', 'Itália', 'Líbano'
          'Nova Zelândia', 'Portugal', 'Uruguai', 'Grécia', 'Marrocos'}

KEYS = {'Tipo', 'Uvas', 'Origem', 'Vinícola', 'Teor Alcoólico', 'Amadurecimento', 'Safra','Classificação', 'Visual', 
        'Olfativo', 'Gustativo', 'Temperatura de serviço', 'Potencial de guarda', 'Decantação', 'Harmonização'}

OTHER = {'Vinícola', 'Teor Alcoólico', 'Amadurecimento', 'Safra','Classificação', 'Visual', 
        'Olfativo', 'Gustativo', 'Temperatura de serviço', 'Potencial de guarda', 'Decantação', 'Harmonização'}


# +
class CatalogClassic(scrapy.Spider):
    name = "catalog_classic"
    #url = url_short
    i=1

    def start_requests(self):
        yield scrapy.Request(url=url_short, callback=self.parse_page)

    def parse_page(self, response, count=i):
        
        wine_list = response.xpath(CATALOG)
        for block in wine_list:
            tag = soup(block.get(), 'lxml')
            key = []
            val = []

            link = prefix + block.css('div > a::attr("href")').get()

            key += ["link"]
            val += [link]

            title = tag.find('h2')
            
            key.append("Nome")

            if title:
                val.append(title.string)
            else:
                val.append(None)
                
            key.append("País")
            
            country = tag.find('div', class_="Country")
            
            if country:
                val.append(country.string)
            else:
                val.append(None)

            precos = tag.find_all(class_='Price-raw')
            
            key.extend(['Preço_Sócio', 'Preço_Normal'])

            if len(precos) >= 2:
                precos = sorted(list(set([float(p.string) for p in precos])))
                val.extend(precos[0:2])
            else:
                val.extend([None]*2)


            avaliação = tag.find("evaluation-tag")
                       
            key.append("Pontuação")

            if avaliação:
                val.append(float(avaliação[':evaluation']))
            else:
                val.append(None)
                       
                       
            key.append("Avaliações")
 
            rating = tag.find('a', class_='Rating-count', string=True)

            if rating:
                rating = rating.string.replace("(", "")
                rating = rating.replace(")", "")
                val.append(rating)
                
            parse_vinho = partial(self.ficha_tecnica, dict_=dict(zip(key, val)))
                
            yield response.follow(link, parse_vinho)
                

        count +=1
        next_page = url_next.format(page=count)
        parse_next = partial(self.parse_page, count=count)
        if count <= COUNT:
            yield response.follow(next_page, parse_next)
            
    # Second parsing method
    def ficha_tecnica(self, response, dict_):
        page = response.xpath('/html').get()
        tag = soup(page, 'lxml')
        #key = []
        #val = []
        
        
        v = tag.find(class_="somelier__description")
        dict_['somelier'] = v.string.strip() if v else None
        
        rights = tag.find_all('div', class_="Right")
        
#         keys = []
#         vals = []
#         for t in rights:
#             keys.append(t.attrs.get('dt'))
#             vals.append(t.attrs.get('dd'))
        
        keys = [t.string for t in tag.find_all('dt')]
        vals = [t.string for t in tag.find_all('dd')]
        
        dict_ = {**dict_, **{k:None for k in KEYS}}
        
        for k,v in zip(keys, vals):
            if k in TIPOS:
                dict_['Tipo'] = k
                dict_['Uvas'] = v
            elif k in PAISES:
                dict_['Origem'] = f'{k}-{v}'
            elif k in OTHER:
                dict_[k] = v                
        
        yield dict_

# +
#export
# class CatalogFaster(scrapy.Spider):
#     name = "catalog"
#     start_urls = [url_short] + [url_next.format(page=i) for i in range(2, 85)]
    

#     def parse(self, response):
#         wine_list = response.xpath(CATALOG)
#         for block in wine_list:
#             tag = soup(block.get(), 'lxml')
#             key = []
#             val = []
            
#             key += ["link"]
#             val += [prefix + block.css('div > a::attr("href")').get()]
            
#             title = tag.find('h2')
            
#             if title:
#                 key.append("Nome")
#                 val.append(title.string)

#             precos = tag.find_all(class_='Price-raw')        

#             if len(precos) >= 2:
#                 precos = sorted(list(set([float(p.string) for p in precos])))
#                 key.append('Preço_Sócio')
#                 val.append(precos[0])
#                 key.append('Preço_Normal')
#                 val.append(precos[1])
            
                
#             avaliação = tag.find("evaluation-tag")
            
#            # print(f"Avaliação: {avaliação.attrs}")
#             if avaliação:
#                 key.append("Pontuação")
#                 val.append(float(avaliação[':evaluation']))
                

#             rating = tag.find('a', class_='Rating-count', string=True)
            
#             if rating:
#                 key.append("Avaliações")
#                 rating = rating.string.replace("(", "")
#                 rating = rating.replace(")", "")
#                 val.append(rating)
        
#             yield dict(zip(key, val))
            
#     # Second parsing method
#     def ficha_tecnica(self, key, val, tag):
#         tag = soup(tag, 'lxml')
#         key = []
#         val = []
        
#         v = tag.find(class_="somelier__description")
#         key.append('somelier')
#         val.append(v.string.strip() if v else '')
        
#         keys = [t.string for t in tag.find_all('dt')]
#         vals = [t.string for t in tag.find_all('dd')]
        
               
#         for k,v in zip(keys, vals):
#             if k in TIPOS:
#                 key.append('tipo')
#                 val.append(k)
#             elif k in PAISES:
#                 key.append('origem')
#                 val.append(f'{k}-{v}')
#             else:
#                 key.append(k)
#                 val.append(v)
                
        
#         return dict(zip(key, val))

# +
def crawl():
    # Run the Spider
    process = CrawlerProcess()
    process.crawl(CatalogClassic)
    process.start()


if __name__ == "__main__":
    Fire(crawl)
# -


