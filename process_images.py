#!/usr/bin/env python3
"""
Script para processar imagens base64 existentes no arquivo CSV
e tentar obter imagens reais dos produtos
"""

import csv
import os
import re
import requests
import hashlib
from urllib.parse import urlparse
from bs4 import BeautifulSoup

class ImageProcessor:
    def __init__(self):
        self.images_dir = 'images'
        self.base64_pattern = re.compile(r'^data:image/[^;]+;base64,')
        
        # Criar diretório de imagens se não existir
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)
    
    def is_base64_placeholder(self, url):
        """Verifica se é um placeholder base64"""
        if not url:
            return True
        
        if url.startswith('data:image/'):
            placeholder_patterns = [
                'R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7',
                'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'
            ]
            return any(pattern in url for pattern in placeholder_patterns)
        
        return False
    
    def download_image(self, url, title):
        """Baixa a imagem da URL e salva localmente"""
        try:
            filename = self.create_filename(url, title)
            filepath = os.path.join(self.images_dir, filename)
            
            if os.path.exists(filepath):
                return filepath
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            return filepath
            
        except Exception as e:
            print(f"Erro ao baixar imagem {url}: {str(e)}")
            return None
    
    def create_filename(self, url, title):
        """Cria um nome de arquivo único para a imagem"""
        parsed_url = urlparse(url)
        path = parsed_url.path
        extension = os.path.splitext(path)[1]
        
        if not extension:
            if 'webp' in url.lower():
                extension = '.webp'
            elif 'jpg' in url.lower() or 'jpeg' in url.lower():
                extension = '.jpg'
            elif 'png' in url.lower():
                extension = '.png'
            else:
                extension = '.jpg'
        
        safe_title = re.sub(r'[^\w\s-]', '', title).strip()
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        safe_title = safe_title[:50]
        
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        
        return f"{safe_title}_{url_hash}{extension}"
    
    def get_real_image_from_product_page(self, product_url, title):
        """Tenta obter imagem real da página do produto"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(product_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Tentar diferentes seletores para imagens
            image_selectors = [
                'img.ui-pdp-image',
                '.ui-pdp-gallery__figure img',
                '.ui-pdp-gallery__main img',
                'img[data-testid="gallery-image"]',
                '.ui-pdp-gallery__figure img[src*="http"]',
            ]
            
            for selector in image_selectors:
                img = soup.select_one(selector)
                if img:
                    src = img.get('src') or img.get('data-src')
                    if src and not self.is_base64_placeholder(src):
                        # Limpar URL
                        clean_url = self.clean_image_url(src)
                        return clean_url
            
            return None
            
        except Exception as e:
            print(f"Erro ao obter imagem da página {product_url}: {str(e)}")
            return None
    
    def clean_image_url(self, url):
        """Remove parâmetros de redimensionamento da URL"""
        if not url:
            return url
        
        url = re.sub(r'[?&]w=\d+', '', url)
        url = re.sub(r'[?&]h=\d+', '', url)
        url = re.sub(r'[?&]size=\d+', '', url)
        url = re.sub(r'[?&]quality=\d+', '', url)
        url = re.sub(r'[?&]D_Q_NP_\d+', '', url)
        url = re.sub(r'[?&]+$', '', url)
        
        return url
    
    def process_csv(self, input_file, output_file):
        """Processa o arquivo CSV e tenta obter imagens reais"""
        processor = ImageProcessor()
        
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames + ['image_path', 'is_base64', 'real_image_url']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                image_url = row.get('image', '')
                title = row.get('title', 'Sem título')
                link = row.get('link', '')
                
                # Verificar se é base64
                if processor.is_base64_placeholder(image_url):
                    row['is_base64'] = 'True'
                    row['image_path'] = ''
                    
                    # Tentar obter imagem real da página do produto
                    if link:
                        print(f"Tentando obter imagem real para: {title}")
                        real_image_url = processor.get_real_image_from_product_page(link, title)
                        if real_image_url:
                            row['real_image_url'] = real_image_url
                            # Baixar a imagem
                            image_path = processor.download_image(real_image_url, title)
                            if image_path:
                                row['image_path'] = image_path
                                print(f"Imagem baixada: {image_path}")
                            else:
                                row['image_path'] = ''
                        else:
                            row['real_image_url'] = ''
                            row['image_path'] = ''
                    else:
                        row['real_image_url'] = ''
                        row['image_path'] = ''
                else:
                    row['is_base64'] = 'False'
                    row['real_image_url'] = image_url
                    # Baixar a imagem existente
                    image_path = processor.download_image(image_url, title)
                    row['image_path'] = image_path if image_path else ''
                
                writer.writerow(row)

def main():
    processor = ImageProcessor()
    
    # Processar o arquivo CSV existente
    input_file = 'coleta/data.csv'
    output_file = 'coleta/data_processed.csv'
    
    if os.path.exists(input_file):
        print("Processando arquivo CSV...")
        processor.process_csv(input_file, output_file)
        print(f"Arquivo processado salvo como: {output_file}")
    else:
        print(f"Arquivo {input_file} não encontrado!")

if __name__ == "__main__":
    main() 