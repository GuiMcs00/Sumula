from datetime import date, timedelta

from utils import properties

from .holidaysBC import BancoCentralHolidays


ano = date.today().strftime("%Y")
mes = date.today().strftime("%m")
dia = date.today().strftime("%d")
data_completa = ano + "-" + mes + "-" + dia
#Caso seja preciso rodar em uma data diferente do dia atual, preencha a data do dia do teste:
data_dia_teste = properties.get('default','data_dou') #PARA RODAR EM PRODUÇÃO, ESTA DATA DEVE ESTAR VAZIA
data_completa = data_dia_teste if data_dia_teste != "" else data_completa


def feriados(data=data_completa)-> bool:
    feriados = BancoCentralHolidays()
    return data in feriados


def data_anterior_util(data=data_completa):
    data_com = data.split('-')
    ano, mes, dia = int(data_com[0]), int(data_com[1]), int(data_com[2])
    # Troca a data de hoje pela data que o usuário definir
    data_escolhida = date(ano, mes, dia)
    dia_semana = data_escolhida.weekday()
    if dia_semana == 0:  # segunda-feira é representada pelo valor 0
        data_anterior = data_escolhida - timedelta(3)
    else:
        data_anterior = data_escolhida - timedelta(1)
    feriado = feriados(str(data_anterior))
    if feriado is True:
        return str(data_anterior_util(str(data_anterior)))
    else:
        return str(data_anterior)


def data_anterior_feriado(data=data_completa):
    data_com = data.split('-')
    ano = data_com[0]
    mes = data_com[1]
    dia = data_com[2]
    # Troca a data de hoje pela data que o usuário definir
    data_escolhida = date.today().replace(int(ano), int(mes), int(dia))
    dia_semana = data_escolhida.weekday()
    if dia_semana == 0:  # segunda-feira é representada pelo valor 0
        data_anterior = data_escolhida - timedelta(3)
    else:
        data_anterior = data_escolhida - timedelta(1)

    return str(data_anterior)