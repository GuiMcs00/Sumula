import os
import sys
import re
import json


project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_dir)



def montar_ementa(titulo, subtitulo, escopo, texto_conteudo, puNameSecao, artType, idOficio, artigos_encontrados):
    ementa = ""

    # Ementa de despachos:
    if re.search("Despacho", titulo, re.IGNORECASE):
        ementa = processar_despacho(titulo, escopo, texto_conteudo, puNameSecao, artType)

    #Ementa de artigos do tipo mensagem:
    elif re.search("Mensagem", artType, re.IGNORECASE) and re.search("Presidência da República", escopo, re.IGNORECASE):
        ementa = processar_mensagem(texto_conteudo)

    # Ementa de portarias:
    if re.search("Portaria", titulo, re.IGNORECASE):
        ementa = processar_portaria(titulo, escopo, texto_conteudo, puNameSecao)

    # Ementa de extrato de ata:
    if re.search("Extrato de Ata", titulo, re.IGNORECASE):
        ementa = processar_extrato_de_ata(titulo)

    #Ementa de Ata da Sessão CMN:
    if re.search("Ata(.*?Sessão CMN)", titulo, re.IGNORECASE):
        ementa = processar_ata_sessao_cmn(titulo)


    # Ementa de extrato da seção 3:
    if re.search("Extrato de Acordo", titulo, re.IGNORECASE) or re.search("Extrato de Convênio", titulo, re.IGNORECASE) \
        or re.search("Extrato de Cooperação Técnica", titulo, re.IGNORECASE):
        ementa = processar_extrato_secao_3(titulo, texto_conteudo)


    # Ementa de decreto:
    if re.search("DECRETO", titulo, re.IGNORECASE) and ementa == "" \
            and re.search('DO2', puNameSecao) \
            and re.search("Atos do Poder Executivo", escopo, re.IGNORECASE):
        ementa = processar_decreto(texto_conteudo)

    # Ementa da seção 3:
    if re.search("(Edital de consulta pública)|(Aviso de Consulta Pública)", titulo, re.IGNORECASE) and ('DO3', puNameSecao) and ementa == '':
        if subtitulo not in texto_conteudo and titulo not in texto_conteudo and texto_conteudo:
            ementa = texto_conteudo.split('\n', 1)[0].replace('"', '\\"')  # pega o primeiro parágrafo do texto 


    # Ementa de Resolução CICC:
    if re.search("Resolução CICC", titulo, re.IGNORECASE) and ementa == "":
        ementa = processar_resolucao_cicc(texto_conteudo)


    # Ementas de Retificações de Portarias:
    if re.search("Retificações", titulo, re.IGNORECASE) and re.search("Portaria n", texto_conteudo, re.IGNORECASE):
        ementa = processar_retificacoes_portarias(texto_conteudo)
        

    #Ementa de retificação:
    if ementa == "" and re.search("Retificação", titulo, re.IGNORECASE):
        ementa = processar_ementa_retificacao(titulo, subtitulo, texto_conteudo)

            
    # Ementas do Bccorreio (Portarias do Banco Central do Brasil da seção 2):
    if re.search("DO2", puNameSecao) and ementa == '' \
            and re.search("PORTARIA Nº", titulo, re.IGNORECASE) \
            and re.search("Banco Central do Brasil", escopo, re.IGNORECASE):
        ementa = processar_ementas_bccorreio(texto_conteudo)
        

    #Pega o primeiro parágrafo se não encontrar: --paragrafos

    if ementa == "" or ementa == ".":
        ementa = processar_ementa_padrao(titulo, subtitulo, texto_conteudo, idOficio, artigos_encontrados)


    return ementa


def processar_despacho(titulo, escopo, texto_conteudo, pub_name_secao, art_type):
    if re.search("Despacho", titulo, re.IGNORECASE) and re.search("Banco Central do Brasil", escopo, re.IGNORECASE) \
            and re.search("servidor", texto_conteudo, re.IGNORECASE):
        ementa = "Autoriza o afastamento do país." #para servidor ou diretor
        return ementa

    elif re.search("Despacho", titulo, re.IGNORECASE) and re.search("Banco Central do Brasil", escopo, re.IGNORECASE) \
        and not re.search("Conselho de Controle de Atividades Financeiras", escopo, re.IGNORECASE):
        inicio_texto = texto_conteudo.find('autoriza')
        fim_texto = texto_conteudo.find('País') + len('País')
        ementa = texto_conteudo[inicio_texto:fim_texto].replace("autoriza", "Autoriza") + "." #para presidente
        return ementa

    elif re.search("Despacho", titulo, re.IGNORECASE) \
            and re.search("Presidência da República", escopo, re.IGNORECASE) and re.search('DO2', pub_name_secao):
        inicio_texto = texto_conteudo.find('Exposição')
        paragrafo_interesse = texto_conteudo.find('Afastamento')
        fim_texto = texto_conteudo[paragrafo_interesse:].find(',') + paragrafo_interesse
        ementa = texto_conteudo[inicio_texto:fim_texto] + "." #exposição de motivos
        return ementa

    elif re.search("Despacho", titulo, re.IGNORECASE) \
            and re.search("Ministério da Fazenda", escopo, re.IGNORECASE) \
            and re.search("DO2", pub_name_secao):
        inicio_texto = texto_conteudo.find('autoriza')
        paragrafo_interesse = texto_conteudo.find('Presidente')
        fim_texto = texto_conteudo[paragrafo_interesse:].find(',') + paragrafo_interesse
        ementa = texto_conteudo[inicio_texto:fim_texto].replace('autoriza', 'Autoriza') + "."
        return ementa

    elif re.search("Despacho", titulo, re.IGNORECASE) and re.search("Conselho de Controle de Atividades Financeiras", escopo, re.IGNORECASE):
        inicio_texto = texto_conteudo.lower().find('presidente do conselho')
        fim_texto = texto_conteudo.find('Técnico')
        ementa = "O " + texto_conteudo[inicio_texto:fim_texto] + "Técnico" + "."
        return ementa

    # Ementas de despachos que não são mensagens da seção 1, obtém o assunto principal localizando o termo assunto caso encontre:
    elif re.search("Despacho", titulo, re.IGNORECASE) and re.search('DO1', pub_name_secao) and not re.search("Mensagem", art_type, re.IGNORECASE):
        assuntos = []

        match = re.search('(Assunto :)|(Assuntos:)|(Assunto:)|(Assuntos :)', texto_conteudo, re.IGNORECASE)

        if match:
            inicio = match.end()
            fim = texto_conteudo.find('.', inicio)
            if fim == -1:
                fim = len(texto_conteudo)
            
            ementa = texto_conteudo[inicio:fim].strip().replace('assunto: ', '').capitalize() + "."
            return ementa
    
    return ""


def processar_mensagem(texto_conteudo):
    match = re.search("Banco Central do Brasil", texto_conteudo, re.IGNORECASE)
    if match:
        ementa = texto_conteudo[match.start():].split('.')[0] + "."
        return ementa
    return ""
    

def processar_portaria(titulo, escopo, texto_conteudo, pub_name_secao):
    # Ementa de portarias:
    if re.search("Portaria", titulo, re.IGNORECASE) and re.search("DO1", pub_name_secao, re.IGNORECASE) \
            and not re.search("Banco Central do Brasil", escopo, re.IGNORECASE) and not re.search("AGU", titulo, re.IGNORECASE):
        
        match = re.search('Art\. 1º', texto_conteudo)
        if match:
            inicio = match.end()
            fim = texto_conteudo.find('.', inicio)
            if fim == -1:
                fim = len(texto_conteudo)

            ementa = str(
                texto_conteudo[inicio:fim].strip().replace('" ', '\\').replace('Homologar', 'Homologa').replace(
                    'Divulgar', 'Divulga').replace('Autorizar', 'Autoriza').replace('Nomear','Nomeia').replace(
                    'Exonerar', 'Exonera').replace('Designar', 'Designa').replace('Modificar', 'Modifica'))
            
            return ementa
            
    elif re.search("Portarias", titulo, re.IGNORECASE) and not re.search("Banco Central do Brasil", escopo, re.IGNORECASE):
        ementa = ""
        contador = 0
        n_portarias = []
        f = open('cargos.json')
        cargos_interesse = json.load(f)
        for cargo_interesse in cargos_interesse["Cargos"]:
            match = re.search("Nº", texto_conteudo)
            if match:
                n_portarias.append(texto_conteudo)
                contador += 1
            if re.search(cargo_interesse, texto_conteudo, re.IGNORECASE) \
                    and not re.search("no âmbito", texto_conteudo, re.IGNORECASE):
                toda_ementa = texto_conteudo
                toda_ementa = re.sub('[ ][A-Z]{3}[ ][0-9]{1}[\.][0-9]{2}', '', toda_ementa).replace(", código", '').replace(" código", "")
                inicio_ementa = n_portarias[contador - 1]
                toda_ementa = inicio_ementa.replace('NOMEAR', 'Nomeia').replace(
                    'HOMOLOGAR', 'Homologa').replace('EXONERAR', 'Exonera').replace('AUTORIZAR',
                                                                                    'Autoriza').replace(
                    'DIVULGAR', 'Divulga').replace('DISPENSAR', 'Dispensa').replace("Art. 1º ", "") + " " + toda_ementa
                ementa = ementa + "\n\n" + toda_ementa

                return ementa

    elif re.search("Portaria", titulo, re.IGNORECASE) \
            and re.search("Gabinete do Ministro", escopo, re.IGNORECASE):
        match = re.search('Art\. 1º', texto_conteudo)
        if match:
            ementa = texto_conteudo[match.end():].strip().replace('Art. 1º ', '')

            return ementa

    elif re.search("Portaria MF", titulo, re.IGNORECASE):
        match = re.search('resolve:', texto_conteudo)
        if match:
            indice = texto_conteudo.find('resolve:') + len('resolve:')
            texto_apos_resolve = texto_conteudo[indice:]
            ementa = texto_apos_resolve.replace('Nomear', 'Nomeia').replace(
                'Homologar', 'Homologa').replace('Exonerar', 'Exonera').replace('Autorizar',
                                                                                'Autoriza').replace(
                'Divulgar', 'Divulga').replace('Dispensar', 'Dispensa').replace("Art. 1º ", "").replace(
                'Designar', 'Designa')
            
            return ementa
    
    return ""


def processar_extrato_de_ata(titulo):
    inicio_texto = re.search('[0-9]{1}[\.][0-9]{3}', titulo)
    fim_texto = titulo.find(' REALIZADA')
    inicio = inicio_texto.span()[0]
    ementa = titulo[inicio:fim_texto] + "."

    return ementa


def processar_ata_sessao_cmn(titulo):
    inicio_texto = re.search('[0-9]{1}[\.][0-9]{3}', titulo)
    fim_texto = titulo.find('CMN') + len('CMN')
    inicio = inicio_texto.span()[0]
    ementa = titulo[inicio:fim_texto] + "."

    return ementa


def processar_extrato_secao_3(titulo, texto_conteudo):
    if re.search("Extrato de Acordo", titulo, re.IGNORECASE):
        texto_limpo = re.sub('( CNPJ(.*?[0-9]{2}[\.][0-9]{3}[\.][0-9]{3}[/][0-9]{4}[-][0-9]{2}))', '',
                            texto_conteudo)
        inicio_texto = texto_limpo.find('Acordo de Cooperação')
        fim_texto = texto_limpo[inicio_texto:].find('.') + inicio_texto
        ementa = texto_limpo[inicio_texto:fim_texto].replace(',', '') + "."

        return ementa

    elif re.search("Extrato de Convênio", titulo, re.IGNORECASE):
        inicio_texto = texto_conteudo.find('Termo')
        fim_texto = texto_conteudo[inicio_texto:].find('Objeto') + inicio_texto
        ementa = texto_conteudo[inicio_texto:fim_texto]
        
        return ementa

    elif re.search("Extrato de Cooperação Técnica", titulo, re.IGNORECASE):
        inicio_texto = texto_conteudo.find('Objeto:')
        fim_texto = texto_conteudo[inicio_texto:].find('.') + inicio_texto
        ementa = texto_conteudo[inicio_texto:fim_texto].replace('Objeto: ', '') + "."

        return ementa
    
    return ""


def processar_decreto(texto_conteudo):
    acoes = {
        "DESIGNAR": "Designa",
        "NOMEAR": "Nomeia",
        "Autorizar": "Autoriza",
        "EXONERAR": "Exonera",
        "HOMOLOGAR": "Homologa",
        "Tornar sem efeito": "Tornar sem efeito",
    }

    ementa = ""
    for chave, acao in acoes.items():
        match = re.search(fr'{chave}', texto_conteudo, re.IGNORECASE)
        if match:
            inicio = match.end()
            fim = texto_conteudo.find('\n', inicio)
            if fim == 1:
                fim = len(texto_conteudo)

            ementa += f"{acao} {texto_conteudo[inicio:fim].replace(':', '.')} \n\n"

    return ementa


def processar_resolucao_cicc(texto_conteudo):
    match = re.search("Art. 1º ", texto_conteudo, re.IGNORECASE)

    if match:
        inicio = match.end()
        fim = texto_conteudo.find('.', inicio)
        if fim == -1:
            fim = len(texto_conteudo)

        ementa = texto_conteudo[inicio:fim].strip().replace('"', '\\"') #pega o parágrafo que tem o Art. 1º

        return ementa
    return ""


def processar_retificacoes_portarias(texto_conteudo):
    #Procura pelos números das portarias:
    lista_numeros_portarias = []
    if not re.search("(Onde se lê)|(leia-se)", texto_conteudo, re.IGNORECASE) and re.search("Portaria nº", texto_conteudo, re.IGNORECASE):
        inicio_portaria = texto_conteudo.find("nº") + 3
        fim_portaria = texto_conteudo.find(",")
        lista_numeros_portarias.append(texto_conteudo[inicio_portaria:fim_portaria])

    portarias = str.join(", ", lista_numeros_portarias)
    portarias = portarias[::-1].replace(",", "e", 1) #susbtitui a última vírgula encontrada
    ementa = "Retificações das Portarias " + portarias[::-1].replace("e", " e") + "."

    return ementa


def processar_ementa_retificacao(titulo, subtitulo, texto_conteudo):
    if subtitulo not in texto_conteudo and titulo not in texto_conteudo and texto_conteudo:
        ementa = texto_conteudo.replace('"', '\\"')
        fim_ementa = ementa.find(", onde se lê:")
        ementa = ementa[:fim_ementa].replace("Na ", "").replace("No", "") + "."

        return ementa
    return ""


def processar_ementas_bccorreio(texto_conteudo):
    ementa = ""

    # Designação para substituir diretor ou presidente:
    ementa += processar_diretor_presidente(texto_conteudo)

    # Designação de menbros para o Coremec:
    ementa += processar_coremec(texto_conteudo)

    # Demissão de servidor:
    ementa += processar_demissao_servidor(texto_conteudo)

    # Remoção de ofício de servidor:
    ementa += processar_remocao_oficio_servidor(texto_conteudo)

    # Alteração de portaria:
    ementa += processar_alteracao_portaria(texto_conteudo)

    # Retificação e ajustes em portarias:
    ementa += processar_retificacao_portaria(texto_conteudo)

    #Disponibiliza requisição de servidor:
    ementa += processar_disponibilizacao_requisicao(texto_conteudo)

    # Disponibiliza cessão de servidor:
    ementa += processar_disponibilizacao_servidor(texto_conteudo)

    # Efetiva requisição: --paragrafos
    ementa += processar_efetiva_requisicao(texto_conteudo)

    # Remoção de ofício de diretor-servidor:
    ementa += processar_remocao_oficio_diretor(texto_conteudo)

    # Designa ou Dispensa titular de função comissionada:
    ementa += processa_funcao_comissionada(texto_conteudo)

    #Designação de cargos quaisquer: --paragrafos
    ementa += processar_designacao_cargos(texto_conteudo)

    #Autorização de cessão:
    ementa += processar_autorizacao_cessao(texto_conteudo)

    #Ementa para diretor que assume determinada área:
    ementa += processar_competencia_diretor(texto_conteudo)

    #Ementa para alteração na composição do Grupo de Trabalho de Avaliação Nacional de Riscos de Lavagem de Dinheiro, de Financiamento do Terrorismo e de Financiamento
    #da Proliferação de Armas de Destruição em Massa:
    ementa += processar_alteracao_grupo_trabalho(texto_conteudo)

    return ementa


def processar_diretor_presidente(texto_conteudo):
    ementa = ""
    
    if re.search("(Fica (designado)|(designada))|(Designar)", texto_conteudo, re.IGNORECASE) \
            and not re.search("Coremec", texto_conteudo, re.IGNORECASE) \
            and not re.search('para designar', texto_conteudo):
        if not re.search("(Fica (dispensado)|(dispesada))|(Dispensar)", texto_conteudo, re.IGNORECASE) \
                and not re.search('função comissionada', texto_conteudo):
            #Ementa sobre substituição de diretor:
            if not re.search("para substituir o Presidente", texto_conteudo, re.IGNORECASE):
                inicio_texto = texto_conteudo.find("resolve")
                qtd_art = texto_conteudo[inicio_texto:].count("Art.")
                if re.search("para substituir", texto_conteudo, re.IGNORECASE):
                    if qtd_art == 2:  # irá substituir só um
                        inicio = texto_conteudo.find("para substituir")
                        fim = inicio + texto_conteudo[inicio:].find(",")
                        ementa = texto_conteudo[inicio:fim].replace("para substituir","Designa substituto para") + "."
                        if re.search("Diretor de Relacionamento, Cidadania e Supervisão de Conduta", texto_conteudo):
                            #Como o texto é obtido até a vírgula, isto evita que o cargo Diretor de Relacionamento, Cidadania e Supervisão de Conduta venha incompleto:
                            ementa = ementa.replace("Diretor de Relacionamento", "Diretor de Relacionamento, Cidadania e Supervisão de Conduta")
                    else:
                        inicio = texto_conteudo.find("para substituir")
                        fim = inicio + texto_conteudo[inicio:].find(",")
                        ementa = texto_conteudo[inicio:fim].replace("para substituir", "Designa substitutos para") + "."
                        if re.search("Diretor de Relacionamento, Cidadania e Supervisão de Conduta", texto_conteudo):
                            #Como o texto é obtido até a vírgula, isto evita que o cargo Diretor de Relacionamento, Cidadania e Supervisão de Conduta venha incompleto:
                            ementa = ementa.replace("Diretor de Relacionamento", "Diretor de Relacionamento, Cidadania e Supervisão de Conduta")
            #Ementa sobre substituição de Presidente:
            else:
                inicio_texto = texto_conteudo.find("Fica designado")
                inicio_cargo = inicio_texto + texto_conteudo[inicio_texto:].find(",")
                fim_cargo = inicio_cargo + texto_conteudo[inicio_cargo + 1:].find(",")
                cargo_completo = texto_conteudo[inicio_cargo:fim_cargo].split(" ")
                try:
                    ementa = "Designa " + cargo_completo[1] + " para substituir o Presidente."
                except IndexError:
                    ementa = ""
        #Ementas sobre dispensa e designação de titulares de função comissionada:
        else:
            if re.search("(((servidor)|(procurador))(.*?função comissionada))", texto_conteudo, re.IGNORECASE):
                if not re.search("Dispensa", texto_conteudo, re.IGNORECASE):
                    ementa = "Designa titular da função comissionada."
                else:
                    ementa = "Dispensa e designa titulares da função comissionada."

    return ementa


def processar_coremec(texto_conteudo):
    ementa = ""
    if re.search("Coremec", texto_conteudo, re.IGNORECASE) \
            and re.search("(Ficam designados(.*?para representar))|(Fica designado(.*?para representar))",
                            texto_conteudo, re.IGNORECASE):
        ementa = "Designa membros para o Comitê de Regulação e Fiscalização dos Mercados Financeiro, de Capitais, de Seguros, de Previdência e Capitalização (Coremec)."

    return ementa


def processar_demissao_servidor(texto_conteudo):
    ementa = ""
    if re.search(
            "(É aplicada ao servidor(.*?pena de demissão))|(É aplicada à servidora(.*?pena de demissão))",
            texto_conteudo, re.IGNORECASE):
        ementa = "Demissão de servidor."
    return ementa


def processar_remocao_oficio_servidor(texto_conteudo):
    ementa =""
    if re.search("(Fica removido de ofício)|(Fica removida de ofício)", texto_conteudo, re.IGNORECASE) \
            and re.search("servidor", texto_conteudo, re.IGNORECASE):
        ementa = "Autoriza remoção de ofício de servidor."
    return ementa


def processar_alteracao_portaria(texto_conteudo):
    ementa = ""
    if re.search("(Fica alterado(.*?Portaria nº))", texto_conteudo, re.IGNORECASE):
        inicio_texto = texto_conteudo.find("Fica alterado")
        inicio = texto_conteudo[inicio_texto:].find('Portaria') + inicio_texto
        ano = re.search('[0-9]{4}', texto_conteudo[inicio:])
        fim_texto = ano.span()[0] + inicio + 4
        ementa = "Altera a " + texto_conteudo[inicio:fim_texto].replace(',', '') + "."
    return ementa


def processar_retificacao_portaria(texto_conteudo):
    ementa = ""
    if re.search('((Art. 1º)(.*?Portaria n((°)|(º)) )([0-9]{3}[\.][0-9]{3})(, de )(([0-9])|([0-9]{2}))( de )(.*?[0-9]{4}))', texto_conteudo):
        inicio_texto = texto_conteudo.find('Art. 1º')
        inicio = texto_conteudo[inicio_texto:].find('Portaria') + inicio_texto
        ano = re.search('[0-9]{4}', texto_conteudo[inicio:])
        fim = ano.span()[0] + inicio + 4
        if re.search('Retificar', texto_conteudo, re.IGNORECASE):
            ementa = "Retifica a " + texto_conteudo[inicio:fim].replace(',', '') + "."
        elif re.search('Tornar sem efeito', texto_conteudo, re.IGNORECASE):
            ementa = "Torna sem efeito " + texto_conteudo[inicio:fim].replace(',', '') + "."
        elif re.search("Alterar", texto_conteudo, re.IGNORECASE):
            ementa = "Altera a " + texto_conteudo[inicio:fim].replace(',', '') + "."
    return ementa


def processar_disponibilizacao_requisicao(texto_conteudo):
    ementa = ""
    if re.search("(Disponibiliza(.*?requisição))", texto_conteudo, re.IGNORECASE):
        ementa = "Disponibiliza requisição."
    return ementa


def processar_disponibilizacao_servidor(texto_conteudo):
    ementa = ""
    if re.search("(Ceder.*?servidor.*?ao término da cessão)", texto_conteudo, re.IGNORECASE):
        ementa = "Disponibiliza cessão de servidor VIGOR."
    return ementa


def processar_efetiva_requisicao(texto_conteudo):
    ementa = ""
    if re.search("Fica efetivada a seguinte requisição", texto_conteudo, re.IGNORECASE):
        if re.search('Cargo:', texto_conteudo, re.IGNORECASE):
            cargo_compl = texto_conteudo.replace('- Cargo: ', '')
        ementa = "Efetiva requisição de " + cargo_compl + "."
    return ementa


def processar_remocao_oficio_diretor(texto_conteudo):
    ementa = ""
    if re.search('(Remover(.*?diretor-servidor))', texto_conteudo, re.IGNORECASE):
        ementa = "Dispõe sobre remoção de diretor-servidor."
    return ementa


def processa_funcao_comissionada(texto_conteudo):
    ementa = ""
    if re.search('(servidor(.*?função comissionada))', texto_conteudo, re.IGNORECASE):
        if re.search('Designar', texto_conteudo, re.IGNORECASE):
            ementa = "Designa titular de função comissionada."
        elif re.search('Dispensar', texto_conteudo, re.IGNORECASE):
            ementa = "Dispensa titular de função comissionada."
    return ementa


def processar_autorizacao_cessao(texto_conteudo):
    ementa = ""
    if re.search("(Fica autorizada(.*?cessão))", texto_conteudo, re.IGNORECASE):
        ementa = "Autoriza a cessão."
    return ementa


def processar_designacao_cargos(texto_conteudo):
    ementa = ""
    if re.search("(Ficam designados)", texto_conteudo, re.IGNORECASE) and ementa == "":
        if re.search("Ficam designados", texto_conteudo, re.IGNORECASE):
            ementa = texto_conteudo.replace("Ficam designados", "Designa").replace(
                "Art. 1º ", "").replace(":", ".")
    return ementa


def processar_competencia_diretor(texto_conteudo):
    ementa = ""
    if re.search("(((Fica designado o Diretor )|(Fica designada a Diretora))(.*?para responder pela área))", texto_conteudo, re.IGNORECASE):
        if re.search("Diretor ", texto_conteudo, re.IGNORECASE):
            ementa = "Define competência de Diretor do Banco Central do Brasil."
        elif re.search("Diretora", texto_conteudo, re.IGNORECASE):
            ementa = "Define competência de Diretora do Banco Central do Brasil."
    return ementa


def processar_alteracao_grupo_trabalho(texto_conteudo):
    ementa = ""
    if re.search("(((Fica designado)|(Fica designada))(.*?Grupo de Trabalho de Avaliação Nacional de Riscos de Lavagem de Dinheiro, de Financiamento do Terrorismo e de Financiamento da Proliferação de Armas de Destruição em Massa))", 
                    texto_conteudo, re.IGNORECASE):
        
        #Se encontrar a portaria e o decreto no texto:
        if re.search("(Portaria (.*?[0-9]{3}[\.][0-9]{3}), de(.*?[0-9](.*?de [0-9]{4})))", texto_conteudo, re.IGNORECASE) \
            and re.search("(Decreto ((.*?[0-9]{2}[\.][0-9]{3})|(.*?[0-9]{1}[\.][0-9]{3})), de(.*?[0-9](.*?de [0-9]{4})))", texto_conteudo, re.IGNORECASE): 
            #Obtêm o intervalo que estão localizadas a portaria e o decreto no texto:
            localiza_portaria =  re.search("(Portaria (.*?[0-9]{3}[\.][0-9]{3}), de(.*?[0-9](.*?de [0-9]{4})))", texto_conteudo) 
            portaria = texto_conteudo[localiza_portaria.span()[0]:localiza_portaria.span()[1]]
            localiza_decreto = re.search("(Decreto ((.*?[0-9]{2}[\.][0-9]{3})|(.*?[0-9]{1}[\.][0-9]{3})), de(.*?[0-9](.*?de [0-9]{4})))", texto_conteudo)
            decreto = texto_conteudo[localiza_decreto.span()[0]:localiza_decreto.span()[1]]
            ementa = "Altera a composição do Grupo de Trabalho de Avaliação Nacional de Riscos de Lavagem de Dinheiro, de Financiamento do Terrorismo e de Financiamento da Proliferação de Armas de Destruição em Massa, de que tratam o " + decreto + " e a " + portaria + "." 
        #Se eoncontrar somente o decreto:
        elif re.search("(Decreto ((.*?[0-9]{2}[\.][0-9]{3})|(.*?[0-9]{1}[\.][0-9]{3})), de(.*?[0-9](.*?de [0-9]{4})))", texto_conteudo, re.IGNORECASE): 
            #Obtém o intervalo que está localizado o decreto no texto:
            localiza_decreto = re.search("(Decreto ((.*?[0-9]{2}[\.][0-9]{3})|(.*?[0-9]{1}[\.][0-9]{3})), de(.*?[0-9](.*?de [0-9]{4})))", texto_conteudo)
            decreto = texto_conteudo[localiza_decreto.span()[0]:localiza_decreto.span()[1]]
            ementa = "Altera a composição do Grupo de Trabalho de Avaliação Nacional de Riscos de Lavagem de Dinheiro, de Financiamento do Terrorismo e de Financiamento da Proliferação de Armas de Destruição em Massa, de que trata o " + decreto + "."
        #Se encontrar somente a portaria:
        elif re.search("(Portaria (.*?[0-9]{3}[\.][0-9]{3}), de(.*?[0-9](.*?de [0-9]{4})))", texto_conteudo, re.IGNORECASE): 
            #Obtém o intervalo que está localizada a portaria no texto:
            localiza_portaria =  re.search("(Portaria (.*?[0-9]{3}[\.][0-9]{3}), de(.*?[0-9](.*?de [0-9]{4})))", texto_conteudo) 
            portaria = texto_conteudo[localiza_portaria.span()[0]:localiza_portaria.span()[1]]
            ementa = "Altera a composição do Grupo de Trabalho de Avaliação Nacional de Riscos de Lavagem de Dinheiro, de Financiamento do Terrorismo e de Financiamento da Proliferação de Armas de Destruição em Massa, de que trata a " + portaria + "."
        
    return ementa
    

def processar_ementa_padrao(titulo, subtitulo, texto_conteudo, idOficio, artigos_encontrados):
    ementa = ""
    match = re.search("(resolve:)|(resolve :)|(r e s o l v e :)", texto_conteudo, re.IGNORECASE)
    if match:
        inicio = match.end()
        fim = texto_conteudo.find('\n', inicio)
        if fim == -1:
            fim = len(texto_conteudo)

        ementa = texto_conteudo[inicio:fim].replace('Art. 1º ', '').replace('Nomear', 'Nomeia').replace(
            'Homologar', 'Homologa').replace('Exonerar', 'Exonera').replace('Autorizar',
                                                                            'Autoriza').replace(
            'Divulgar', 'Divulga').replace('Dispensar', 'Dispensa').replace("Art. 1º ", "").replace(
            'Designar', 'Designa')
        
        ementa = re.sub('[ ][A-Z]{3}[ ][0-9]{1}[\.][0-9]{2}', '', ementa).replace(", código", '').replace(" código", "")
        ementa = re.sub('(, matrícula(.*?([ ][0-9]{7})))|( matrícula(.*?([ ][0-9]{7})))', '', ementa)
        ementa = re.sub('(, matrícula(.*?([ ][0-9]{1}[\.][0-9]{3}[\.][0-9]{3}[-][0-9]{1})))|( matrícula(.*?([ ][0-9]{1}[\.][0-9]{3}[\.][0-9]{3}[-][0-9]{1})))', '', ementa)

    #Para caso venha com erro de digitação, sem os dois pontos no final, verificando se é a última palavra do parágrafo:
    elif re.search("resolve", texto_conteudo, re.IGNORECASE):
        match = re.search("resolve", texto_conteudo, re.IGNORECASE)
        inicio = match.end()
        fim = texto_conteudo.find('\n', inicio)
        if fim == -1:
            fim = len(texto_conteudo)

        ementa = texto_conteudo[inicio:fim].replace('Art. 1º ', '').replace('Nomear', 'Nomeia').replace(
            'Homologar', 'Homologa').replace('Exonerar', 'Exonera').replace('Autorizar',
                                                                            'Autoriza').replace(
            'Divulgar', 'Divulga').replace('Dispensar', 'Dispensa').replace("Art. 1º ", "").replace(
            'Designar', 'Designa')
        
        #Limpa o código e a matrícula no texto: --paragrafos somewhere
        ementa = re.sub('[ ][A-Z]{3}[ ][0-9]{1}[\.][0-9]{2}', '', ementa).replace(", código", '').replace(" código", "")
        ementa = re.sub('(, matrícula(.*?([ ][0-9]{7})))|( matrícula(.*?([ ][0-9]{7})))', '', ementa)
        ementa = re.sub('(, matrícula(.*?([ ][0-9]{1}[\.][0-9]{3}[\.][0-9]{3}[-][0-9]{1})))|( matrícula(.*?([ ][0-9]{1}[\.][0-9]{3}[\.][0-9]{3}[-][0-9]{1})))', '', ementa)


    if (ementa == "" or ementa == ".") and not re.search("Parte 2", titulo, re.IGNORECASE): #Pega o primeiro parágrafo que encontrar:
        if subtitulo not in texto_conteudo and titulo not in texto_conteudo and texto_conteudo:
            ementa = texto_conteudo
            
        if len(ementa) > 500: #Define um limite de caracteres na ementa
            final_texto = 500
            while ementa[final_texto] != " ": #Impede que quebre uma palavra do texto
                final_texto -= 1
            ementa = ementa[0:final_texto] + " ..."

    # Por último, pega ememnta para artigos que tem parte 1 e parte 2:
    if ementa == "" and re.search("Parte 2", titulo, re.IGNORECASE):        
        for artigo in artigos_encontrados:
            if artigo.get("idOficio") == idOficio:
                ementa = artigo.get('Ementa', "")
                break

    return ementa