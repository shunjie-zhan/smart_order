"""
invocar api de mapa, de la cual obtiene la distancia de reparto y
planificacion de la trayectoria

"""
import logging
from http.client import responses

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import os
from typing import Dict, Any, List, Optional, Tuple, Literal, Union
import requests
from urllib3 import Retry
from requests.adapters import HTTPAdapter
import json
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

pathInput = Literal["1", "2", "3"]
pathModel = Literal["walking", "bike", "driving"]


class PathConverter:
    MODE_MAPPING = {
        "1": "walking",
        "2": "bicycling",
        "3": "driving"
    }

    @classmethod
    def to_mode(cls, path_input: Union[pathInput]) -> pathModel:
        if path_input in cls.MODE_MAPPING:
            return cls.MODE_MAPPING[path_input]
        else:
            raise ValueError(f"invalid path_input:{path_input}")


@dataclass  # asignar valor de forma rapido
class AmpConfig:
    AMAP_API_KEY: str = os.getenv("AMAP_API_KEY")
    MERCHANT_LONGITUDE: str = os.getenv("MERCHANT_LONGITUDE")
    MERCHANT_LATITUDE: str = os.getenv("MERCHANT_LATITUDE")
    DELIVERY_RADIUS: int = int(os.getenv("DELIVERY_RADIUS"))
    DEFAULT_PATH_MODE: str = os.getenv("DEFAULT_PATH_MODE")

    def __post_init__(self):
        if self.AMAP_API_KEY is None:
            raise ValueError("AMAP_API_KEY sin valor")


config = AmpConfig()


def remake_request():
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)

    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session


def base_request(url_base: str, param: dict) -> Optional[Dict]:
    session = remake_request()
    try:
        # 1. remake session
        response = session.get(url=url_base, params=param, timeout=10)
        response.raise_for_status()

        return response.json()
    except requests.exceptions.SSLError as err:
        try:
            # 2. cambiar a http request
            logging.error(f"Error en https request: {err}")
            url_base.replace('https://', 'http://')
            response = session.get(url=url_base, params=param, timeout=10)
            return response.json()
        except requests.exceptions.RequestException as err:
            logging.error(f"Error en request: {err}")
            raise f"Error en request{err}"

    # 3.error de over time
    except requests.exceptions.RequestException as err:
        raise f"Error en request{err}"

    # 4.error en Json
    except json.decoder.JSONDecodeError as err:
        raise f"Error en Json{err}"


def geocode_address(address) -> Dict[str, Any]:
    # 1. url de solicitud : https://restapi.amap.com/v3/geocode/geo?parameters
    try:
        requests_url = "https://restapi.amap.com/v3/geocode/geo"

        # 2. parametro de solicitud
        params = {
            'address': address,
            "key": os.environ.get("AMAP_API_KEY"),
        }
        # 3. send
        response = base_request(requests_url, params)

        # 4. result
        if response["status"] != "1":
            return {
                "status": False,
                "messege": response["info"]
            }
        geocodes = response["geocodes"][0]

        return {
            "formatted_address": geocodes["formatted_address"],
            "location": geocodes["location"],
            "success": True
        }

    except Exception as err:
        logging.error(f"Error en Geo request: {err}")
        raise f"Error en Geo request{err}"


def calculate_distance(first_point: str, second_point: str, param: pathInput or None) -> Dict[str, Any]:
    """
    https://restapi.amap.com/v5/direction/driving?parameters
    https://restapi.amap.com/v5/direction/walking?parameters
    :param first_point:
    :param second_point:
    :param param: show_fields
    :return:
    """
    try:
        # 1. check api_key
        if config.AMAP_API_KEY is None:
            raise ValueError("AMAP_API_KEY sin valor")
        # 2.url de solicitud

        result_mode = PathConverter.to_mode(param)

        path_requets = {
            "walking": "https://restapi.amap.com/v5/direction/walking",
            "bicycling": "https://restapi.amap.com/v5/direction/bicycling",
            "driving": "https://restapi.amap.com/v5/direction/driving"
        }
        # 3. construir parametro
        parametro = {
            "key": config.AMAP_API_KEY,
            "origin": first_point,
            "destination": second_point,
        }

        if result_mode == "driving":
            parametro["show_fields"] = "cost"

        # 4.enviar requests
        response = base_request(path_requets[result_mode], parametro)

        if response["status"] != "1":
            return {
                "success": False,
                "message": response["info"],
            }

        path = response["route"]["paths"][0]
        duration = path["duration"] if result_mode == "bicycling" else path["cost"]["duration"]
        # 5. procesar dato
        return {
            "distance": int(path["distance"]),
            "duration": duration,
            "status": "success",
        }

    except Exception as err:
        raise f"Error en envio de request:{err}"

def check_range(address: str, param: pathInput = None) -> Dict[str, Any]:
    """

    :param address:  cambiar direccion introducido
    :param param: escoger modo
    comprobar distancia introducido (geo) con objetivo (geo)
    :return:
    """
    try:
        geo_address = geocode_address(address)

        if geo_address["status"]:
            return {
                "status": "fail",
                "messege": geo_address["message"],
            }
        objective = f"{config.MERCHANT_LATITUDE}, {config.MERCHANT_LONGITUDE}"
        result_distance = calculate_distance(first_point=objective, second_point=geo_address["location"], param=param or config.DEFAULT_PATH_MODE)

        if not result_distance["success"]:
            return {
                "status": "fail",
                "messege": result_distance["message"],
            }
        distance = result_distance["distance"] /1000
        in_range = result_distance["distance"] <= config.MERCHANT_LATITUDE
        return {
            "status": "success",
            "in_range": in_range,
            "distance": distance,
            "duration": result_distance["duration"],
            "formatted_distance": geo_address["formatted_address"],
            "message": (
                f"Direccion de reparto: {geo_address["formatted_address"]} \n"
                f"Distancia de reparto: {distance} \n "
                f"Estado de reparto: {'En area' if in_range else 'Fuera area'} "
            )

        }
    except Exception as err:
        logging.error(f"Error en calcular distancia de reparto:{err}")
        raise  err


if __name__ == '__main__':
    # print(geocode_adress(address="北京市昌平区宏福科技园(郑平路")) #116.365533,40.102488
    # print(geocode_adress(address="北京市昌平区温都水城(快速公交站)")) #116.372850,40.106030

    print(calculate_distance(first_point="116.365533,40.102488", second_point="116.372850,40.106030"))
