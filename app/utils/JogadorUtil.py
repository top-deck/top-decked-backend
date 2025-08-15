from collections import defaultdict
from app.core.db import SessionDep
from app.models import Jogador, JogadorTorneioLink, Torneio, Rodada
from sqlmodel import select
from typing import List
from app.utils.Enums import MesEnum
from app.utils.TorneioUtil import calcular_taxa_vitoria

def calcular_estatisticas(session: SessionDep, jogador: Jogador):
    estat_por_mes = _retornar_estatisticas(session, jogador.pokemon_id)
    
    torneios_links = session.exec(select(JogadorTorneioLink)
                                  .where(JogadorTorneioLink.jogador_id == jogador.pokemon_id))

    torneios_historico = _retornar_estatisticas_torneio(session, jogador, torneios_links)
    return {estat_por_mes, torneios_historico}

def _retornar_estatisticas_torneio(session: SessionDep, jogador: Jogador, 
                                   torneios_links: List["JogadorTorneioLink"]):
    estatisticas = []
    for link in torneios_links:
        colocacao = colocacao_jogador(session, link.torneio, jogador)
        estatisticas.append({
            "id" : link.torneio_id,
            "nome" : link.torneio.nome,
            "data_inicio" : link.torneio.data_inicio,
            "colocacao": colocacao,
            "participantes": len(link.torneio.jogadores),
            "pontuacao": link.pontuacao_com_regras
        })
    return estatisticas
        
def _retornar_estatisticas(session: SessionDep, jogador_id: str):
    rodadas = session.exec(
        select(Rodada).where(
            (Rodada.jogador1_id == jogador_id) or
            (Rodada.jogador2_id == jogador_id)
        )
    ).all()
    links = session.exec(
        select(JogadorTorneioLink)
        .where(JogadorTorneioLink.jogador_id == jogador_id)
    ).all()

    estatisticas = defaultdict(lambda: {"pontos": 0, "vitorias": 0, "derrotas": 0, "empates": 0})
    for link in links:
        ano = link.torneio.data_inicio.year
        mes = link.torneio.data_inicio.month
        chave = (ano, mes)
        estatisticas[chave]["pontos"] += link.pontuacao_com_regras or 0
        
    for rodada in rodadas:
        ano = rodada.data_de_inicio.year
        mes = rodada.data_de_inicio.month
        chave = (ano, mes)

        if not rodada.vencedor:
            estatisticas[chave]["empates"] += 1
        elif rodada.vencedor == jogador_id:
            estatisticas[chave]["vitorias"] += 1
        else:
            estatisticas[chave]["derrotas"] += 1

    resultado_formatado = []
    for (ano, mes), dados in sorted(estatisticas.items()):
        resultado_formatado.append({
            "mes": MesEnum.abreviacao(mes),
            "ano": ano,
            "pontos": dados["pontos"],
            "vitorias": dados["vitorias"],
            "derrotas": dados["derrotas"],
            "empates": dados["empates"]
        })

    return resultado_formatado

def colocacao_jogador(session: SessionDep, torneio: Torneio, jogador: Jogador):
    ranking = []
    for j in torneio.jogadores:
        pontuacao = j.pontuacao
        forca_oponentes = calcular_forca_oponente(session, torneio, j)
        ranking.append((j, pontuacao, forca_oponentes))

    ranking.sort(key=lambda x: (x[1], x[2]), reverse=True)
    
    for i, (j, _, _) in enumerate(ranking, start=1):
        if j.id == jogador.id:
            return i
    return None

def calcular_forca_oponente(session: SessionDep, torneio: Torneio, jogador: Jogador):
    oponentes_vencidos = []
    rodadas = session.exec(
        select(Rodada).where(Rodada.torneio_id == torneio.id)
    ).all()

    for rodada in rodadas:
        if rodada.vencedor_id == jogador.id:
            oponente_id = rodada.jogador2_id if rodada.jogador1_id == jogador.id else rodada.jogador1_id
            oponentes_vencidos.append(oponente_id)
    
    if not oponentes_vencidos:
        return 0

    taxas = []
    for op_id in oponentes_vencidos:
        op_jogador = session.get(Jogador, op_id)
        taxas.append(calcular_taxa_vitoria(session, torneio, op_jogador))

    return sum(taxas) / len(taxas)