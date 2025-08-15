from app.core.db import SessionDep
from app.schemas.Ranking import Ranking, RankingPorLoja
from sqlmodel import select, extract
from sqlalchemy.orm import joinedload, selectinload
from app.models import Jogador, JogadorTorneioLink, Rodada, Loja, Torneio
from app.utils.TorneioUtil import calcular_taxa_vitoria


def calcula_ranking_geral(session: SessionDep):
    jogadores = session.exec(
        select(Jogador)
        .options(
            joinedload(Jogador.torneios)
            .joinedload(JogadorTorneioLink.torneio),
            joinedload(Jogador.usuario),
        )
    ).all()
    ranking = []
    
    for jogador in jogadores:
        total_pontos = 0
        total_torneios = 0
        total_vitorias = 0
        total_derrotas = 0
        total_empates = 0

        for link in jogador.torneios:
            torneio = link.torneio
            if not torneio:
                continue

            total_torneios += 1
            total_pontos += int(link.pontuacao_com_regras)

            rodadas = session.exec(
                select(Rodada).where(
                    (Rodada.torneio_id == link.torneio_id) &
                    ((Rodada.jogador1_id == jogador.pokemon_id) or (Rodada.jogador2_id == jogador.pokemon_id))
                )
            ).all()

            for rodada in rodadas:
                if(rodada.vencedor == jogador.pokemon_id):
                    total_vitorias += 1
                elif(rodada.vencedor is not None):
                    total_derrotas += 1
                else:
                    total_empates += 1

        ranking.append(Ranking(
            nome_jogador=jogador.nome,
            pontos=total_pontos,
            torneios=total_torneios,
            vitorias=total_vitorias,
            derrotas=total_derrotas,
            empates=total_empates,
            taxa_vitoria= calcular_taxa_vitoria(session,jogador)
        ))

    ranking.sort(key=lambda x: x.pontos, reverse=True)

    return ranking

def calcula_ranking_geral_por_loja(session: SessionDep, mes: int = None):
    lojas = session.exec(select(Loja)).all()
    jogadores = session.exec(select(Jogador)).all()
    ranking = []
    for loja in lojas:
        for jogador in jogadores:
            links = session.exec(
                select(JogadorTorneioLink)
                .join(JogadorTorneioLink.torneio)
                .where(
                    JogadorTorneioLink.jogador_id == jogador.pokemon_id,
                    Torneio.loja_id == loja.id,
                    ((mes is None) or (extract('month', Torneio.data_inicio) == mes))
                )
            ).all()
            if(links == []):
                continue
            total_pontos = 0
            total_torneios = 0
            total_vitorias = 0
            total_derrotas = 0
            total_empates = 0
            for link in links:
                total_torneios += 1
                total_pontos += int(link.pontuacao_com_regras)

                rodadas = session.exec(
                    select(Rodada).where(
                        (Rodada.torneio_id == link.torneio_id) &
                        ((Rodada.jogador1_id == jogador.pokemon_id) or (Rodada.jogador2_id == jogador.pokemon_id))
                    )
                ).all()

                for rodada in rodadas:
                    if(rodada.vencedor == jogador.pokemon_id):
                        total_vitorias += 1
                    elif(rodada.vencedor is not None):
                        total_derrotas += 1
                    else:
                        total_empates += 1
            total_rodadas = total_vitorias + total_derrotas + total_empates
            taxa_vitoria = int((total_vitorias / total_rodadas) * 100) if total_rodadas > 0 else 0

            ranking.append(RankingPorLoja(
                nome_jogador=jogador.nome,
                nome_loja=loja.nome,
                pontos=total_pontos,
                torneios=total_torneios,
                vitorias=total_vitorias,
                derrotas=total_derrotas,
                empates=total_empates,
                taxa_vitoria= taxa_vitoria
            ))
        
    ranking.sort(key=lambda x: x.pontos, reverse=True)

    return ranking