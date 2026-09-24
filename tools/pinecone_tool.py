"""
en encargar de la conexion con el base de dato vectorial PineCone y su respectivo manejo

"""


from dotenv import load_dotenv
load_dotenv()
import os
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from pinecone import Pinecone
from pinecone import ServerlessSpec
from typing import List, Dict, Any
import dashscope
from http import HTTPStatus
import re

class PineconeVectorDB:
    """
    encargado de manejo de BD relacionado con el base de dato vectorial PineCone
    """

    def __init__(self):
        # 1. key para servicio nube
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")
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
            pc_vector_count=vector_status["total_vector_count"]
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
                api_key=self.dashscope_api_key,
                model=self.embedding_model,
                input=content,
                dimension=self.dimension,
            )
            # 2. procesar resultado
            if resp.status_code == HTTPStatus.OK:
                # logger.info(f"[String -> vector] exitosa con HttpStatus:{resp.status_code}")
                return resp.get("output").get("embeddings")[0].get("embedding")
            else:
                logger.error(f"[Error -> vector con HttpStatus:{resp.status_code}]")
                return None
        except Exception as err:
            logger.error(f"[ERROR al embedding content] {err}")
            return None
            pass

    def upset_menu_data(self,menu_data:str=None, batch_size:int=30,clear_existed:bool=True)->bool:
        """
        almacenar vector a pinecone
        :arg1 string a procesar
        :arg2 int batch_size buffer para procesar
        :return:
        """

        # logger.info("inicio de funcion upset_menu_data")
        print("inicio de funcion upset_menu_data")
        try:
            if not menu_data:
                # 1. consultar BD si no existe
                # logger.debug("antes de consulta MySQLDB")
                from smart_order.tools.db_tool import get_string_menu_items
                if clear_existed:
                    self.clear_vector()

                menu_data = get_string_menu_items()
                # 2.procear texto
                if not self._validation_str(menu_data):
                    logger.error("[ERROR -> menu_data] en validacion")
                    return False
                # 2.1. fragmentar
                # logger.debug("antes de fragmentarStr")

                embeding_chunk =self._split_str(menu_data)
                if not embeding_chunk:
                    logger.error("[ERROR -> menu_data] en embedding")
                    return False

                batch=[]
                #3. vectorizarDB
                # logger.debug("antes de vectorizarDB")
                for index, chunk in enumerate(embeding_chunk,1) :
                    vector=self._embedding_content(chunk)
                    if not vector or len(vector) != self.dimension:
                        logger.error("[ERROR -> embedding content extesion]")
                        return False
                    if not self.index and not self.initialize_conection():
                        logger.error("[ERROR -> sin index para pinecone]")
                        return False

                    menu_meta_data={
                        "content":chunk,
                        "line_number":index,
                        "dish_id":f"dish_id{index}",
                        "type":"menu_item",
                    }
                    unique_id=str(index)
                    batch.append((unique_id,vector,menu_meta_data))

                    #3.1. almancenar
                    # logger.info(f"inseccion de batch: {len(batch)} y batch: {batch_size})")
                    if len(batch) >= batch_size:
                        logger.info("inseccion de batch")
                        self.index.upsert(vectors=batch)
                        batch=[]

                if batch:
                    self.index.upsert(vectors=batch)
                logger.info(f"[INFO -> upset menu to pinecone]")
                return True

            else:
                return False

        except Exception as err:
            logger.error(f"[ERROR en upset_menu_data > al almacenar Vector DB] {err}")
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

        # 2. reg para validacion
        str_key_validation="No menu items encontrado"
        # 3. proceso de validacion
        return not str_key_validation in str_validation

    def _split_str(self,contetoToSplit:str)->list[str]:
        """
        splite str
        :return:
        """

        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=0,separators=["\n"],length_function=len)
            # texts = text_splitter.split_text(document)
            document_str=text_splitter.create_documents([contetoToSplit])
            list_str=[]
            for document in document_str:
                list_str.append(document.page_content.strip())

            return list_str
        except Exception as err:
            logger.error(f"[ERROR al split] {err}")
            return []

    def search_similar(self,query_todo:str,match_key:int=2)-> List[Dict[str,any]]:

        try:
            if not self.initialize_conection() and not self.index :
                logger.error("sin instancia de index")
                return []
            query_vector=self._embedding_content(query_todo)
            if not query_vector or len(query_vector) != self.dimension:
                logger.error("sin query_vector or sin dimension")
                return []
            # pinecone_query_result = self.index.search(query_vector)
            pinecone_query_result = self.index.query(
                vector=query_vector,
                top_k=match_key,
                include_metadata=True,
            )

            matches_result=pinecone_query_result["matches"]
            if not matches_result:
                return []

            out_result=[]
            for result in matches_result:
                match_item={
                    "id":result["id"],
                    "score":result["score"],
                    "content":result["metadata"]["content"],
                    "line_number":result["metadata"]["line_number"],
                }
                out_result.append(match_item)
                logger.debug(f"resultado mached con len: {len(out_result)}")
            return out_result

        except Exception as err:
            logger.error(f"[ERROR al search similar ] {err}")
            return []


pinecone_db=PineconeVectorDB()


# exponer fncion de consultar a PineconeDB
def pinecone_input(menu_data:str=None,clear_existed:bool=True)->bool:
    return  pinecone_db.upset_menu_data(menu_data,clear_existed=clear_existed)

# exponer funcion de consulta a LocalDB
def search_menu_items(query:str,match_key:int=2 )->List[str]:

    result_similar =pinecone_db.search_similar(query,match_key=match_key)

    if not result_similar:
        return []

    return [ result["content"] for result in result_similar]


def search_menu_items_ids(query:str,match_key:int=2 )->Dict[str, Any]:
    """
                    "id":result["id"],
                    "score":result["score"],
                    "content":result["metadata"]["content"],
                    "line_number":result["metadata"]["line_number"],
    :param query:
    :param match_key:
    :return:
    """

    result_similar =pinecone_db.search_similar(query,match_key=match_key)

    if not result_similar:
        return {}

    ids=[]
    for result in result_similar:
        content = result["content"]

        re_result = re.match(r"dish_id:(\d+)",content)

        if re_result:
            id_re=int(re_result.group(1))
        else:
            id_re=result["id"]
        ids.append(id_re)


    return {
        "contents":[result["content"] for result in result_similar],
        "ids":ids,
        "scores":[result["score"] for result in result_similar],
    }


if __name__ == '__main__':
    # pinecone_db.initialize_conection()
#     pinecone_db.upset_menu_data(menu_data=None,batch_size=30,clear_existed=True)
#
    # print("busqueda vectorial")
    # similar_result = pinecone_db.search_similar(query_todo="quiero que me recomendes 川菜")
    # for result in similar_result:
    #     print(result)

    print("consular de busqueda similar")
    result_search = search_menu_items_ids(query="quiero que me recomendes 川菜",match_key=2)
    print(result_search)


