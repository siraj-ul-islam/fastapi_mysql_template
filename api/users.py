
from models.users import UsersSchema, UsersInSchema
from typing import List
from fastapi import APIRouter, status, Depends, HTTPException
from database import database, Users
from passlib.hash import pbkdf2_sha256
from internal.Token import get_current_user, get_current_active_user

router = APIRouter(
    prefix='/user',
    tags=["Users"]
)


@router.post('/create/', status_code=status.HTTP_201_CREATED,
             response_model=UsersSchema,
             summary="Create a user",
             response_description="User Created")
async def create_user(user: UsersInSchema, current_user: UsersSchema = Depends(get_current_user)):
    """
    Creates a User with the given information:

    - **name**: Username who is adding the information. (STR) *--Required*
    - **password**: Password must be stored against each proxy. (STR)*--Required*
    - **email**: Add email. Must not be added before. (STR) *--Required*
    - **profile_image**: Add profile_image. (STR) *--Optional*
    - **user_type**: Define the user type, i-e admin,user,manager. (STR) *--Required*
    - **credit**: (STR) *--Optional*
    - **created_at**: Auto filled. Can left empty. (DATETIME) *--Optional*
    """
    try:
        # Hash the user's password before inserting into the database
        hashed_password = pbkdf2_sha256.hash(user.password)

        # Insert the user record into the database
        query = Users.insert().values(name=user.name, password=hashed_password, email=user.email,
                                      user_type=user.user_type, profile_image=user.profile_image, credit=user.credit)
        last_record_id = await database.execute(query)

        # Return the created user record
        return {**user.dict(), "id": last_record_id}

    except Exception as e:
        # Log the error for debugging purposes
        print(e)
        # Return an appropriate error response
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create user.")


@router.get('/show/list/', response_model=List[UsersSchema], summary="Get a list of all users")
async def get_users(current_user: UsersSchema = Depends(get_current_user)):
    """
                Returns a list of users with following information:

                `id`,`name`,`remember_token`,`user_type`,`credit`,`email`

    """
    if current_user.user_type != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You don't have permission to access this resource")

    query = Users.select()

    return await database.fetch_all(query=query)


@router.get("/users/me")
async def read_users_me(current_user: UsersSchema = Depends(get_current_active_user)):
    return current_user


@router.delete('/delete/{id}/', status_code=status.HTTP_204_NO_CONTENT,
               summary="Deletes a user from the table.")
async def delete_user(id:int, current_user: UsersSchema = Depends(get_current_user)):
    """
                        Removes a user from the table by providing user id. Successful response is 204.

    """
    query = Users.delete().where(Users.c.id == id)
    my_query = await database.execute(query)
    if not my_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ID does not exist")

    return {"message": "User deleted"}
