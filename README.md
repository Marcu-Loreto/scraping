# Scraping MercadoLivre com Processamento de Imagens

Este projeto implementa um sistema de scraping do MercadoLivre com processamento inteligente de imagens, incluindo detecção e tratamento de imagens base64 (placeholders) e download automático de imagens reais.

## Características

- ✅ **Detecção automática de imagens base64**: Identifica placeholders transparentes
- ✅ **Download de imagens reais**: Baixa imagens webp e outros formatos localmente
- ✅ **Processamento inteligente**: Tenta obter imagens reais das páginas de produtos
- ✅ **Pipeline configurável**: Sistema modular para processamento de dados
- ✅ **Script utilitário**: Processa dados existentes retroativamente

## Estrutura do Projeto

```
scraping/
├── coleta/
│   ├── coleta/
│   │   ├── items.py              # Modelo de dados personalizado
│   │   ├── pipelines.py          # Pipelines de processamento
│   │   ├── settings.py           # Configurações do Scrapy
│   │   └── spiders/
│   │       └── mercadolivre.py   # Spider principal
│   ├── data.csv                  # Dados coletados
│   └── scrapy.cfg               # Configuração do Scrapy
├── images/                      # Diretório para imagens baixadas
├── process_images.py            # Script para processar dados existentes
├── requirements.txt             # Dependências do projeto
└── README.md                   # Este arquivo
```

## Instalação

1. **Instalar dependências**:
```bash
pip install -r requirements.txt
```

2. **Verificar estrutura**:
```bash
cd coleta
scrapy list
```

## 🚀 Como Usar

### 1. Executar o Spider

O spider agora usa o item personalizado, pipelines configurados e **paginação completa**:

```bash
cd coleta
# Executar todas as páginas
py -m scrapy crawl mercadolivre -o data_all_pages.csv

# Executar apenas 5 páginas (para teste)
py -m scrapy crawl mercadolivre -a max_pages=5 -o data_5_pages.csv

# Executar com delay maior (recomendado)
py -m scrapy crawl mercadolivre -s DOWNLOAD_DELAY=2 -o data_safe.csv
```

**Novos campos no output**:
- `image_url`: URL original da imagem
- `image_path`: Caminho local onde a imagem foi salva
- `is_base64`: Flag indicando se é imagem base64
- `link`: Link do produto

**Funcionalidades de paginação**:
- ✅ **Paginação automática**: Percorre todas as páginas automaticamente
- ✅ **Múltiplos seletores**: Usa diversos seletores para encontrar "próxima página"
- ✅ **Limite configurável**: Pode limitar o número de páginas com `-a max_pages=N`
- ✅ **Logs informativos**: Mostra progresso da paginação
- ✅ **Rate limiting**: Delay entre requests para evitar bloqueio

### 2. Testar Paginação

Para testar se a paginação está funcionando corretamente:

```bash
# Testar com 3 páginas (recomendado para teste)
py test_pagination.py

# Ou testar diretamente com o spider
cd coleta
py -m scrapy crawl mercadolivre -a max_pages=3 -L INFO
```

O teste irá:
- ✅ Verificar se consegue encontrar a próxima página
- ✅ Contar produtos em cada página
- ✅ Mostrar URLs das páginas processadas
- ✅ Confirmar que a paginação funciona

### 3. Processar Dados Existentes

Para processar o arquivo CSV existente e tentar obter imagens reais:

```bash
python process_images.py
```

Este script irá:
- Ler o arquivo `coleta/data.csv`
- Identificar imagens base64
- Tentar obter imagens reais das páginas de produtos
- Baixar as imagens para o diretório `images/`
- Gerar um novo arquivo `coleta/data_processed.csv`

### 4. Configurações Avançadas

#### Filtrar Apenas Itens com Imagens Reais

No arquivo `coleta/coleta/pipelines.py`, descomente a linha no `FilterBase64Pipeline`:

```python
if adapter.get('is_base64', False):
    raise DropItem(f"Item com imagem base64 removido: {adapter.get('title')}")
```

#### Ajustar Diretório de Imagens

No `ImageProcessingPipeline`, modifique:

```python
self.images_dir = 'images'  # Mude para o diretório desejado
```

## Como Funciona

### Detecção de Base64

O sistema identifica imagens base64 usando padrões específicos:
- `data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7`
- Este é um placeholder transparente de 1x1 pixel usado pelo MercadoLivre

### Obtenção de Imagens Reais

1. **Na listagem**: Se detecta base64, faz request para a página do produto
2. **Na página do produto**: Usa múltiplos seletores CSS para encontrar imagens reais
3. **Limpeza de URL**: Remove parâmetros de redimensionamento
4. **Download**: Baixa e salva localmente com nome único

### Seletores de Imagem Utilizados

```css
img.ui-pdp-image
.ui-pdp-gallery__figure img
.ui-pdp-gallery__main img
img[data-testid="gallery-image"]
```

## Exemplos de Output

### Antes (com base64)
```csv
brand,price,title,image,alt_text
FILA,"R$244,90","Tênis Masculino Progress Lite Fila","data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7","Tênis Masculino Progress Lite Fila"
```

### Depois (com imagem real)
```csv
brand,price,title,image_url,image_path,is_base64,real_image_url
FILA,"R$244,90","Tênis Masculino Progress Lite Fila","data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7","images/Tenis-Masculino-Progress-Lite-Fila_a1b2c3d4.webp","True","https://http2.mlstatic.com/D_Q_NP_2X_973796-MLA83481691989_042025-E.webp"
```

## Troubleshooting

### Erro de Conexão
- Verifique sua conexão com a internet
- O MercadoLivre pode ter rate limiting

### Imagens Não Baixadas
- Verifique se o diretório `images/` existe
- Confirme permissões de escrita
- Verifique logs do spider

### Performance
- O processamento pode ser lento devido aos requests adicionais
- Considere usar `DOWNLOAD_DELAY` no settings.py

## Comandos Úteis

```bash
# Executar spider com todas as páginas
py -m scrapy crawl mercadolivre -o data_all.csv

# Executar apenas 5 páginas (para teste)
py -m scrapy crawl mercadolivre -a max_pages=5 -o data_test.csv

# Executar com logs detalhados
py -m scrapy crawl mercadolivre -L DEBUG

# Executar com delay maior (recomendado para produção)
py -m scrapy crawl mercadolivre -s DOWNLOAD_DELAY=3 -o data_safe.csv

# Testar paginação apenas
py test_pagination.py

# Verificar pipelines ativos
py -m scrapy crawl mercadolivre -s LOG_LEVEL=INFO
```

## Contribuição

Para melhorar o projeto:

1. Adicione novos seletores de imagem no spider
2. Implemente cache de imagens
3. Adicione suporte a outros formatos de imagem
4. Melhore o tratamento de erros

## Licença

Este projeto é para fins educacionais. Respeite os termos de uso do MercadoLivre.
