1 - Criando o ambiente
Criando uma pasta para colocar o projeto 
  ***mkdir scraping*** 

Entrar no diretorio novo
cd scraping
Criar o ambiente viirtual;
python -m venv .venv
Ativar o ambiente virtua;

.\.venv\Scripts\activate

Criar um projeto no Git Hub "scraping"

criar um arquivo README.md

echo "# scraping" >> [README.md](http://readme.md/)

inicializar o repositorio do git

git init
Outros comando para o Git hub ( adicionar os arquivos criado dentro do github)
git add .
Fazer o commit no GitHub

git commit -m “first commit”

Criar a Branch Main
git branch -M main

Direcionar os arquivos ao GitHub ( Criar o repositorios)
`git remote add origin https://github.com/Marcu-Loreto/scraping.git`

Resumo dos comandos para GitHub

```
echo "# scraping" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/Marcu-Loreto/scraping.git
git push -u origin main
```

Criando  o projeto

ETL - Extration Transform Load

Extração usando a biblioteca **SCRAPY (**https://www.scrapy.org/**)
pip install scrapy**

Scrapy cria a inicialização de todos projeto como um Framework ( Ele cria uam pagina com todos os itens)

**scrapy startproject coleta**

Comando no scrapy para criar a rota para iniocar o scraping ( a url do site) por exemplo:  https://lista.mercadolivre.com.br/tenis-corrida-masculino

scrapy genspider mercadolivre https://lista.mercadolivre.com.br/tenis-corrida-masculino

resultado: Created spider 'mercadolivre' using template 'basic' in module:
coleta.spiders.mercadolivre

Ele cria um arquivo dentro da pasta coleta o arquivo mecrcado livre .py (  ./coleta/spider/mercadolivre.py )

***Obs.: Camando para ver a lista de bibliotecas instaladas “pip list” ou “pip list | findstr scrapy ( para buscar uma biblioteca esp[peciufica.***

A sequencia de busca é : Request // Parse ( um de para ) e o Nextpage

Para acompanhar o resultado dos camandos, pode-se usar o comando **scrapy shell  -** com ele vai ser capaz de acompanar o log de acesso

Scrapy shell
 
