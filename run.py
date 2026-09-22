"""
iniciar el servidor uvicorn
"""
import uvicorn
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """"
    instancia el servidor uvicorn
    """
    try:
        logger.info('Iniciando el servidor')
        uvicorn.run("api.main:app", port=8000, log_level="info")
    except Exception as err:
        # logger.exception('Faltando el servidor')
        print('Faltando el servidor')

if __name__ == '__main__':
    main()
