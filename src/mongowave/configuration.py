from configparser import *
import os
import json
import uuid

class ConfigLocation:
    @staticmethod
    def CONFIG_FILE():
        return os.path.expanduser("~/.mongowave")

class ClientConnection:
    def __init__(self):
        self.id = uuid.uuid4()
        self.name=""
        self.host="localhost"
        self.port=27017
        self.db=""
        self.user=""

class ConfigurationManager:
    def __init__(self):
        self.connections = []
        self.active_connection = None
        self.load()

    def load(self):
        config = ConfigParser()
        config.read(ConfigLocation.CONFIG_FILE())
        if config.has_section("Connections"):
            connections = json.loads(config.get("Connections","list"))
            active = config.get("Connections","active")

            for section in connections:
                connection = ClientConnection()
                if section==active:
                    self.active_connection = connection
                connection.id = uuid.UUID(section)
                connection.name = config.get(section,"name")
                connection.host = config.get(section,"host")
                connection.port = int(config.get(section,"port"))
                connection.db = config.get(section,"db")
                connection.user = config.get(section,"user")
                self.connections.append(connection)

    def save(self):
        config = ConfigParser()
        config.add_section('Connections')
        conn_ids=[]
        for conn in self.connections:
            section = str(conn.id)
            conn_ids.append(section)
            config.add_section(section)
            config.set(section,"name",conn.name)
            config.set(section,"host",conn.host)
            config.set(section,"port",str(conn.port))
            config.set(section,"db",conn.db)
            config.set(section,"user",conn.user)

        config.set('Connections',"list",json.dumps(conn_ids))
        if self.active_connection is not None:
            config.set('Connections',"active",str(self.active_connection.id))
        else:
            config.set('Connections',"active","")

        with open(ConfigLocation.CONFIG_FILE(), 'wt', encoding='utf8') as configfile:
            config.write(configfile)
