from fastapi.security import OAuth2PasswordRequestForm
from internal.Token import create_access_token
from fastapi import APIRouter, status, HTTPException, Depends
from database import database, Users
from passlib.hash import pbkdf2_sha256

router = APIRouter(
    tags=["Log In"]
)


@router.post('/login/', summary="Performs authentication")
async def log_in(request: OAuth2PasswordRequestForm = Depends()):
    """
    Performs authentication and returns the authentication token to keep the user
    logged in for a longer time.

    Provide **Username** and **Password** to log in.
    """
    try:
        # Use asynchronous code to perform database queries
        query = Users.select().where(Users.c.name == request.username)
        my_user = await database.fetch_one(query=query)

        # If user not found, raise HTTPException
        if not my_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Verify password using pbkdf2_sha256
        if not pbkdf2_sha256.verify(request.password, my_user.password):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Password is incorrect")

        # Create and return the access token
        access_token = create_access_token(data={"sub": my_user.name, "id": my_user.id, "user_type":my_user.user_type})
        return {"access_token": access_token, "token_type": "bearer"}

    # Handle any unexpected errors with a generic HTTPException
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


