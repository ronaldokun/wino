# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.3
#   kernelspec:
#     display_name: deepfake
#     language: python
#     name: deepfake
# ---

# +
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup as soup
from pprint import pprint as pp
from itertools import tee
import scrapy
from fire import Fire
from scrapy.crawler import CrawlerProcess
DATA = Path.cwd() / 'data'
PAGE = '.gr__wine_com_br'
FICHA = '.TechnicalDetails'
URL = 'https://www.wine.com.br/vinhos/casillero-reserva-limited-edition-cabernet-sauvignon/prod23130.html'

df = pd.read_csv(DATA / 'wines.csv')

TAG = '''<div class="TechnicalDetails">\n<div class="container visible-xs">\n<div class="row somelier">\n<div class="col-xs-12">
         <h2 class="somelier__title">Comentário do Sommelier</h2>
         <div class="somelier__description">\nEdição especial para o Halloween, esse Cabernet Sauvignon além de apresentar um rótulo ousado e divertido, também traz a elegância de um belo exemplar Concha Y Toro.O Casillero Del Diablo é um tinto frutado, equilibrado e saboroso! Uma edição limitada!\n</div>\n</div>\n
         <div class="col-xs-12 content-space">\n</div>\n</div>\n</div>\n<div class="container">\n
         <div class="row">\n<div class="col-xs-12 col-md-8 col-md-offset-4 col-sm-7 col-sm-offset-5">\n
         <h2 class="TechnicalDetails-title">\nFicha Técnica\n </h2>\n</div>\n</div>\n<div class="TechnicalDetails-image">\n
         <script src="https://ajax.cloudflare.com/cdn-cgi/scripts/7089c43e/cloudflare-static/rocket-loader.min.js" data-cf-settings="30065b171190d5cba9ad9c02-|49"></script><img title="Casillero Reserva Limited Edition Cabernet Sauvignon" alt="Casillero Reserva Limited Edition Cabernet Sauvignon" src="https://www.wine.com.br/cdn-cgi/image/f=auto,h=900,q=100/assets-images/produtos/23130-03.png" onerror="this.parentElement.parentElement.classList.add(\'js-wine-kit\')">\n</div>\n
         <div class="row">\n<div class="col-xs-12 col-md-8 col-md-offset-4 col-sm-7 col-sm-offset-5">\n
         <div class="row">\n<div class="col-xs-12 col-sm-6">\n<div class="row">\n
         <div class="col-xs-8 col-sm-12 TechnicalDetails-description TechnicalDetails-description--grape">\n
         <div class="Left">\n<i class="Icon Icon--grapes"></i>\n</div>\n
         <div class="Right">\n<dt>Tinto</dt>\n<dd>Cabernet Sauvignon (100.00%)</dd>\n</div>\n</div>\n
         <div class="col-xs-8 col-sm-12 TechnicalDetails-description TechnicalDetails-description--location">\n
         <div class="Left">\n<i class="Icon Icon--location"></i>\n</div>\n
         <div class="Right">\n<dt>Chile</dt>\n<dd>Valle Central </dd>\n</div>\n</div>\n
         <div class="col-xs-8 col-sm-12 TechnicalDetails-description TechnicalDetails-description--winery">\n
         <div class="Left">\n<i class="Icon Icon--winery"></i>\n</div>\n
         <div class="Right">\n<dt>Vinícola</dt>\n<dd>Concha y Toro</dd>\n</div>\n</div>\n
         <div class="col-xs-8 col-sm-12 TechnicalDetails-description TechnicalDetails-description--alcoholic_strength">\n
         <div class="Left">\n<i class="Icon Icon--wine-and-cup"></i>\n</div>\n
         <div class="Right">\n<dt>Teor Alcoólico</dt>\n<dd>13.50% ABV</dd>\n</div>\n</div>\n
         <div class="col-xs-8 col-sm-12 TechnicalDetails-description TechnicalDetails-description--ageing">\n
         <div class="Left">\n<i class="Icon Icon--ageing"></i>\n</div>\n
         <div class="Right">\n<dt>Amadurecimento</dt>\n<dd>Em barricas de carvalho.</dd>\n</div>\n</div>\n
         <div class="col-xs-8 col-sm-12 TechnicalDetails-description TechnicalDetails-description--harvest">\n
         <div class="Left">\n<i class="Icon Icon--harvest"></i>\n</div>\n
         <div class="Right">\n<dt>Safra</dt>\n<dd>2017</dd>\n</div>\n</div>\n
         <div class="col-xs-8 col-sm-12 TechnicalDetails-description TechnicalDetails-description--classification">\n
         <div class="Left">\n<i class="Icon Icon--classification"></i>\n</div>\n
         <div class="Right">\n<dt>Classificação</dt>\n<dd>Seco</dd>\n</div>\n</div>\n</div>\n</div>\n
         <div class="col-xs-12  col-sm-6">\n<div class="row">\n<div class="col-xs-8 col-sm-12 TechnicalDetails-description TechnicalDetails-description--appearance">\n
         <div class="Left">\n<i class="Icon Icon--appearance"></i>\n</div>\n
         <div class="Right">\n<dt>Visual</dt>\n <dd>Rubi intenso</dd>\n</div>\n</div>\n
         <div class="col-xs-8 col-sm-12 TechnicalDetails-description TechnicalDetails-description--aroma">\n
         <div class="Left">\n<i class="Icon Icon--aroma"></i>\n</div>\n
         <div class="Right">\n<dhttps://www.wine.com.br/vinhos/casillero-reserva-limited-edition-cabernet-sauvignon/prod23130.htmlt>Olfativo</dt>\n<dd>Cassis, cereja, ameixa e notas de tostado</dd>\n</div>\n</div>\n
         <div class="col-xs-8 col-sm-12 TechnicalDetails-description TechnicalDetails-description--taste">\n
         <div class="Left">\n<i class="Icon Icon--taste"></i>\n</div>\n
         <div class="Right">\n<dt>Gustativo</dt>\n<dd>Corpo médio, taninos sedosos e final longo e frutado.</dd>\n</div>\n</div>\n
         <div class="col-xs-8 col-sm-12 TechnicalDetails-description TechnicalDetails-description--temperature">\n
         <div class="Left">\n<i class="Icon Icon--temperature"></i>\n</div>\n
         <div class="Right">\n<dt>Temperatura de serviço</dt>\n<dd>15 °C</dd>\n</div>\n</div>\n
         <div class="col-xs-8 col-sm-12 TechnicalDetails-description TechnicalDetails-description--temperature">\n
         <div class="Left">\n<i class="Icon Icon--ageing_potential"></i>\n</div>\n
         <div class="Right">\n<dt>Potencial de guarda</dt>\n<dd>4 anos</dd>\n</div>\n</div>\n</div>\n</div>\n</div>\n</div>\n</div>\n
         <div class="row">\n<div class="col-xs-12 col-md-8 col-md-offset-4 col-sm-7 col-sm-offset-5">\n
         <article class="TechnicalDetails-matching">\n<dt>Harmonização</dt>\n<dd>Carnes vermelhas, pratos condimentados e queijos envelhecidos como Gruyère e azuis.</dd>\n</article>\n</div>\n</div>\n</div>\n</div>
      '''

# +
TIPOS = {'Branco', 'Espumante', 'Frisante', 'Licoroso', 'Rosé', 'Tinto'}
PAISES = {'África do Sul', 'Alemanha', 'Argentina', 'Austrália', 'Brasil', 'Chile'
          'China', 'Espanha', 'Estados Unidos', 'França', 'Hungria', 'Itália', 'Líbano'
          'Nova Zelândia', 'Portugal', 'Uruguai', 'Grécia', 'Marrocos'}

KEYS = {'Vinícola', 'Teor_Alcoólico', 'Amadurecimento', 'Safra','Classificação', 'Visual', 
        'Olfativo', 'Gustativo', 'Temperatura', 'Potencial_Guarda', 'Decantação''Harmonização'}

# -

#export
class FichaTecnica(scrapy.Spider):
    
    name = "ficha_tecnica"
    
    start_urls = df['link'].to_list()
    

    def parse(self, response):
        page = response.xpath('/html').get()
        yield self.ficha_tecnica(page)

    # Second parsing method
    def ficha_tecnica(self, tag):
        tag = soup(tag, 'lxml')
        result = {}
        key = []
        val = []
        
        v = tag.find(class_="PageHeader-title")
        key.append("title")
        val.append(v.string if v else '')
        
        v = tag.find(class_="somelier__description")
        key.append('somelier')
        val.append(v.string.strip() if v else '')
        
        precos = tag.find_all(class_='Price-raw')        
        
        if len(precos) >= 2:
            precos = sorted(list(set([float(p.string) for p in precos])))
            key.append('Preço_Sócio')
            val.append(precos[0])
            key.append('Preço_Normal')
            val.append(precos[1])
            
        
        keys = [t.string for t in tag.find_all('dt')]
        vals = [t.string for t in tag.find_all('dd')]
        
               
        for k,v in zip(keys, vals):
            if k in TIPOS:
                key.append('Tipo')
                val.append(k)
            elif k in PAISES:
                key.append('Origem')
                val.append(f'{k}-{v}')
            else:
                key.append(k)
                val.append(v)
                
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

        
        return dict(zip(key, val))
        #try:
        #    ficha.remove("Ficha Técnica")
        #except:
        #    pass
        #field, description =  tee(ficha, 2)
        #field, description = list(field)[::2], list(description)[1::2]
        #return {f:d for f,d in zip(field, description)}

if __name__ == "__main__":
    
    process = CrawlerProcess()
    process.crawl(FichaTecnica)
    process.start()

tag = """<div class="ClubPrice-value">
<span>Sócio:</span>
<span>
<span class="Price is-loading" v-price="v-price">
<span class="Price-raw">126.90</span>
<span class="Price-formatted"></span>
</span>
</span>"""


tag = soup(tag, 'lxml')

tag.find('span', class_='Price-raw')


