"""

basado en el modelo MVC, se encarga de implementar las funciones esenciales
api/main -> service
1. smart_chat: invocar tool/assistant.py -> chat_with_assistant
2. delivery_check: invocar check_delivery_range
3. get_menu: invocar get_menu_items_list
"""
from smart_order.tools.amap_tool import check_range, pathInput


def get_menu():
    """
    Desde Model obtiene el dato para dar a vista
    :return:
    """
    from smart_order.tools.db_tool import get_all_list_items
    return get_all_list_items()

def check_delivery_range(address:str, mode:pathInput="2"):
    return check_range(address,mode)