"""
es la capa exterior, donde se implementa FastApi,
donde se expone tres api para:
1. POST /chat - interfaz de chat
2. POST /delivery - interfaz de reparto
3. GET /menu/list - interfaz de lista de menu

"""
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from smart_order.service.order_service import check_delivery_range
from smart_order.tools.amap_tool import pathInput

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


class DeliveryResponse(BaseModel):
    success: bool
    in_range: bool
    distance: float
    formatted_address: str  # in geo-located
    duration: float
    message: str
    travel_mode: pathInput
    input_address: str


class DeliveryRequest(BaseModel):
    address: str
    travel_mode: pathInput = "2"


@app.post("/delivery", response_model=DeliveryResponse)
async def delivery(request: DeliveryRequest):
    """
    Api para conectar con web sobre reparto
    :param request:
    :return:
    """
    # logger.debug(f"DeliveryRequest: {request}")
    try:
        # logger.debug(f"DeliveryRequest: {request}")
        result_distance = check_delivery_range(request.address, request.travel_mode)
        if result_distance["status"] == "fail":
            return DeliveryResponse(
                success=False,
                in_range=False,
                distance=0.0,
                formatted_address=request.input_address,
                duration=0.0,
                message=result_distance["message"],
                travel_mode=request.travel_mode,
                input_address=request.input_address,
            )
        return DeliveryResponse(
            success=True,
            in_range=result_distance["in_range"],
            distance=result_distance["distance"],
            formatted_address=result_distance["formatted_distance"],
            duration=result_distance["duration"],
            message=result_distance["message"],
            travel_mode=request.travel_mode,
            input_address=request.address,

        )
    except Exception as err:
        logging.error(f"Error en /delivery: {err}")
        return DeliveryResponse(
            success=False,
            message=f'Error en /delivery: {err}'
        )

# def read_root():
#     return {"Hello": "World"}
#
#
# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: str | None = None):
#     return {"item_id": item_id, "q": q}
