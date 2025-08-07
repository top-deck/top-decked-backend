from fastapi import HTTPException

class TopDeckedException:
    def bad_request(message: str):
        return HTTPException(
            status_code=400,
            detail=message)
    
    def forbidden():
        return HTTPException(
            status_code=401,
            detail="Autenticação negada",
            headers={"WWW-Authenticate": "Bearer"})

    def unauthorized():
        return HTTPException(
            status_code=403,
            detail="Permissão negada",
            headers={"WWW-Authenticate": "Bearer"})

    def not_found(message: str):
        return HTTPException(
            status_code=404, 
            detail=message)
        
EXCEPTIONS = TopDeckedException()