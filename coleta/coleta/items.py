# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ColetaItem(scrapy.Item):
    # define the fields for your item here like:
    brand = scrapy.Field()
    price = scrapy.Field()
    title = scrapy.Field()
    image_url = scrapy.Field()  # URL original da imagem
    image_path = scrapy.Field()  # Caminho local onde a imagem foi salva
    alt_text = scrapy.Field()
    is_base64 = scrapy.Field()  # Flag para indicar se é base64
    link = scrapy.Field()  # Link do produto


class TausteItem(scrapy.Item):
    # Campos para produtos do Tauste
    title = scrapy.Field()           # Título do produto
    price = scrapy.Field()           # Preço
    description = scrapy.Field()     # Descrição do produto
    image_url = scrapy.Field()       # URL da imagem
    image_path = scrapy.Field()      # Caminho local da imagem
    product_link = scrapy.Field()    # Link do produto
    page_number = scrapy.Field()     # Número da página
    source_url = scrapy.Field()      # URL da página fonte
    category = scrapy.Field()        # Categoria do produto
    brand = scrapy.Field()           # Marca do produto
    is_base64 = scrapy.Field()       # Flag para base64
