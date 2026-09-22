"""

basado en el modelo MVC, se encarga de implementar las funciones esenciales
api/main -> service
1. smart_chat: invocar tool/assistant.py -> chat_with_assistant
2. delivery_check: invocar check_delivery_range
3. get_menu: invocar get_menu_items_list
"""
def get_menu():
    """
    Desde Model obtiene el dato para dar a vista
    :return:
    """
    from smart_order.tools.db_tool import get_all_list_items
    return get_all_list_items()
