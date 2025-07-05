#!/usr/bin/env python3
"""
Script para testar o site Tauste usando Selenium para renderizar JavaScript
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def test_tauste_with_selenium():
    """Testa o site Tauste com Selenium"""
    
    print("🚀 Iniciando teste com Selenium...")
    
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executar sem interface gráfica
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("✅ Driver Chrome iniciado")
        
        # Acessar a página
        url = "https://tauste.com.br/sorocaba3/padaria.html"
        print(f"🔍 Acessando: {url}")
        
        driver.get(url)
        
        # Aguardar carregamento
        print("⏳ Aguardando carregamento da página...")
        time.sleep(5)
        
        # Aguardar elementos específicos
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            print("✅ Página carregada")
        except Exception as e:
            print(f"⚠️ Timeout aguardando elementos: {e}")
        
        # Salvar HTML renderizado
        html_content = driver.page_source
        with open('tauste_selenium_rendered.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("💾 HTML renderizado salvo em: tauste_selenium_rendered.html")
        
        # Analisar com BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        print("\n🔍 Analisando HTML renderizado...")
        
        # 1. Procurar por elementos li
        li_elements = soup.find_all('li')
        print(f"📋 Total de elementos <li>: {len(li_elements)}")
        
        # 2. Procurar por produtos
        product_selectors = [
            'li.item.product.product-item',
            'li[class*="item"]',
            'li[class*="product"]',
            '.product-item',
            '.item',
        ]
        
        for selector in product_selectors:
            elements = soup.select(selector)
            print(f"📋 Seletor '{selector}': {len(elements)} elementos")
            
            if elements:
                first_elem = elements[0]
                print(f"   Primeiro elemento:")
                print(f"   - Tag: {first_elem.name}")
                print(f"   - Classes: {first_elem.get('class', [])}")
                print(f"   - HTML: {str(first_elem)[:200]}...")
        
        # 3. Procurar por preços
        price_elements = soup.find_all(text=lambda text: text and 'R$' in text)
        print(f"📋 Elementos com preços (R$): {len(price_elements)}")
        
        if price_elements:
            print("   Primeiros 5 preços:")
            for i, price in enumerate(price_elements[:5]):
                print(f"   {i+1}. {price.strip()}")
        
        # 4. Procurar por títulos em negrito
        bold_elements = soup.find_all(['strong', 'b'])
        print(f"📋 Elementos em negrito: {len(bold_elements)}")
        
        if bold_elements:
            print("   Primeiros 5 títulos em negrito:")
            for i, elem in enumerate(bold_elements[:5]):
                text = elem.get_text(strip=True)
                if text:
                    print(f"   {i+1}. {text[:100]}...")
        
        # 5. Procurar por imagens
        images = soup.find_all('img')
        print(f"📋 Imagens: {len(images)}")
        
        if images:
            print("   Primeiras 3 imagens:")
            for i, img in enumerate(images[:3]):
                src = img.get('src', 'N/A')
                alt = img.get('alt', 'N/A')
                print(f"   {i+1}. src: {src}, alt: {alt}")
        
        # 6. Procurar por links
        links = soup.find_all('a', href=True)
        print(f"📋 Links: {len(links)}")
        
        # 7. Procurar por padrões específicos
        add_to_list = soup.find_all(text=lambda text: text and 'Incluir na lista de compras' in text)
        print(f"📋 'Incluir na lista de compras': {len(add_to_list)}")
        
        compare = soup.find_all(text=lambda text: text and 'Adicionar para Comparar' in text)
        print(f"📋 'Adicionar para Comparar': {len(compare)}")
        
        # 8. Procurar por números de produtos (1., 2., 3., etc.)
        numbered_items = soup.find_all(text=lambda text: text and text.strip().endswith('.') and text.strip()[:-1].isdigit())
        print(f"📋 Números de produtos: {len(numbered_items)}")
        
        if numbered_items:
            print("   Primeiros 5 números:")
            for i, num in enumerate(numbered_items[:5]):
                print(f"   {i+1}. {num.strip()}")
        
        # 9. Tentar encontrar produtos por estrutura
        print("\n🔍 Procurando por produtos por estrutura...")
        
        # Procurar por elementos que contenham preços e títulos
        all_elements = soup.find_all()
        product_candidates = []
        
        for elem in all_elements:
            text = elem.get_text()
            if text and 'R$' in text and len(text) > 10:
                product_candidates.append(elem)
        
        print(f"📋 Candidatos a produtos: {len(product_candidates)}")
        
        if product_candidates:
            print("   Primeiros 3 candidatos:")
            for i, candidate in enumerate(product_candidates[:3]):
                text = candidate.get_text(strip=True)
                print(f"   {i+1}. {text[:150]}...")
                print(f"      Tag: {candidate.name}, Classes: {candidate.get('class', [])}")
        
        # 10. Testar página 2
        print("\n🔍 Testando página 2...")
        driver.get("https://tauste.com.br/sorocaba3/padaria.html?p=2")
        time.sleep(3)
        
        html_page2 = driver.page_source
        soup_page2 = BeautifulSoup(html_page2, 'html.parser')
        
        price_elements_page2 = soup_page2.find_all(text=lambda text: text and 'R$' in text)
        print(f"📋 Preços na página 2: {len(price_elements_page2)}")
        
        if price_elements_page2:
            print("   Primeiros 3 preços da página 2:")
            for i, price in enumerate(price_elements_page2[:3]):
                print(f"   {i+1}. {price.strip()}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    finally:
        try:
            driver.quit()
            print("✅ Driver fechado")
        except:
            pass

if __name__ == "__main__":
    test_tauste_with_selenium() 