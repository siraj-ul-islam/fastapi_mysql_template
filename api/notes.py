import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page, paginate
from sqlalchemy import select
from database import database, Notes, Users
from internal.Token import get_current_user
from models.notes import NoteDB,NoteCreate,NoteUpdate,UserDB, User,NoteBase,UserBase
from starlette.responses import Response

router = APIRouter(
    prefix='/notes',
    tags=['Notes'],
)


@router.post('/create/', status_code=status.HTTP_201_CREATED, response_model=NoteDB,
             summary="Create a Note", response_description="Note Created")
async def create_note(record: NoteCreate, current_user: UserDB = Depends(get_current_user)):
    """
        Creates a new note with the given information:

        - **title**: Title of the note. (STR) *--Required*
        - **content**: Content of the note. (STR) *--Optional*
        """
    try:
        query = Notes.insert().values(user_id=current_user.id, title=record.title, content=record.content)
        last_record_id = await database.execute(query)

        new_record = await database.fetch_one(Notes.select().where(Notes.c.id == last_record_id))
        return new_record
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get('/get/all/notes/', response_model=Page[NoteDB], summary="Get a list of all Notes")
async def get_notes(current_user: UserDB = Depends(get_current_user)):
    """
        Returns a paginated list of all notes belonging to the current user.
    """
    try:
        query = Notes.select().where(Notes.c.user_id == current_user.id)
        return paginate(await database.fetch_all(query))
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get('/get/note/{note_id}', response_model=NoteDB, summary="Get a Note by ID")
async def get_note(note_id: int, current_user: UserDB = Depends(get_current_user)):
    """
        Returns the note with the specified ID, belonging to the current user.

        - **note_id**: ID of the note to retrieve. (INT) *--Required*
    """
    try:
        query = Notes.select().where((Notes.c.id == note_id) & (Notes.c.user_id == current_user.id))
        note = await database.fetch_one(query)
        if not note:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
        return note
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch note")


@router.delete('/{note_id}/', status_code=status.HTTP_204_NO_CONTENT, summary="Delete a Note")
async def delete_note(note_id: int, current_user: UserDB = Depends(get_current_user)):
    """
        Deletes the note with the specified ID, belonging to the current user.

        - **note_id**: ID of the note to delete. (INT) *--Required*
    """
    try:
        query = Notes.delete().where((Notes.c.id == note_id) & (Notes.c.user_id == current_user.id))
        deleted_count = await database.execute(query)
        if deleted_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.put('/update/{note_id}/', status_code=status.HTTP_200_OK, response_model=NoteDB, summary="Update a Note",
            response_description="Note updated successfully.")
async def update_note(note_id: int, note: NoteUpdate, current_user: UserDB = Depends(get_current_user)):
    """
        Updates the note with the specified ID, belonging to the current user.

        - **note_id**: ID of the note to update. (INT) *--Required*
        - **note**: Updated note information. (NoteUpdate) *--Required*
    """
    try:
        note_record = await database.fetch_one(Notes.select().where(Notes.c.id == note_id))
        if not note_record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
        if note_record.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized to update note")

        query_value = {}
        if note.title:
            query_value['title'] = note.title
        if note.content:
            query_value['content'] = note.content

        query = Notes.update().where((Notes.c.id == note_id) & (Notes.c.user_id == current_user.id)).values(
            **query_value)
        num_updated = await database.execute(query)

        if num_updated == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

        updated_note = await database.fetch_one(Notes.select().where(Notes.c.id == note_id))
        return updated_note

    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post('/bulk_create/', status_code=status.HTTP_201_CREATED, response_model=List[NoteDB],
             summary="Bulk Create Notes", response_description="Notes Created")
async def bulk_create_notes(records: List[NoteCreate], current_user: UserDB = Depends(get_current_user)):
    """
        Creates multiple notes in bulk.

        - **records**: List of note records to create. (List[NoteCreate]) *--Required*
    """
    try:
        values = [
            {'user_id': current_user.id, 'title': record.title, 'content': record.content}
            for record in records
        ]
        query = Notes.insert().values(values)
        last_record_id = await database.execute(query)

        new_record_ids = list(range(last_record_id - len(records) + 1, last_record_id + 1))

        new_records = await database.fetch_all(Notes.select().where(Notes.c.id.in_(new_record_ids)))
        return new_records
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post('/bulk_delete/', status_code=status.HTTP_204_NO_CONTENT, summary="Bulk Delete Notes")
async def bulk_delete_notes(note_ids: List[int], current_user: UserDB = Depends(get_current_user)):
    """
        Deletes multiple notes in bulk.

        - **note_ids**: List of note IDs to delete. (List[int]) *--Required*
    """
    try:
        # Get user ID for current user
        user_id = current_user.id

        # Delete notes with matching IDs and user ID
        query = Notes.delete().where((Notes.c.id.in_(note_ids)) & (Notes.c.user_id == user_id))
        deleted_count = await database.execute(query)

        # If no rows were deleted, raise a 404 error
        if deleted_count != len(note_ids):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        # Return a successful response with no content
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)




