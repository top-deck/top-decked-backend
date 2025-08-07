from fastapi import HTTPException, APIRouter
from app.core.db import SessionDep
from app.models.Loja import LojaCriar, LojaPublico, LojaAtualizar, Loja
from app.models.Usuario import Usuario
from sqlmodel import select
from app.services.UsuarioService import verificar_novo_usuario


router = APIRouter(
    prefix="/lojas",
    tags=["Lojas"])

@router.post("/", response_model=LojaPublico)
def criar_loja(loja: LojaCriar, session: SessionDep):
    verificar_novo_usuario(loja.email, session)
    
    novo_usuario = Usuario(
        email=loja.email,
        tipo="loja"
    )
    novo_usuario.set_senha(loja.senha)
    
    session.add(novo_usuario)
    session.commit()
    session.refresh(novo_usuario)

    db_loja = Loja(
        nome=loja.nome,
        endereco=loja.endereco,
        usuario=novo_usuario
    )
    
    session.add(db_loja)
    session.commit()
    session.refresh(db_loja)
    return db_loja


@router.get("/", response_model=list[LojaPublico])
def retornar_lojas(session: SessionDep):
    lojas = session.exec(select(Loja))
    return lojas


@router.get("/{loja_id}", response_model=LojaPublico)
def retornar_loja(loja_id: int, session: SessionDep):
    loja = session.get(Loja, loja_id)
    if not loja:
        raise HTTPException(status_code=404, detail="Loja não encontrada")
    return loja


@router.patch("/{loja_id}", response_model=LojaPublico)
def atualizar_loja(loja_id: int, loja: LojaAtualizar, session: SessionDep):
    loja_db = session.get(Loja, loja_id)
    if not loja_db:
        raise HTTPException(status_code=404, detail="Loja não encontrada")

    loja_data = loja.model_dump(exclude_unset=True)

    if "senha" in loja_data and loja_data["senha"]:
        loja_db.usuario.set_senha(loja_data["senha"])
        session.add(loja_db.usuario)
        loja_data.pop("senha")

    loja_db.sqlmodel_update(loja_data)
    session.add(loja_db)
    session.commit()
    session.refresh(loja_db)
    return loja_db

@router.delete("/{loja_id}")
def apagar_loja(loja_id: int, session: SessionDep):
    loja = session.get(Loja, loja_id)
    if not loja:
        raise HTTPException(status_code=404, detail="Loja não encontrada")
    session.delete(loja)
    session.commit()
    return {"ok": True}
