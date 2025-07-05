import scrapy
from coleta.items import ColetaItem
import re
# dicas do processo https://www.notion.so/Projeto-Scrapping-219a06795c3680ef9696d4dd76f0bbda?showMoveTo=true&saveParent=true

class MercadolivreSpider(scrapy.Spider):
    name = "mercadolivre"
    allowed_domains = ["lista.mercadolivre.com.br"]
    start_urls = ["https://lista.mercadolivre.com.br/tenis-corrida-masculino"]
    
    # Configurações de paginação
    custom_settings = {
        'DOWNLOAD_DELAY': 1,  # Delay entre requests para evitar bloqueio
        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,  # Randomização do delay
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,  # Limitar requests simultâneos
    }
    
    def __init__(self, max_pages=None, *args, **kwargs):
        super(MercadolivreSpider, self).__init__(*args, **kwargs)
        self.max_pages = int(max_pages) if max_pages else None
        self.current_page = 0

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })

    def parse(self, response):
        self.current_page += 1
        self.logger.info(f"Processando página {self.current_page}")
        
        cards = response.css('div.poly-card')  # elemento-pai que contém imagem + conteúdo
        for card in cards:
            item = ColetaItem()
            
            # Dados básicos
            item['brand'] = card.css('span.poly-component__brand::text').get()
            item['price'] = card.css('span.andes-money-amount').xpath('string(.)').get()
            item['title'] = card.css('a.poly-component__title *::text').get()
            item['alt_text'] = card.css('img.poly-component__picture::attr(alt)').get()
            item['link'] = card.css('a.poly-component__link::attr(href)').get()
            
            # Processar imagem
            image_url = card.css('img.poly-component__picture::attr(src)').get()
            
            # Tentar obter imagem real se for base64
            if image_url and self.is_base64_placeholder(image_url):
                # Tentar obter imagem real do link do produto
                product_link = item['link']
                if product_link:
                    yield scrapy.Request(
                        product_link,
                        callback=self.parse_product_image,
                        meta={'item': item},
                        headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                        }
                    )
                else:
                    item['image_url'] = image_url
                    yield item
            else:
                item['image_url'] = image_url
                yield item
        
        # Processar paginação - buscar próxima página
        next_page = self.get_next_page(response)
        
        # Verificar se atingiu o limite de páginas
        if self.max_pages and self.current_page >= self.max_pages:
            self.logger.info(f"Limite de {self.max_pages} páginas atingido. Parando.")
            return
        
        if next_page:
            self.logger.info(f"Indo para próxima página: {next_page}")
            yield response.follow(
                next_page, 
                callback=self.parse,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            )
        else:
            self.logger.info("Chegou ao fim das páginas")
   
    def parse_product_image(self, response):
        """Extrai imagem real da página do produto"""
        item = response.meta['item']
        
        # Tentar diferentes seletores para imagens
        image_selectors = [
            'img.ui-pdp-image::attr(src)',
            'img.ui-pdp-image::attr(data-src)',
            '.ui-pdp-gallery__figure img::attr(src)',
            '.ui-pdp-gallery__figure img::attr(data-src)',
            '.ui-pdp-gallery__main img::attr(src)',
            '.ui-pdp-gallery__main img::attr(data-src)',
            'img[data-testid="gallery-image"]::attr(src)',
            'img[data-testid="gallery-image"]::attr(data-src)',
        ]
        
        for selector in image_selectors:
            image_url = response.css(selector).get()
            if image_url and not self.is_base64_placeholder(image_url):
                # Limpar URL (remover parâmetros de redimensionamento)
                clean_url = self.clean_image_url(image_url)
                item['image_url'] = clean_url
                break
        else:
            # Se não encontrou imagem real, usar a original
            item['image_url'] = None
        
        yield item
    
    def is_base64_placeholder(self, url):
        """Verifica se é um placeholder base64 (1x1 pixel transparente)"""
        if not url:
            return True
        
        # Verificar se é base64
        if url.startswith('data:image/'):
            # Verificar se é o placeholder específico do MercadoLivre
            placeholder_patterns = [
                'R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7',
                'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'
            ]
            return any(pattern in url for pattern in placeholder_patterns)
        
        return False
    
    def clean_image_url(self, url):
        """Remove parâmetros de redimensionamento da URL da imagem"""
        if not url:
            return url
        
        # Remover parâmetros comuns de redimensionamento
        url = re.sub(r'[?&]w=\d+', '', url)
        url = re.sub(r'[?&]h=\d+', '', url)
        url = re.sub(r'[?&]size=\d+', '', url)
        url = re.sub(r'[?&]quality=\d+', '', url)
        
        # Remover parâmetros específicos do MercadoLivre
        url = re.sub(r'[?&]D_Q_NP_\d+', '', url)
        
        # Limpar URLs que terminam com parâmetros vazios
        url = re.sub(r'[?&]+$', '', url)
        
        return url
    
    def get_next_page(self, response):
        """Extrai o link da próxima página usando múltiplos métodos"""
        import json
        import re
        
        # Método 1: Extrair dos dados JSON no HTML
        try:
            # Procurar por padrões JSON que contenham next_page
            json_patterns = [
                r'"next_page":\s*\{[^}]*"url":\s*"([^"]+)"',
                r'"next_page":\s*\{[^}]*"value":\s*"Seguinte"[^}]*"url":\s*"([^"]+)"',
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, response.text)
                if matches:
                    next_url = matches[0].replace('\\u002F', '/')
                    self.logger.info(f"Próxima página encontrada (JSON): {next_url}")
                    return next_url
        except Exception as e:
            self.logger.debug(f"Erro ao extrair JSON: {e}")
        
        # Método 2: Extrair URLs com padrão "Desde_X"
        try:
            # Procurar por URLs que contenham "Desde_" (padrão do MercadoLivre)
            desde_pattern = r'https://[^"]*_Desde_\d+_NoIndex_True'
            matches = re.findall(desde_pattern, response.text)
            if matches:
                # Pegar a primeira URL que não seja a atual
                current_url = response.url
                for url in matches:
                    if url != current_url and '_Desde_' in url:
                        self.logger.info(f"Próxima página encontrada (Desde): {url}")
                        return url
        except Exception as e:
            self.logger.debug(f"Erro ao extrair Desde: {e}")
        
        # Método 3: Seletores XPath tradicionais (fallback)
        next_page_selectors = [
            # Priorizar a classe específica que você confirmou
            '//a[contains(@class,"andes-pagination__link") and contains(@aria-label,"Seguinte")]/@href',
            '//a[contains(@class,"andes-pagination__link") and contains(@aria-label,"Próxima")]/@href',
            '//a[contains(@class,"andes-pagination__link") and contains(@aria-label,"Next")]/@href',
            '//a[contains(@class,"andes-pagination__link") and contains(text(),"Seguinte")]/@href',
            '//a[contains(@class,"andes-pagination__link") and contains(text(),"Próxima")]/@href',
            '//a[contains(@class,"andes-pagination__link") and contains(text(),"Next")]/@href',
            # Fallbacks gerais
            '//a[contains(text(),"Seguinte")]/@href',
            '//a[contains(text(),"Próxima")]/@href',
            '//a[contains(text(),"Next")]/@href',
            '//a[contains(@class,"andes-pagination__button--next")]/@href',
            '//li[contains(@class,"andes-pagination__button--next")]/a/@href',
            '//a[@data-testid="pagination-next"]/@href',
            '//a[contains(@aria-label,"Próxima")]/@href',
            '//a[contains(@aria-label,"Next")]/@href',
            '//a[contains(@aria-label,"Seguinte")]/@href',
        ]
        
        for selector in next_page_selectors:
            next_page = response.xpath(selector).get()
            if next_page and next_page.strip():
                self.logger.info(f"Próxima página encontrada (XPath): {next_page}")
                return next_page
        
        # Método 4: Seletores CSS (fallback)
        css_selectors = [
            # Priorizar a classe específica que você confirmou
            'a.andes-pagination__link[aria-label*="Seguinte"]::attr(href)',
            'a.andes-pagination__link[aria-label*="Próxima"]::attr(href)',
            'a.andes-pagination__link[aria-label*="Next"]::attr(href)',
            'a.andes-pagination__link:contains("Seguinte")::attr(href)',
            'a.andes-pagination__link:contains("Próxima")::attr(href)',
            'a.andes-pagination__link:contains("Next")::attr(href)',
            # Fallbacks gerais
            'a.andes-pagination__button--next::attr(href)',
            'li.andes-pagination__button--next a::attr(href)',
            'a[data-testid="pagination-next"]::attr(href)',
            '.andes-pagination__button a[aria-label*="Próxima"]::attr(href)',
            '.andes-pagination__button a[aria-label*="Next"]::attr(href)',
            '.andes-pagination__button a[aria-label*="Seguinte"]::attr(href)',
        ]
        
        for selector in css_selectors:
            next_page = response.css(selector).get()
            if next_page and next_page.strip():
                self.logger.info(f"Próxima página encontrada (CSS): {next_page}")
                return next_page
        
        self.logger.info("Nenhuma próxima página encontrada - fim da paginação")
        return None
#comando para rodar o spider: scrapy crawl mercadolivre -o data.csv para salvar em csv
#comando para rodar o spider: scrapy crawl mercadolivre -o data.json para salvar em json
#comando para rodar o spider: scrapy crawl mercadolivre -o data.xml para salvar em xml
#comando para rodar o spider: scrapy crawl mercadolivre -o data.jl para salvar em jsonlines
#comando para rodar o spider: scrapy crawl mercadolivre -o data.jl.gz para salvar em jsonlines gzip
#comando para rodar o spider: scrapy crawl mercadolivre -o data.jl.bz2 para salvar em jsonlines bzip2
#comando para rodar o spider: scrapy crawl mercadolivre -o data.jl.zip para salvar em jsonlines zip
#comando para rodar o spider: scrapy crawl mercadolivre -o data.jl.tar para salvar em jsonlines tar
#comando para rodar o spider: scrapy crawl mercadolivre -o data.jl.tar.gz para salvar em jsonlines tar gzip	    

