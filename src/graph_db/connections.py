import os
from neo4j import GraphDatabase, Driver
from dotenv import load_dotenv


class GraphDBConnection:
    _driver: Driver | None = None

    def __init__(self):
        raise RuntimeError("Call get_driver() instead")

    @classmethod
    def get_driver(cls) -> Driver:
        if cls._driver is None:
            load_dotenv()
            uri = os.getenv("NEO4J_URI")
            user = os.getenv("NEO4J_USERNAME")
            password = os.getenv("NEO4J_PASSWORD")

            if not all([uri, user, password]):
                raise ValueError(
                    "NEO4J_URI, NEO4J_USERNAME, and NEO4J_PASSWORD must be set in .env file"
                )

            cls._driver = GraphDatabase.driver(uri, auth=(user, password))
        return cls._driver

    @classmethod
    def close_driver(cls):
        if cls._driver is not None:
            cls._driver.close()
            cls._driver = None
