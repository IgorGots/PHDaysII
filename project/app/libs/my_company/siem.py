import os

SIEM_HOST = 'siem.mycompany.net'
SIEM_PORT = 1111

SIEM_USER = os.getenv("SIEM_USER")
SIEM_PASS = os.getenv("SIEM_PASS")


class SiemSearch():
    def __init__(self, client_config, query):
        pass


def siem_query(query):
    siem_config = {
        "username": SIEM_USER,
        "password": SIEM_PASS,
        "host": SIEM_HOST,
        "port": SIEM_PORT,
        "autologin": True
    }

    siem_search = SiemSearch(client_config=siem_config, query=query)

    return siem_search.result
