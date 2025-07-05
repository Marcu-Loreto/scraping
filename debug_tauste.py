#!/usr/bin/env python3
"""
Script para debugar e analisar a estrutura HTML do site Tauste
"""

import requests
from bs4 import BeautifulSoup
import json

def analyze_tauste_structure():
    """Analisa a estrutura HTML do site Tauste"""
    
    url = "https://tauste.com.br/sorocaba3/padaria.html"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    print(f"🔍 Analisando: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print(f"✅ Status: {response.status_code}")
        print(f"📄 Tamanho: {len(response.content)} bytes")
        
        # Salvar HTML para análise
        with open('debug_tauste.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("💾 HTML salvo em: debug_tauste.html")
        
        # Procurar por produtos
        print("\n🔍 Procurando por produtos...")
        
        # Possíveis seletores para produtos
        product_selectors = [
            '.product-item',
            '.item',
            '[data-product]',
            '.product',
            '.card',
            '.product-card',
            '.item-product',
            'li',  # Lista de produtos
            'div[class*="product"]',
            'div[class*="item"]',
        ]
        
        for selector in product_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"✅ Seletor '{selector}': {len(elements)} elementos encontrados")
                
                # Analisar o primeiro elemento
                if elements:
                    first_element = elements[0]
                    print(f"📋 Primeiro elemento com '{selector}':")
                    print(f"   Tag: {first_element.name}")
                    print(f"   Classes: {first_element.get('class', [])}")
                    print(f"   ID: {first_element.get('id', 'N/A')}")
                    
                    # Procurar por título
                    title_selectors = ['h1', 'h2', 'h3', 'h4', '.title', '.product-name', '.name']
                    for title_sel in title_selectors:
                        title_elem = first_element.select_one(title_sel)
                        if title_elem:
                            print(f"   Título ({title_sel}): {title_elem.get_text(strip=True)[:100]}")
                            break
                    
                    # Procurar por preço
                    price_selectors = ['.price', '.product-price', '[class*="price"]', '.value']
                    for price_sel in price_selectors:
                        price_elem = first_element.select_one(price_sel)
                        if price_elem:
                            print(f"   Preço ({price_sel}): {price_elem.get_text(strip=True)[:50]}")
                            break
                    
                    # Procurar por imagem
                    img_elem = first_element.select_one('img')
                    if img_elem:
                        print(f"   Imagem: {img_elem.get('src', 'N/A')}")
                        print(f"   Alt: {img_elem.get('alt', 'N/A')}")
                    
                    # Procurar por link
                    link_elem = first_element.select_one('a')
                    if link_elem:
                        print(f"   Link: {link_elem.get('href', 'N/A')}")
                    
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
        ]
        
        for selector in pagination_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"✅ Paginação '{selector}': {len(elements)} elementos encontrados")
                for elem in elements:
                    print(f"   HTML: {elem}")
                    links = elem.select('a')
                    print(f"   Links encontrados: {len(links)}")
                    for link in links:
                        print(f"     - {link.get('href', 'N/A')} | {link.get_text(strip=True)}")
                break
        
        # Procurar por padrões de URL
        print("\n🔍 Procurando por padrões de URL...")
        all_links = soup.find_all('a', href=True)
        tauste_links = [link for link in all_links if 'tauste.com.br' in link.get('href', '')]
        
        print(f"Total de links Tauste: {len(tauste_links)}")
        for link in tauste_links[:10]:  # Primeiros 10
            href = link.get('href')
            text = link.get_text(strip=True)
            print(f"   {href} | {text}")
        
        # Verificar se há dados JSON
        print("\n🔍 Procurando por dados JSON...")
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and ('product' in script.string.lower() or 'item' in script.string.lower()):
                print("✅ Script com dados de produtos encontrado")
                print(f"   Conteúdo: {script.string[:200]}...")
                break
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    analyze_tauste_structure() 