import re
from bs4 import BeautifulSoup
import os
import sys
import pandas as pd

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_dir)

from .criterions import df_combined



def search_article(arquivos):
    total_artigos_encontrados = []

    for file_path in arquivos:
        arquivo_xml = open_xml_file(file_path)
        dicionario_artigo = extract_bs(arquivo_xml, file_path)

        total_artigos_encontrados.append(dicionario_artigo)

    print("Artigos encontrados: ", len(total_artigos_encontrados))
    

    print("\nFiltro pelo Combined DataFrame: \n")
    artigos_filtrados_combined_dataframe = []
    artigos_restantes = []
    for artigo in total_artigos_encontrados:
        if filter_articles_by_combined_dataframe(artigo, df_combined):
            artigos_filtrados_combined_dataframe.append(artigo)
        else:
            artigos_restantes.append(artigo)
    print("Artigos filtrados pelo Combined DataFrame: ", len(artigos_filtrados_combined_dataframe))

    nome = 'artigos.txt'
    with open(nome, 'w', encoding='utf-8') as arquivo:
        for artigo in artigos_filtrados_combined_dataframe:
            arquivo.write(str(artigo))
            arquivo.write('\n')
        arquivo.write('\n')

    print(f'Total: {len(artigos_filtrados_combined_dataframe)}')

    return artigos_filtrados_combined_dataframe


def open_xml_file(file_path):    
    with open(file_path, 'r', encoding="utf-8") as arquivo:

        conteudo_xml = arquivo.read()
        return conteudo_xml


def extract_bs(xml_file, file_path):
    bs_texto = BeautifulSoup(xml_file, 'xml')
    texto_tag = bs_texto.find('Texto')
    
    # processando o html para adicionar um espaço entre as tags
    texto_tag = re.sub(r'(</\w+>)', r' \1', texto_tag.string)

    # parser html para a tag encapsulada cdata
    cdata_content = BeautifulSoup(texto_tag, 'html.parser')

    # identificando tags dentro da tag encapsulada
    identifica_tag = cdata_content.find('p', {'class':'identifica'})
    subtitulo_tag = cdata_content.find('p', {'class': 'subtitulo'})
    ementa_tag = cdata_content.find('p', {'class':'ementa'})
    assinatura_tag = cdata_content.find('p', {'class':'assina'})
    cargo_tag = cdata_content.find('p', {'class':'cargo'})

    escopo = bs_texto.find('article').get('artCategory')
    secao = bs_texto.find('article').get('pubName')
    edicao = bs_texto.find('article').get('editionNumber')
    pdfPage = bs_texto.find('article').get('pdfPage')
    data = bs_texto.find('article').get('pubDate').replace("/","-")
    art_type = bs_texto.find('article').get('artType')
    idOficio = bs_texto.find('article').get('idOficio')
    art_class = bs_texto.find('article').get('artClass')

    data_pub = str(data)

    identifica = identifica_tag.get_text() if identifica_tag else None
    subtitulo = subtitulo_tag.get_text() if subtitulo_tag else None
    ementa = ementa_tag.get_text() if ementa_tag else None
    assinatura = assinatura_tag.get_text() if assinatura_tag else None
    cargo = cargo_tag.get_text() if cargo_tag else None

    # retirando as tags para sobrar apenas o texto
    if identifica_tag:
        identifica_tag.extract()
    if subtitulo_tag:
        subtitulo_tag.extract()
    if ementa_tag:
        ementa_tag.extract()
    if assinatura_tag:
        assinatura_tag.extract()
    if cargo_tag:
        cargo_tag.extract()

    texto = cdata_content.get_text()

    nome_arquivo = os.path.basename(file_path)

    dicionario_artigo = {
        'Título': str(identifica),        
        'SubTítulo': str(subtitulo),        
        'Escopo': escopo,
        'Ementa': str(ementa),
        'Texto': str(texto),
        'Assinatura': str(assinatura),
        'Cargo': str(cargo),
        'Seção': str(secao),
        'Edição': str(edicao),
        'DataPub': data_pub,
        'pdfPage': pdfPage,
        'artType': art_type,
        'idOficio': idOficio,
        'PubOrder': art_class,
        'LinkArquivo': nome_arquivo
    }

    return dicionario_artigo


def filter_articles_by_combined_dataframe(artigo, dataframe):
    termos_encontrados = []
    dataframe_copy = dataframe.copy()
    dataframe_copy.set_index('Termo', inplace=True)

    terms_keys = [
            ('SecondaryTerm','SecondaryKey','SecondaryTermRegex'),
            ('ExtraTerm1','ExtraKey1','ExtraTermRegex1'),
            ('ExtraTerm2','ExtraKey2','ExtraTermRegex2'),
            ('ExtraTerm3','ExtraKey3','ExtraTermRegex3'),
            ('ExtraTerm4','ExtraKey4','ExtraTermRegex4'),
            ('ExtraTerm5','ExtraKey5','ExtraTermRegex5'),
            ('ExtraTerm6','ExtraKey6','ExtraTermRegex6'),

        ]
    
    not_term_keys = [
        ('NotTerm1','NotKey1','NotTermoRegex'),
        ('NotTerm2','NotKey2','NotTermoRegex2'),
    ]

    for termo_principal in dataframe_copy.index:
        rows = dataframe_copy.loc[termo_principal]

        if isinstance(rows, pd.Series):
            rows = rows.to_frame().T

        for _, row in rows.iterrows():
            chave_principal = row['Key'] 
            termo_regex = row['TermoRegex']

            if not search_term_in_article(artigo, termo_principal, chave_principal, termo_regex):
                continue
            
            
            temp_termos_encontrados = [f"{chave_principal}: {termo_principal}"]
            excecao = False

            # Verificação de termos de exceção
            for not_term_col, not_key_col, not_regex_col in not_term_keys:
                not_term = row.get(not_term_col)
                not_key = row.get(not_key_col)
                not_regex = row.get(not_regex_col) if not_regex_col is not None else False

                if pd.notna(not_term) and pd.notna(not_key):
                    if search_term_in_article(artigo, not_term, not_key, not_regex):
                        print(f"Exceção encontrada -> {not_key}: {not_term} em {chave_principal}: {termo_principal}")
                        excecao = True
                        break
            
            if excecao:
                temp_termos_encontrados = []
                continue

            # Verificação aos demais termos
            matches = True
            for term_col, key_col, regex_col in terms_keys:
                term = row.get(term_col)
                key = row.get(key_col)
                regex = row.get(regex_col) if regex_col is not None else False

                if pd.notna(term) and pd.notna(key):
                    if search_term_in_article(artigo, term, key, regex):
                        temp_termos_encontrados.append(f'{key}: {term}')
                    else:
                        matches = False
                        break
            
            if matches:
                termos_encontrados.extend(temp_termos_encontrados)
                
    if termos_encontrados:
        artigo['Termos Encontrados'] = termos_encontrados
        print(f'Encontrado -> {termos_encontrados}')
        return True
    else:
        return False


def search_term_in_article(artigo, termo, parte=None, use_regex=False) -> bool:

    def match_content(conteudo, termo, use_regex=False):
        if use_regex:
            return re.search(termo, conteudo, re.IGNORECASE) is not None
        else:
            termo_escaped = re.escape(termo)  # Escapa o termo para evitar tratamento como regex
            return re.search(termo_escaped, conteudo, re.IGNORECASE) is not None

    if parte:
        if isinstance(parte, pd.Series):
            for item in parte:
                if item in artigo:
                    conteudo = artigo[item]
                    if conteudo and isinstance(conteudo, str) and match_content(conteudo, termo, use_regex):
                        return True
        elif parte in artigo:
            conteudo = artigo[parte]
            if conteudo and isinstance(conteudo, str) and match_content(conteudo, termo, use_regex):
                return True
    else:
        for conteudo in artigo.values():
            if conteudo and isinstance(conteudo, str) and match_content(conteudo, termo, use_regex):
                return True

    return False


