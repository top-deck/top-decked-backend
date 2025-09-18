from sqlmodel import select
from app.core.db import SessionDep
from app.models import Rodada, Torneio, Jogador, JogadorTorneioLink


def retornar_torneio_completo(torneio: Torneio):
    torneio_dict = torneio.model_dump()
    
    torneio_dict["loja"] = torneio.loja
    torneio_dict["jogadores"] = [
        {
            "jogador_id": link.jogador_id,
            "nome": link.jogador.nome,
            "tipo_jogador_id": link.tipo_jogador_id,
            "pontuacao": link.pontuacao
        }
        for link in torneio.jogadores
    ]

    torneio_dict["rodadas"] = [
        {
            "jogador1_id": rodada.jogador1_id,
            "jogador2_id": rodada.jogador2_id,
            "vencedor": rodada.vencedor,
            "num_rodada": rodada.num_rodada,
            "mesa": rodada.mesa,
            "data_de_inicio": rodada.data_de_inicio
        }
        for rodada in torneio.rodadas
    ]

    
    return torneio_dict


def editar_torneio_regras(torneio: Torneio, regra_basica: int, regras_adicionais: dict):
    torneio.regra_basica_id = regra_basica
    
    for jogador in torneio.jogadores:
        jogador.pontuacao = 0
        jogador.pontuacao_com_regras = 0
        jogador_id = jogador.jogador_id
        
        if regras_adicionais and jogador_id in regras_adicionais:
            jogador.tipo_jogador_id = regras_adicionais[jogador_id]
        else:
            jogador.tipo_jogador_id = regra_basica
    
    return torneio


def calcular_pontuacao(session: SessionDep, torneio: Torneio):
    regra_basica = torneio.regra_basica
    
    for rodada in torneio.rodadas:
        jogador1_id = rodada.jogador1_id
        jogador2_id = rodada.jogador2_id
        jogador1_link = session.get(JogadorTorneioLink, {"torneio_id": torneio.id,
                                                          "jogador_id": jogador1_id})
        jogador2_link = session.get(JogadorTorneioLink, {"torneio_id": torneio.id,
                                                          "jogador_id": jogador2_id})
        jogador1_tipo = jogador1_link.tipo_jogador
        jogador2_tipo = jogador2_link.tipo_jogador

        if rodada.vencedor == jogador1_id:
            # Jogador 1 ganha os pontos por vitória 
            # e os pontos da regra de derrota do oponente
            jogador1_link.pontuacao_com_regras += (jogador1_tipo.pt_vitoria 
                                                + jogador2_tipo.pt_oponente_ganha)
            # Jogador 2 ganha os pontos por derrota 
            # e os pontos da regra de vitória do oponente (possivelmente negativos)
            jogador2_link.pontuacao_com_regras += (jogador2_tipo.pt_derrota
                                                + jogador1_tipo.pt_oponente_perde)

            jogador1_link.pontuacao += (regra_basica.pt_vitoria
                                           + regra_basica.pt_oponente_ganha)
            
            jogador2_link.pontuacao += (regra_basica.pt_derrota
                                            + regra_basica.pt_oponente_perde)
            
        elif rodada.vencedor == jogador2_id:
            # Jogador 2 ganha os pontos por vitória
            # e os pontos da regra de derrota do oponente
            jogador2_link.pontuacao_com_regras += (jogador2_tipo.pt_vitoria
                                        + jogador1_tipo.pt_oponente_ganha)
            # Jogador 1 ganha os pontos por derrota
            # e os pontos da regra de vitória do oponente (possivelmente negativos)
            jogador1_link.pontuacao_com_regras += (jogador1_tipo.pt_derrota
                                                + jogador2_tipo.pt_oponente_perde)
            
            jogador2_link.pontuacao += (regra_basica.pt_vitoria
                                                   + regra_basica.pt_oponente_ganha)
            
            jogador1_link.pontuacao += (regra_basica.pt_derrota
                                        + regra_basica.pt_oponente_perde)
        else:
            # Jogador 1 ganha os pontos por empate
            # e os pontos da regra de empate do oponente
            jogador1_link.pontuacao_com_regras += (jogador1_tipo.pt_empate
                                                + jogador2_tipo.pt_oponente_empate)
            # Jogador 2 ganha os pontos por empate
            # e os pontos da regra de empate do oponente
            jogador2_link.pontuacao_com_regras += (jogador2_tipo.pt_empate
                                                + jogador1_tipo.pt_oponente_empate)
            
            jogador1_link.pontuacao += (regra_basica.pt_empate
                                        + regra_basica.pt_oponente_empate)
            
            jogador2_link.pontuacao += (regra_basica.pt_empate
                                        + regra_basica.pt_oponente_empate)
            
    jogador1_link.pontuacao_com_regras += torneio.pontuacao_de_participacao
    jogador2_link.pontuacao_com_regras += torneio.pontuacao_de_participacao
    session.add(jogador1_link)
    session.add(jogador2_link)
    
def calcular_taxa_vitoria(session: SessionDep, jogador: Jogador):
    vitorias, derrotas, empates = 0, 0, 0
    
    rodadas = session.exec(select(Rodada).where(
                ((Rodada.jogador1_id == jogador.pokemon_id) | (Rodada.jogador2_id == jogador.pokemon_id))))

    for rodada in rodadas:
        if(rodada.vencedor == jogador.pokemon_id):
            vitorias += 1
        elif(rodada.vencedor is not None):
            derrotas += 1
        else:
            empates += 1
            
    total = vitorias + derrotas + empates
    return int((vitorias / total) * 100) if total > 0 else 0