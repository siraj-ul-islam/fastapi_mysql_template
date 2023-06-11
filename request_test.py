# import requests
#
# data = [
#     {"title": "Note 1", "content": "Content 1"},
#     {"title": "Note 2", "content": "Content 2"},
#     {"title": "Note 3", "content": "Content 3"}
# ]
#
# response = requests.post("http://localhost:8000/notes/bulk_create/", json=data)
# if response.status_code == 201:
#     created_notes = response.json()
#     print(created_notes)
# else:
#     print(f"Failed to create notes. Status code: {response.status_code}")
#
#
# note_ids = [123, 456, 789]  # List of note IDs to delete
# url = "http://your-api-url/notes/bulk_delete/"
#
# response = requests.post(url, json=note_ids)
# if response.status_code == 204:
#     print("Bulk delete operation successful.")
# else:
#     print(f"Failed to perform