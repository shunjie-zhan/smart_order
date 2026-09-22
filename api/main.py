"""
es la capa exterior, donde se implementa FastApi,
donde se expone tres api para:
1. POST /chat - interfaz de chat
2. POST /delivery - interfaz de reparto
3. GET /menu/list - interfaz de lista de menu

"""
from fastapi import FastAPI

app = FastAPI(title="API para smart order", description="expone tres API: /chat, /delivery  /menu/list")


# @app.get("/")
# def read_root():
#     return {"Hello": "World"}
#
#
# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: str | None = None):
#     return {"item_id": item_id, "q": q}
