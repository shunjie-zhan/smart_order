"""
invocar api de mapa, de la cual obtiene la distancia de reparto y
planificacion de la trayectoria

"""
import logging
from http.client import responses

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import os
from typing import Dict, Any, List, Optional, Tuple
import requests
from urllib3 import Retry
from requests.adapters import HTTPAdapter
import json
from dotenv import load_dotenv

load_dotenv()


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


def geocode_adress(address) -> Dict[str, Any]:
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
            "status": True,
            "messege": geocodes["location"],
            "formatted_address": geocodes["formatted_address"],
        }

    except Exception as err:
        logging.error(f"Error en Geo request: {err}")
        raise f"Error en Geo request{err}"


if __name__ == '__main__':
    print(geocode_adress(address="武汉大学"))
