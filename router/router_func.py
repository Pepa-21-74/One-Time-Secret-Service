from fastapi import Body, status, APIRouter, HTTPException, Request
from repository.data import Secret_key_repository
from database import SessionDep
from security import security_instanse
from schemas.secrets_orm import KeyAdd
from services.rate_limiter import security_protection

router = APIRouter(prefix="/keys", tags=["Работа с ключами"])

@router.post("/conceal")
async def generate_secret_key(
    db: SessionDep,
    secret_data:KeyAdd = Body(embed=True)#для формата ключ-значение
):
    
    encrypted_secret = security_instanse.encrypt(secret_data.key)

    hashed_password = None

    if secret_data.password is not None:
        hashed_password = security_instanse.hash_password(secret_data.password)

    new_id = security_instanse.create_secret_key()
    secret_id = await Secret_key_repository.add_secret_record(
        db, encrypted_secret,hashed_password, new_id
    )
    
    return {"id" : secret_id}


@router.post("/secrets/{secret_key}/reveal")
async def get_secret_key(
    secret_key:str, 
    db: SessionDep,
    request: Request,
    password: str | None = Body(None, embed=True)
    ):

    record = await Secret_key_repository.get_secret_password(db, secret_key)

    if record is None:
              raise HTTPException(
              status_code=status.HTTP_403_FORBIDDEN,
              detail="Secret not found or already view"
          )

    if record.hashed_password:
        if not password:

            raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Secret not found or already view"
        )

        if request.client is None:
            client_id = record.id
        
        else:
            client_id = request.client.host
        
        if not security_protection.unblocking(client_id):
        
            if security_protection.is_blocked(client_id):
                raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Too many attempts. Enter the password in 5 minutes."
            ) 

        if not security_instanse.check_password(password, record.hashed_password):

            security_protection.recording_of_failures(client_id)

            if security_protection.is_blocked(client_id):
                raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Too many attempts. Enter the password in 5 minutes."
            ) 

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Incorrect password"
            )


        
    encrypted_secret = await Secret_key_repository.reveal_secret_record(db, secret_key)
    decrypt_secret = security_instanse.decrypt(encrypted_secret)

    return {"secret" : decrypt_secret}