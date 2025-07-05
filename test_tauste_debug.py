#!/usr/bin/env python3
"""
Script de teste para debugar o spider Tauste
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'coleta'))

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from coleta.spiders.tauste import TausteSpider

class DebugTausteSpider(TausteSpider):
    """Spider para debugar o Tauste"""
    
    def parse(self, response):
        """Parse da página principal com debug detalhado"""
        self.current_page += 1
        print(f"🔍 DEBUG - Página {self.current_page}: {response.url}")
        print(f"📄 Status: {response.status}")
        print(f"📏 Tamanho: {len(response.body)} bytes")
        
        # Salvar HTML para análise
        with open(f'debug_tauste_page_{self.current_page}.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"💾 HTML salvo em: debug_tauste_page_{self.current_page}.html")
        
        # Analisar estrutura HTML
        print("\n🔍 Analisando estrutura HTML...")
        
        # Procurar por produtos
        product_selectors = [
            '.product-item',
            '.item',
            '[data-product]',
            '.product',
            '.card',
            '.product-card',
            '.item-product',
            'li',
            'div[class*="product"]',
            'div[class*="item"]',
            'div[class*="card"]',
            'div[class*="produto"]',
            'div[class*="item"]',
        ]
        
        for selector in product_selectors:
            elements = response.css(selector)
            if elements:
                print(f"✅ Seletor '{selector}': {len(elements)} elementos encontrados")
                
                # Analisar o primeiro elemento
                if elements:
                    first_element = elements[0]
                    print(f"📋 Primeiro elemento com '{selector}':")
                    print(f"   Tag: {first_element.root.tag}")
                    print(f"   Classes: {first_element.attrib.get('class', 'N/A')}")
                    print(f"   ID: {first_element.attrib.get('id', 'N/A')}")
                    
                    # Procurar por título
                    title_selectors = ['h1', 'h2', 'h3', 'h4', '.title', '.product-name', '.name', 'strong', 'b']
                    for title_sel in title_selectors:
                        title_elem = first_element.css(title_sel)
                        if title_elem:
                            title_text = title_elem.get()
                            print(f"   Título ({title_sel}): {title_text[:100] if title_text else 'N/A'}")
                            break
                    
                    # Procurar por preço
                    price_selectors = ['.price', '.product-price', '[class*="price"]', '.value', 'span']
                    for price_sel in price_selectors:
                        price_elem = first_element.css(price_sel)
                        if price_elem:
                            price_text = price_elem.get()
                            print(f"   Preço ({price_sel}): {price_text[:50] if price_text else 'N/A'}")
                            break
                    
                    # Procurar por imagem
                    img_elem = first_element.css('img')
                    if img_elem:
                        img_src = img_elem.attrib.get('src', 'N/A')
                        img_alt = img_elem.attrib.get('alt', 'N/A')
                        print(f"   Imagem: {img_src}")
                        print(f"   Alt: {img_alt}")
                    
                    # Procurar por link
                    link_elem = first_element.css('a')
                    if link_elem:
                        link_href = link_elem.attrib.get('href', 'N/A')
                        print(f"   Link: {link_href}")
                    
                    print()
                    break
        
        # Procurar por paginação
        print("🔍 Procurando por paginação...")
        pagination_selectors = [
            '.pagination',
            '.pager',
            '[class*="pagination"]',
            '[class*="pager"]',
            '.pages',
            'nav',
            'ul[class*="page"]',
            'a[href*="p="]',
        ]
        
        for selector in pagination_selectors:
            elements = response.css(selector)
            if elements:
                print(f"✅ Paginação '{selector}': {len(elements)} elementos encontrados")
                for elem in elements:
                    print(f"   HTML: {elem.get()}")
                    links = elem.css('a')
                    print(f"   Links encontrados: {len(links)}")
                    for link in links:
                        href = link.attrib.get('href', 'N/A')
                        text = link.get()
                        print(f"     - {href} | {text}")
                break
        
        # Procurar por padrões de URL
        print("\n🔍 Procurando por padrões de URL...")
        all_links = response.css('a[href]')
        tauste_links = [link for link in all_links if 'tauste.com.br' in link.attrib.get('href', '')]
        
        print(f"Total de links Tauste: {len(tauste_links)}")
        for link in tauste_links[:10]:  # Primeiros 10
            href = link.attrib.get('href', 'N/A')
            text = link.get()
            print(f"   {href} | {text[:50]}")
        
        # Verificar se há dados JSON
        print("\n🔍 Procurando por dados JSON...")
        scripts = response.css('script')
        for script in scripts:
            script_content = script.get()
            if script_content and ('product' in script_content.lower() or 'item' in script_content.lower()):
                print("✅ Script com dados de produtos encontrado")
                print(f"   Conteúdo: {script_content[:200]}...")
                break
        
        # Testar paginação
        next_page = self.get_next_page(response)
        if next_page:
            print(f"➡️ Próxima página: {next_page}")
        else:
            print("❌ Nenhuma próxima página encontrada")
        
        print("🏁 Fim da análise")

def main():
    """Função principal"""
    settings = get_project_settings()
    settings.set('LOG_LEVEL', 'INFO')
    settings.set('ROBOTSTXT_OBEY', False)
    
    process = CrawlerProcess(settings)
    process.crawl(DebugTausteSpider, max_pages=1)
    process.start()

if __name__ == "__main__":
    main() 