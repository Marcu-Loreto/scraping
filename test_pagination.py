#!/usr/bin/env python3
"""
Script para testar a paginação do spider
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'coleta'))

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from coleta.spiders.mercadolivre import MercadolivreSpider

class TestSpider(MercadolivreSpider):
    """Spider de teste que apenas verifica a paginação"""
    
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })

    def parse(self, response):
        self.current_page += 1
        print(f"✅ Página {self.current_page} processada: {response.url}")
        
        # Contar produtos na página
        cards = response.css('div.poly-card')
        print(f"   📦 Produtos encontrados: {len(cards)}")
        
        # Verificar se há próxima página
        next_page = self.get_next_page(response)
        if next_page:
            print(f"   ➡️  Próxima página: {next_page}")
            
            # Verificar limite de páginas
            if self.max_pages and self.current_page >= self.max_pages:
                print(f"   🛑 Limite de {self.max_pages} páginas atingido")
                return
            
            yield response.follow(
                next_page, 
                callback=self.parse,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            )
        else:
            print("   🏁 Fim das páginas")

def test_pagination(max_pages=3):
    """Testa a paginação com um número limitado de páginas"""
    print(f"🧪 Testando paginação (máximo {max_pages} páginas)...")
    print("=" * 60)
    
    # Configurações para teste
    settings = get_project_settings()
    settings.update({
        'DOWNLOAD_DELAY': 2,  # Delay maior para teste
        'RANDOMIZE_DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'LOG_LEVEL': 'ERROR',  # Reduzir logs
    })
    
    # Executar teste
    process = CrawlerProcess(settings)
    process.crawl(TestSpider, max_pages=max_pages)
    process.start()
    
    print("=" * 60)
    print("✅ Teste de paginação concluído!")

if __name__ == "__main__":
    # Testar com 3 páginas
    test_pagination(3) 