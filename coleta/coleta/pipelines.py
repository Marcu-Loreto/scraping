# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import os
import re
import hashlib
import requests
from urllib.parse import urlparse
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class ColetaPipeline:
    def process_item(self, item, spider):
        return item


class ImageProcessingPipeline:
    """Pipeline para processar imagens e detectar base64"""
    
    def __init__(self):
        self.images_dir = 'images'
        
        # Criar diretório de imagens se não existir
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        image_url = adapter.get('image_url')
        
        if not image_url:
            return item
        
        # Verificar se é base64
        if self.is_base64_image(image_url):
            adapter['is_base64'] = True
            adapter['image_path'] = None
            # Log para debug
            spider.logger.info(f"Imagem base64 detectada para: {adapter.get('title', 'Sem título')}")
        else:
            adapter['is_base64'] = False
            # Tentar baixar a imagem
            image_path = self.download_image(image_url, adapter.get('title', 'sem_titulo'))
            adapter['image_path'] = image_path
            if image_path:
                spider.logger.info(f"Imagem baixada: {image_path}")
            else:
                spider.logger.warning(f"Falha ao baixar imagem: {image_url}")
        
        return item
    
    def is_base64_image(self, url):
        """Verifica se a URL é uma imagem base64"""
        if not url:
            return False
        return url.startswith('data:image/')
    
    def download_image(self, url, title):
        """Baixa a imagem da URL e salva localmente"""
        try:
            # Criar nome de arquivo único
            filename = self.create_filename(url, title)
            filepath = os.path.join(self.images_dir, filename)
            
            # Verificar se já existe
            if os.path.exists(filepath):
                return filepath
            
            # Baixar a imagem
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Salvar a imagem
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            return filepath
            
        except Exception as e:
            print(f"Erro ao baixar imagem {url}: {str(e)}")
            return None
    
    def create_filename(self, url, title):
        """Cria um nome de arquivo único para a imagem"""
        # Extrair extensão da URL
        parsed_url = urlparse(url)
        path = parsed_url.path
        extension = os.path.splitext(path)[1]
        
        if not extension:
            # Tentar detectar extensão pelo content-type
            if 'webp' in url.lower():
                extension = '.webp'
            elif 'jpg' in url.lower() or 'jpeg' in url.lower():
                extension = '.jpg'
            elif 'png' in url.lower():
                extension = '.png'
            else:
                extension = '.jpg'  # Padrão
        
        # Criar nome baseado no título e hash da URL
        safe_title = re.sub(r'[^\w\s-]', '', title).strip()
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        safe_title = safe_title[:50]  # Limitar tamanho
        
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        
        return f"{safe_title}_{url_hash}{extension}"


class FilterBase64Pipeline:
    """Pipeline para filtrar itens com imagens base64 (opcional)"""
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Se quiser filtrar apenas itens com imagens reais, descomente:
        # if adapter.get('is_base64', False):
        #     raise DropItem(f"Item com imagem base64 removido: {adapter.get('title')}")
        
        return item
