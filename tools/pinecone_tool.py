"""
en encargar de la conexion con el base de dato vectorial PineCone y su respectivo manejo

"""
from gettext import textdomain
from operator import index

from dotenv import load_dotenv
load_dotenv()
import os
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from pinecone import Pinecone
from pinecone import ServerlessSpec
from typing import List
import dashscope
from http import HTTPStatus

class PineconeVectorDB:
    """
    encargado de manejo de BD relacionado con el base de dato vectorial PineCone
    """

    def __init__(self):
        # 1. key para servicio nube
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.dashscope_api_key = os.getenv("DASHSCOPE_API_BASE")
        self.pinecone_env = os.getenv("PINECONE_ENV")

        # 2.configuracion de bd y texto vectorial
        self.index_name="smart-order"
        self.embedding_model="qwen3.7-text-embedding-flash"
        self.dimension=1024

        # 3.valorares para configurar pinecone
        self.pinecone=None
        self.index=None

    def initialize_conection(self)-> bool:
        """
        configurar pinecone
        :return:
        """
        try:
            # 1. obtener key para pinecone
            if not self.pinecone_api_key:
                logger.error("PINECONE_API_KEY not set")
                return False
            # 2. establecer coneccion con pinecone
            self.pinecone = Pinecone(api_key=self.pinecone_api_key)
            # 3. crear index para pinecone
            if not self.pinecone.has_index(self.index_name):
                self.pinecone.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=os.getenv(self.pinecone_env),
                    )
                )
            # 4. uso de index de pinecone
            self.index = self.pinecone.Index(self.index_name)
            logger.info("PINECONE INDEX created successfully")
            return True



        except Exception as err:
            logger.error(f"[ERROR al inicializar pinecone] {err}")
            return False

    def clear_vector(self) -> bool:
        """
        clear vector value
        :return:
        """
        try:
            if self.index and self.initialize_conection():
                logger.error("sin index")
                return False

            # 1. si hay valor se elimna
            vector_status=self.index.describe_index_status()
            pc_vector_count=vector_status.total_vector_count
            if pc_vector_count == 0:
                logger.info("sin index")
                return True
            self.index.delete_index(delete_all=True)
            logger.info("eliminado todo index")
            return True
        except Exception as err:
            logger.error(f"[ERROR al clear pinecone] {err}")
            return False

    def _embedding_content(self, content:str) ->List[float] or None:
        """
        encargado de vectorizar str
        :param content:
        :return: [0.112321,0.1232123 ...]
        """
        try:
            # 1. procesar texto
            resp = dashscope.TextEmbedding.call(
                api_key=self.pinecone_api_key,
                model=self.embedding_model,
                input=content,
                dimension=self.dimension,  # 指定向量维度（仅 qwen3.7-text-embedding、text-embedding-v3及 text-embedding-v4支持该参数）
            )
            # 2. procesar resultado
            if resp.status_code == HTTPStatus.OK:
                logger.info(f"[String -> vector]")
                return resp.output.embeddings[0].embedding
            else:
                logger.error(f"[Error -> vector]")
                return None
        except Exception as err:
            logger.error(f"[ERROR al embedding content] {err}")
            return None
            pass

    def upset_menu_data(self,menu_data:str, batch_size:int=100,clear_existed:bool=True)->bool:
        """
        almacenar vector a pinecone
        :arg1 string a procesar
        :arg2 int batch_size buffer para procesar
        :arg3 bool clear_existed bool para eliminar
        :return:
        """

        try:
            if not menu_data:
                # 1. consultar BD si no existe
                from smart_order.tools.db_tool import get_string_menu_items
                menu_data = get_string_menu_items()
            else:
                # 2.procear texto
                #3. vectorizar
                #4. almancenar
        except Exception as err:
            logger.error(f"[ERROR al almacenar Vector DB] {err}")
            return  False

    def _validation_str(self,str_validation:str)->bool:
        """

        :param str_validation:
        :return:
        """
        # 1. si hay datos
        if not str_validation:
            logger.error("sin dato para validacion")
            return False

        # 2. validacion de str
        None
        print("22")

