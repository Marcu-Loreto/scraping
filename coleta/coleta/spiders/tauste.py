#!/usr/bin/env python3
"""
Spider para coletar produtos do site Tauste
"""

import scrapy
import re
from urllib.parse import urljoin, urlparse
from ..items import TausteItem


class TausteSpider(scrapy.Spider):
    name = 'tauste'
    allowed_domains = ['tauste.com.br']
    
    # URL inicial da padaria
    start_urls = ['https://tauste.com.br/sorocaba3/padaria.html']
    
    # Controle de paginação
    current_page = 0
    max_pages = None  # None = sem limite
    
    def __init__(self, max_pages=None, *args, **kwargs):
        super(TausteSpider, self).__init__(*args, **kwargs)
        if max_pages:
            self.max_pages = int(max_pages)
    
    def start_requests(self):
        """Inicia as requisições com headers apropriados"""
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                },
                callback=self.parse
            )
    
    def parse(self, response):
        """Parse da página principal"""
        self.current_page += 1
        self.logger.info(f"🔍 Processando página {self.current_page}: {response.url}")
        
        # Extrair produtos da página atual
        products = self.extract_products(response)
        self.logger.info(f"📦 Encontrados {len(products)} produtos na página {self.current_page}")
        
        # Yield dos produtos
        for product in products:
            yield product
        
        # Verificar se há próxima página
        next_page = self.get_next_page(response)
        if next_page and (self.max_pages is None or self.current_page < self.max_pages):
            self.logger.info(f"➡️ Próxima página encontrada: {next_page}")
            yield scrapy.Request(
                next_page,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                },
                callback=self.parse
            )
        else:
            if self.max_pages and self.current_page >= self.max_pages:
                self.logger.info(f"🏁 Limite de {self.max_pages} páginas atingido")
            else:
                self.logger.info("🏁 Fim das páginas")
    
    def extract_products(self, response):
        """Extrai produtos da página"""
        products = []
        
        # Baseado no conteúdo real do site, vou usar uma abordagem diferente
        # O site parece ter produtos listados com números e preços
        
        # 1. Procurar por elementos que contenham preços (R$)
        price_elements = response.css('*:contains("R$")')
        self.logger.info(f"📋 Encontrados {len(price_elements)} elementos com preços")
        
        if not price_elements:
            self.logger.warning("⚠️ Nenhum preço encontrado na página")
            return products
        
        # 2. Procurar por títulos em negrito (strong, b)
        bold_elements = response.css('strong, b')
        self.logger.info(f"📋 Encontrados {len(bold_elements)} elementos em negrito")
        
        # 3. Tentar extrair produtos por padrão
        # Baseado no conteúdo que vi, os produtos têm: número, título, preço
        product_data = self.extract_products_by_pattern(response)
        
        if product_data:
            self.logger.info(f"✅ Extraídos {len(product_data)} produtos por padrão")
            products.extend(product_data)
        
        return products
    
    def extract_products_by_pattern(self, response):
        """Extrai produtos baseado no padrão do site Tauste"""
        products = []
        
        try:
            # Pegar todo o texto da página
            page_text = response.text
            
            # Procurar por padrões de produtos
            # Padrão: número. título **marca** preço R$ XX,XX
            import re
            
            # Padrão para encontrar produtos
            # Exemplo: "1. 107484 Vinho Cartuxa Ea Tinto Seco Portugal Garrafa 750ml **Cartuxa** R$ 69,90"
            product_pattern = r'(\d+)\.\s*(\d+)\s*(.*?)\s*\*\*(.*?)\*\*\s*R\$\s*([\d,]+)'
            
            matches = re.findall(product_pattern, page_text, re.DOTALL)
            
            for match in matches:
                try:
                    product_num = match[0]
                    product_id = match[1]
                    title = match[2].strip()
                    brand = match[3].strip()
                    price = f"R$ {match[4]}"
                    
                    # Criar item
                    item = TausteItem()
                    item['title'] = title
                    item['price'] = price
                    item['brand'] = brand
                    item['description'] = f"Produto {product_id}"
                    item['page_number'] = self.current_page
                    item['source_url'] = response.url
                    item['category'] = 'Padaria'
                    
                    products.append(item)
                    
                except Exception as e:
                    self.logger.error(f"❌ Erro ao processar produto: {e}")
                    continue
            
            # Se não encontrou com o padrão principal, tentar padrão mais simples
            if not products:
                # Padrão mais simples: título **marca** R$ preço
                simple_pattern = r'(.*?)\s*\*\*(.*?)\*\*\s*R\$\s*([\d,]+)'
                matches = re.findall(simple_pattern, page_text, re.DOTALL)
                
                for match in matches:
                    try:
                        title = match[0].strip()
                        brand = match[1].strip()
                        price = f"R$ {match[2]}"
                        
                        # Filtrar títulos muito curtos ou vazios
                        if len(title) > 5:
                            item = TausteItem()
                            item['title'] = title
                            item['price'] = price
                            item['brand'] = brand
                            item['page_number'] = self.current_page
                            item['source_url'] = response.url
                            item['category'] = 'Padaria'
                            
                            products.append(item)
                    
                    except Exception as e:
                        self.logger.error(f"❌ Erro ao processar produto simples: {e}")
                        continue
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao extrair produtos por padrão: {e}")
        
        return products
    
    def extract_product_data(self, element, response):
        """Extrai dados de um produto individual"""
        try:
            # Extrair título - baseado na estrutura do Tauste
            title_selectors = [
                '.product-name::text',
                '.product-item-name::text', 
                'h2::text',
                'h3::text',
                'strong::text',
                'b::text',
                '.name::text',
                '.title::text',
                'a::text',
            ]
            
            title = None
            for selector in title_selectors:
                title = element.css(selector).get()
                if title and title.strip():
                    title = title.strip()
                    break
            
            # Extrair preço - baseado na estrutura do Tauste
            price_selectors = [
                '.price::text',
                '.product-price::text',
                '.price-box .price::text',
                '[class*="price"]::text',
                'span:contains("R$")::text',
                '.value::text',
            ]
            
            price = None
            for selector in price_selectors:
                price = element.css(selector).get()
                if price and 'R$' in price:
                    price = price.strip()
                    break
            
            # Extrair descrição
            description_selectors = [
                '.description::text',
                '.product-description::text',
                '.short-description::text',
                '.details::text',
            ]
            
            description = None
            for selector in description_selectors:
                description = element.css(selector).get()
                if description and description.strip():
                    description = description.strip()
                    break
            
            # Extrair imagem
            image_selectors = [
                '.product-image img::attr(src)',
                '.product-image-photo::attr(src)',
                'img::attr(src)',
                '.image::attr(src)',
            ]
            
            image_url = None
            for selector in image_selectors:
                image_url = element.css(selector).get()
                if image_url:
                    image_url = urljoin(response.url, image_url)
                    break
            
            # Extrair link do produto
            link_selectors = [
                '.product-item-link::attr(href)',
                '.product-name a::attr(href)',
                'a::attr(href)',
            ]
            
            product_link = None
            for selector in link_selectors:
                product_link = element.css(selector).get()
                if product_link:
                    product_link = urljoin(response.url, product_link)
                    break
            
            # Extrair marca (pode estar no título ou em elemento separado)
            brand_selectors = [
                '.brand::text',
                '.manufacturer::text',
                '.product-brand::text',
            ]
            
            brand = None
            for selector in brand_selectors:
                brand = element.css(selector).get()
                if brand and brand.strip():
                    brand = brand.strip()
                    break
            
            # Se não encontrou marca específica, tentar extrair do título
            if not brand and title:
                # Procurar por marcas conhecidas no título
                known_brands = ['Tauste', 'Cartuxa', 'Don Luciano', 'Ceremony', 'Santa Carolina', 
                               'Villa Fabrizia', 'Norton', 'Pata Negra', 'Mosketto', 'Perini', 
                               'Quinta De Bons-Ventos', 'Zolla', 'Concha Y Toro', 'Casillero Del Diablo', 'Trivento']
                for known_brand in known_brands:
                    if known_brand.lower() in title.lower():
                        brand = known_brand
                        break
            
            # Criar item
            item = TausteItem()
            item['title'] = title
            item['price'] = price
            item['description'] = description
            item['image_url'] = image_url
            item['product_link'] = product_link
            item['brand'] = brand
            item['page_number'] = self.current_page
            item['source_url'] = response.url
            item['category'] = 'Padaria'  # Categoria fixa para este spider
            
            return item
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao extrair dados do produto: {e}")
            return None
    
    def get_next_page(self, response):
        """Extrai o link da próxima página"""
        # Padrão de URL do Tauste: ?p=2, ?p=3, etc.
        current_url = response.url
        
        # Verificar se já tem parâmetro de página
        if '?p=' in current_url:
            # Extrair número da página atual
            match = re.search(r'\?p=(\d+)', current_url)
            if match:
                current_page_num = int(match.group(1))
                next_page_num = current_page_num + 1
                next_url = re.sub(r'\?p=\d+', f'?p={next_page_num}', current_url)
                return next_url
        else:
            # Primeira página, adicionar ?p=2
            if '?' in current_url:
                next_url = f"{current_url}&p=2"
            else:
                next_url = f"{current_url}?p=2"
            return next_url
        
        return None 