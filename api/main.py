"""
es la capa exterior, donde se implementa FastApi,
donde se expone tres api para:
1. POST /chat - interfaz de chat
2. POST /delivery - interfaz de reparto
3. GET /menu/list - interfaz de lista de menu

"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(title="API para smart order", description="expone tres API: /chat, /delivery  /menu/list")


class MenuListResponse(BaseModel):
    success: bool  # estado
    menu_items: List[dict]  # lista
    count: int  # numero
    message: str  # http response


@app.get("/menu/list", response_model=MenuListResponse)
async def menu_list():
    # 1. invocar metodo de service
    from smart_order.service.order_service import get_menu
    list_menu = get_menu()

    if not list_menu:
        return MenuListResponse(
            success=False,
            menu_items=[],
            count=0,
            message="No menu list"
        )
    return MenuListResponse(
        success=True,
        menu_items=list_menu,
        count=len(list_menu),
        message="Lista enviada"
    )



# def read_root():
#     return {"Hello": "World"}
#
#
# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: str | None = None):
#     return {"item_id": item_id, "q": q}
