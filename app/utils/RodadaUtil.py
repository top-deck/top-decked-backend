from app.core.db import SessionDep
from app.models import Torneio, Rodada, JogadorTorneioLink, Jogador
from sqlmodel import select
from datetime import datetime
from app.utils.JogadorUtil import retornar_vde_jogador

def nova_rodada(session: SessionDep, torneio: Torneio):
    jogadores = session.exec(select(JogadorTorneioLink)
                             .where(JogadorTorneioLink.torneio_id == torneio.id)).all()
    
    jogadores = sorted(jogadores, key=lambda j: (j.pontuacao, j.jogador_id), reverse=True)
    mesa_livre = 1
    rodada_atual = torneio.rodada_atual + 1
    
    jogando = {}
    result = {}
    for i, jogador in enumerate(jogadores):
        adversario = None
        if jogando.get(jogador.jogador_id, False):
            continue
        
        for pos_adversario in jogadores[i+1:]:
            if jogando.get(pos_adversario.jogador_id, False):
                continue
            

            ja_jogaram = session.exec(
                select(Rodada).where(
                    ((Rodada.jogador1_id == jogador.jogador_id) &
                    (Rodada.jogador2_id == pos_adversario.jogador_id))
                    |
                    ((Rodada.jogador1_id == pos_adversario.jogador_id) &
                    (Rodada.jogador2_id == jogador.jogador_id))
                )
            ).first()
            
            if ja_jogaram:
                continue
            
            adversario = pos_adversario
            break
        
        nova_rodada = Rodada(
            jogador1_id=jogador.jogador_id,
            jogador2_id=adversario.jogador_id if adversario else None,
            torneio_id=torneio.id,
            num_rodada=rodada_atual,
            mesa=mesa_livre,
            data_de_inicio=datetime.now(),
            finalizada=False
        )
        session.add(nova_rodada)
        
        jogando[jogador.jogador_id] = True
        jogador_vde = retornar_vde_jogador(session, jogador, torneio)
        
        if adversario:
            jogando[adversario.jogador_id] = True
            adversario_vde = retornar_vde_jogador(session, adversario, torneio)
            adversario = session.exec(select(Jogador)
                                        .where(Jogador.pokemon_id == adversario.jogador_id)).first()
        
        
        jogador = session.exec(select(Jogador)
                                .where(Jogador.pokemon_id == jogador.jogador_id)).first()
        
        result[mesa_livre] = [
            {
                "jogador_id" : jogador.pokemon_id,
                "usuario_id" : jogador.usuario_id,
                "jogador_nome" : jogador.nome,
                **jogador_vde
            }, 
            {
                "jogador_id": adversario.pokemon_id,
                "usuario_id": adversario.usuario_id,
                "jogador_nome": adversario.nome,
                **adversario_vde
            } if adversario else {}
        ]

        mesa_livre += 1
            
    torneio.rodada_atual = rodada_atual
    session.add(torneio)
    
    return result
