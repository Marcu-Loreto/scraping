import scrapy
# dicas do processo https://www.notion.so/Projeto-Scrapping-219a06795c3680ef9696d4dd76f0bbda?showMoveTo=true&saveParent=true

class MercadolivreSpider(scrapy.Spider):
    name = "mercadolivre"
    allowed_domains = ["lista.mercadolivre.com.br"]
    start_urls = ["https://lista.mercadolivre.com.br/tenis-corrida-masculino"]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })

    def parse(self, response):
     cards = response.css('div.poly-card')  # elemento-pai que contém imagem + conteúdo
     for card in cards:
        yield {
            'brand': card.css('span.poly-component__brand::text').get(),
            'price': card.css('span.andes-money-amount').xpath('string(.)').get(),
            'title': card.css('a.poly-component__title *::text').get(),
            'image': card.css('img.poly-component__picture::attr(src)').get(),
            'alt_text': card.css('img.poly-component__picture::attr(alt)').get(),
            # 'link': card.css('a.poly-component__link::attr(href)').get()  # caso queira o link do produto
        }
   
    #next_page = response.css('li.andes-pagination__button.a::attr(href)').get()
    # if next_page:
     # yield response.follow(next_page, callback=self.parse)
    
     next_page = response.xpath('//a[contains(text(),"Seguinte")]/@href').get()
     if next_page:
       yield response.follow(next_page, callback=self.parse)
#comando para rodar o spider: scrapy crawl mercadolivre -o data.csv para salvar em csv
#comando para rodar o spider: scrapy crawl mercadolivre -o data.json para salvar em json
#comando para rodar o spider: scrapy crawl mercadolivre -o data.xml para salvar em xml
#comando para rodar o spider: scrapy crawl mercadolivre -o data.jl para salvar em jsonlines
#comando para rodar o spider: scrapy crawl mercadolivre -o data.jl.gz para salvar em jsonlines gzip
#comando para rodar o spider: scrapy crawl mercadolivre -o data.jl.bz2 para salvar em jsonlines bzip2
#comando para rodar o spider: scrapy crawl mercadolivre -o data.jl.zip para salvar em jsonlines zip
#comando para rodar o spider: scrapy crawl mercadolivre -o data.jl.tar para salvar em jsonlines tar
#comando para rodar o spider: scrapy crawl mercadolivre -o data.jl.tar.gz para salvar em jsonlines tar gzip	    

