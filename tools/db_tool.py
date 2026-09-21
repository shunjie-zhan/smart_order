"""
se encarga de la gestion de base de dato MySQL, relacionado con menu_items

"""
import logging
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
            logger.info(f'Conecion exitosa: {db_result}')
        else:
            logger.error(f'Conecion error: {db_result}')

if __name__ == '__main__':
    print(f'Test con la conecion de BD')
    test_connection()




