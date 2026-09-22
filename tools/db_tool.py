"""
se encarga de la gestion de base de dato MySQL, relacionado con menu_items

"""
from typing import List, Dict,Any
import logging
from logging import Logger

import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""manejo de base de dato"""
class DataBaseConnection:
    """instancia de la base de dato"""
    def __init__(self):
        """configuracion de la base de dato"""
        self.host = os.getenv("MYSQL_HOST","localhost")
        self.port = os.getenv("MYSQL_PORT","3306")
        self.user = os.getenv("MYSQL_USER_NAME","root")
        self.password = os.getenv("MYSQL_USER_PASSWORD","root")
        self.db_name = os.getenv("MYSQL_DB_NAME","menu")

        """instancia de conexion y instancia de cursor"""
        self.connection=None
        self.cursor=None

    """establece conecion de BD"""
    def initialize_connection(self)->bool:
        try:
            # 1.iniciar conector
            self.connection = mysql.connector.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                database=self.db_name,
                charset="utf8")

            # 2.iniciar cursor
            self.cursor = self.connection.cursor(dictionary=True)
            logger.info(f'Conectado con la base de dato {self.db_name}')
            return True

            pass
        except mysql.connector.Error as err:
            logger.error(f'Base de dato: {self.db_name} con error:{err}')
            return False

    """close BD"""
    def close_connection(self)->bool:
        try:
            if self.cursor:
                self.cursor.close()
                self.cursor = None

            if self.connection and self.connection.is_connected():
                self.connection.close()
                self.connection = None
            logger.debug(f'Close BD con exito {self.db_name}')
            return True
        except mysql.connector.Error as err:
            logger.error(f'Close de Base de dato: {self.db_name} con error:{err}')
            return False

    """manejo automatico de instancia con WITH"""
    """enter: ejecuta antes de with"""
    def __enter__(self):
        if self.initialize_connection():
            logger.info(f'Auto coneccion BD: {self.db_name}')
            return self
        else:
            raise Exception(f'Auto coneccion BD con error: {self.db_name}')
    """exit: ejecuta despues de with"""
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        :param exc_type: exception type
        :param exc_val: exception value
        :param exc_tb: exception trackBack code
        :return:
        """
        self.close_connection()

        if exc_type:
            logger.error(f'Auto desconecion con error: {exc_val} con codigo: {exc_tb}')
        return False

def test_connection():
    with DataBaseConnection() as db:
        db.cursor.execute('select 1')
        db_result = db.cursor.fetchone()
        if db_result:
            # logger.info(f'Conecion exitosa: {db_result}')
            print(f'Conecion exitosa: {db_result}')
        else:
            logger.error(f'Conecion error: {db_result}')

def get_string_menu_items() ->str:
    """
    coger todo los items, conectando con \n, y devolviendo string, para vectorizar
    :return:str
    """
    try:
        with (DataBaseConnection() as db):
            # 1. setencia sql
            query_sql = """
            SELECT
                id,dish_name,price,description,category,
                spice_level,flavor,main_ingredients,cooking_method,
                is_vegetarian,allergens,is_available
            FROM menu_items
            WHERE is_available = 1
            ORDER BY category, dish_name
            """
            # 2.ejecutar sql
            db.cursor.execute(query_sql)
            menu_items = db.cursor.fetchall()

            # 3. procesar resultado
            if not menu_items:
                logger.error(f'No items found')
                return "No menu items encontrado"

            menu_factorizado = []
            for item in menu_items:
                # 3.1 formatear spice_level
                spice_level_mapping = {
                    0: "no picante",
                    1: "poco picante",
                    2: "medio picante",
                    3: "muy picante"
                }
                formated_spice_level=spice_level_mapping.get(item.get('spice_level'),
                                                             "sin resultado de picante")

                # 3.2 formatear is_vegetarian
                formated_is_vegetarian= "vegetal" if item.get('is_vegetarian') else "no vegetal"

                # 3.3 formatear description
                formated_description = item.get('description') if item.get('description').strip() else "sin decripcion"

                # 3.4 formatear main_ingredients
                formated_main_ingredients = item.get('main_ingredients') if item.get('main_ingredients').strip() else "sin ingredientes"

                # 3.5 formatear allergens
                formated_allergens = item.get('allergens') if item.get('allergens').strip() else "sin alergicos"
                menu_item_concatenated = f"platoID:{item['id']}|NombrePlato:{item['dish_name']}|precio:{item['price']:.2f}€|descripcion:{formated_description}|categoria:{item['category']}|picor:{formated_spice_level}|sabor:{item['flavor']}|ingredientePrincipal:{formated_main_ingredients}|metodoCoccion:{item['cooking_method']}|vegetal:{formated_is_vegetarian}|alergico:{formated_allergens}"
                menu_factorizado.append(menu_item_concatenated)

            # 4. return resultado
            logger.info(f"Total platos extraidos: {len(menu_factorizado)}")
            return "\n".join(menu_factorizado)

    except Exception as err:
        logger.error(f'Error al consultar todo los items: {err}')
        return "False"

def get_all_list_items() -> List[Dict[str,Any]] :
    """

    :return: una lista que contiene dicto de String + variable
    """

    try:
        with (DataBaseConnection() as db):
            # 1. sentencia SQL
            query_sql = """
            SELECT
                id,dish_name,price,description,category,
                spice_level,flavor,main_ingredients,cooking_method,
                is_vegetarian,allergens,is_available
            FROM menu_items
            WHERE is_available = 1
            ORDER BY category, dish_name
            """
            # 2. ejecutar SQL
            db.cursor.execute(query_sql)

            # 3. obtener resultado
            db_result = db.cursor.fetchall()

            # 4. processar resultado + return
            if not db_result:
                logger.error(f'No items found')
                return []

            menu_lista= []
            for item in db_result:
                # 4.1 mapper of spice level
                spice_level_mapping = {
                    0: "no picante",
                    1: "poco picante",
                    2: "medio picante",
                    3: "muy picante"
                }
                formated_spice_level = spice_level_mapping.get(item.get('spice_level'),"sin resultado de picante")

                processed_item = {
                  "id": item['id'],
                  "dish_name": item['dish_name'],
                  "price": float(item['price']),
                  "formatted_price": f"{item['price']:.2f}€",
                  "description": item['description'] or "sin descripcion",
                  "category": item['category'],
                  "spice_level": item['spice_level'],
                  "formatted_spice": formated_spice_level,
                  "flavor": item['flavor'] or "sin sabor",
                  "main_ingredients": item['main_ingredients'] or "sin ingredientes",
                  "cooking_method": item['cooking_method'] or "sin metodo coccion",
                  "is_vegetarian": bool(item['is_vegetarian']),
                  "formatted_vegetarian": "si" if item['is_vegetarian'] else "no" ,
                  "allergens": item['allergens'] if item['allergens'].strip() else "sin alergicos",
                  "is_available": bool( item['is_available'])
                }
                menu_lista.append(processed_item)

                # 4. return resultado
            logger.info(f"Total platos extraidos: {len(menu_lista)}")
            return menu_lista

    except Exception as err:
        logger.error(f'Error al leer lista de los items: {err}')
        return []

# if __name__ == '__main__':
#     print(f'Test con la conecion de BD')
#     test_connection()

# if __name__ == '__main__':
#     print("todo platos en string")
#     menu_items = get_all_menu_items()
#     print(menu_items)
#     print("v12")

# if __name__ == '__main__':
#     print("todo platos en lista")
#     menu_items = get_all_list_items()
#     # for item in menu_items:
#     #     print(item)
#     for index, item in enumerate(menu_items):
#         print(f"Con enumeracion {index + 1}, el plato es{item}")





