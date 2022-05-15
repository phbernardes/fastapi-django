from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from rest_framework_simplejwt.authentication import JWTAuthentication

from users.models import User

__all__ = ["UserAuthentified"]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_authentified_user(token: str = Depends(oauth2_scheme)) -> User:
    jwt_authenticator = JWTAuthentication()
    validated_token = jwt_authenticator.get_validated_token(token)

    user = jwt_authenticator.get_user(validated_token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


UserAuthentified: User = Depends(get_authentified_user)
