#!/usr/bin/env python3
"""
Script de debug detalhado para analisar a estrutura HTML do Tauste
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'coleta'))

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from coleta.spiders.tauste import TausteSpider

class DetailedDebugTausteSpider(TausteSpider):
    """Spider para debug detalhado do Tauste"""
    
    def parse(self, response):
        """Parse da página principal com debug detalhado"""
        self.current_page += 1
        print(f"🔍 DEBUG DETALHADO - Página {self.current_page}: {response.url}")
        print(f"📄 Status: {response.status}")
        print(f"📏 Tamanho: {len(response.body)} bytes")
        
        # Salvar HTML para análise
        with open(f'debug_tauste_detailed_{self.current_page}.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"💾 HTML salvo em: debug_tauste_detailed_{self.current_page}.html")
        
        # Analisar estrutura HTML detalhadamente
        print("\n🔍 Análise detalhada da estrutura HTML...")
        
        # 1. Procurar por elementos li
        li_elements = response.css('li')
        print(f"📋 Total de elementos <li>: {len(li_elements)}")
        
        # 2. Procurar por elementos com classes específicas
        class_patterns = ['item', 'product', 'product-item']
        for pattern in class_patterns:
            elements = response.css(f'[class*="{pattern}"]')
            print(f"📋 Elementos com classe contendo '{pattern}': {len(elements)}")
            
            if elements:
                # Analisar o primeiro elemento
                first_elem = elements[0]
                print(f"   Primeiro elemento com '{pattern}':")
                print(f"   - Tag: {first_elem.root.tag}")
                print(f"   - Classes: {first_elem.attrib.get('class', 'N/A')}")
                print(f"   - ID: {first_elem.attrib.get('id', 'N/A')}")
                print(f"   - HTML: {first_elem.get()[:200]}...")
        
        # 3. Procurar por produtos específicos
        print("\n🔍 Procurando por produtos específicos...")
        
        # Procurar por números de produtos (1., 2., 3., etc.)
        numbered_items = response.css('li:contains(".")')
        print(f"📋 Elementos li com números: {len(numbered_items)}")
        
        # Procurar por preços (R$)
        price_elements = response.css('*:contains("R$")')
        print(f"📋 Elementos com preços (R$): {len(price_elements)}")
        
        # Procurar por títulos em negrito
        bold_elements = response.css('strong, b')
        print(f"📋 Elementos em negrito: {len(bold_elements)}")
        
        if bold_elements:
            print("   Primeiros 5 títulos em negrito:")
            for i, elem in enumerate(bold_elements[:5]):
                text = elem.get().strip()
                if text:
                    print(f"   {i+1}. {text[:100]}...")
        
        # 4. Procurar por links de produtos
        product_links = response.css('a[href*="product"], a[href*="item"]')
        print(f"📋 Links de produtos: {len(product_links)}")
        
        # 5. Procurar por imagens
        images = response.css('img')
        print(f"📋 Imagens: {len(images)}")
        
        if images:
            print("   Primeiras 3 imagens:")
            for i, img in enumerate(images[:3]):
                src = img.attrib.get('src', 'N/A')
                alt = img.attrib.get('alt', 'N/A')
                print(f"   {i+1}. src: {src}, alt: {alt}")
        
        # 6. Procurar por padrões específicos do Tauste
        print("\n🔍 Procurando por padrões específicos do Tauste...")
        
        # Procurar por "Incluir na lista de compras"
        add_to_list = response.css('*:contains("Incluir na lista de compras")')
        print(f"📋 Elementos 'Incluir na lista de compras': {len(add_to_list)}")
        
        # Procurar por "Adicionar para Comparar"
        compare = response.css('*:contains("Adicionar para Comparar")')
        print(f"📋 Elementos 'Adicionar para Comparar': {len(compare)}")
        
        # 7. Procurar por seções específicas
        print("\n🔍 Procurando por seções específicas...")
        
        sections = response.css('h1, h2, h3, h4, h5, h6')
        print(f"📋 Títulos de seção: {len(sections)}")
        
        if sections:
            print("   Primeiros 5 títulos:")
            for i, section in enumerate(sections[:5]):
                text = section.get().strip()
                if text:
                    print(f"   {i+1}. {text[:100]}...")
        
        # 8. Procurar por dados JSON
        print("\n🔍 Procurando por dados JSON...")
        scripts = response.css('script')
        json_scripts = []
        
        for script in scripts:
            content = script.get()
            if content and ('product' in content.lower() or 'item' in content.lower() or 'json' in content.lower()):
                json_scripts.append(content)
        
        print(f"📋 Scripts com dados JSON: {len(json_scripts)}")
        
        if json_scripts:
            print("   Primeiro script com dados:")
            print(f"   {json_scripts[0][:300]}...")
        
        # 9. Testar seletores específicos
        print("\n🔍 Testando seletores específicos...")
        
        test_selectors = [
            'li.item.product.product-item',
            'li[class*="item product product-item"]',
            'li.item',
            '.product-item',
            '.item',
            '[class*="product"]',
            '[class*="item"]',
        ]
        
        for selector in test_selectors:
            elements = response.css(selector)
            print(f"   Seletor '{selector}': {len(elements)} elementos")
            
            if elements:
                first_elem = elements[0]
                print(f"     - Primeiro elemento: {first_elem.root.tag}, classes: {first_elem.attrib.get('class', 'N/A')}")
                print(f"     - HTML: {first_elem.get()[:150]}...")
        
        print("\n🏁 Fim da análise detalhada")

def main():
    """Função principal"""
    settings = get_project_settings()
    settings.set('LOG_LEVEL', 'ERROR')  # Reduzir logs
    settings.set('ROBOTSTXT_OBEY', False)
    
    process = CrawlerProcess(settings)
    process.crawl(DetailedDebugTausteSpider, max_pages=1)
    process.start()

if __name__ == "__main__":
    main() 