from fastapi import HTTPException, APIRouter
from core import SessionDep
from models import LojaCriar, LojaPublico, LojaAtualizar, Loja
from models.Usuario import Usuario
from sqlmodel import select

router = APIRouter(tags=["Lojas"])


@router.post("/lojas/", response_model=LojaPublico)
def criar_loja(loja: LojaCriar, session: SessionDep):
    novo_usuario = Usuario(
        email=loja.usuario.email
    )
    novo_usuario.set_senha(loja.usuario.senha)
    session.add(novo_usuario)
    session.commit()
    session.refresh(novo_usuario)

    db_loja = Loja(
        nome=loja.nome,
        endereco=loja.endereco,
        usuario_id=novo_usuario.id,
        usuario=novo_usuario
    )
    session.add(db_loja)
    session.commit()
    session.refresh(db_loja)
    return db_loja


@router.get("/lojas/", response_model=list[LojaPublico])
def retornar_lojas(session: SessionDep):
    lojas = session.exec(select(Loja))
    return lojas


@router.get("/lojas/{loja_id}", response_model=LojaPublico)
def retornar_loja(loja_id: int, session: SessionDep):
    loja = session.get(Loja, loja_id)
    if not loja:
        raise HTTPException(status_code=404, detail="Loja não encontrada")
    return loja


@router.patch("/lojas/{loja_id}", response_model=LojaPublico)
def atualizar_loja(loja_id: int, loja: LojaAtualizar, session: SessionDep):
    loja_db = session.get(Loja, loja_id)
    if not loja_db:
        raise HTTPException(status_code=404, detail="Loja não encontrada")
    loja_data = loja.model_dump(exclude_unset=True)
    loja_db.sqlmodel_update(loja_data)
    session.add(loja_db)
    session.commit()
    session.refresh(loja_db)
    return loja_db


@router.delete("/lojas/{loja_id}")
def apagar_loja(loja_id: int, session: SessionDep):
    loja = session.get(Loja, loja_id)
    if not loja:
        raise HTTPException(status_code=404, detail="Loja não encontrada")
    session.delete(loja)
    session.commit()
    return {"ok": True}
