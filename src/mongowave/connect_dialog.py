from gi.repository import Gtk, Gdk
from pymongo import MongoClient

from mongowave.utils import *

class ConnectDialog:
    def __init__(self, config):
        self.init_complete = False
        self.config = config
        self.builder = Gtk.Builder()
        self.uifile = determine_path()+'/data/connect.glade'
        self.builder.add_from_file(self.uifile)
        self.connect_dialog = self.builder.get_object('connect_dialog')
        self.dbcombobox = self.builder.get_object('dbcombobox')
        self.dbcombobox_store = self.builder.get_object('dbcombobox-store')
        self.hostname_entry = self.builder.get_object('hostname')
        self.port_entry = self.builder.get_object('port')
        self.refreshdb = self.builder.get_object('refreshdb')
        self.refreshdb.connect("clicked",self.on_refresh)
        self.connection_combobox = self.builder.get_object('connection_combobox')
        self.connection_combobox.connect("changed", self.on_name_combo_changed)
        self.load_connection_store(config)

    def on_name_combo_changed(self,combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            connection = self.connection_store[tree_iter][1]
            self.active_db = connection.db
            self.hostname_entry.set_text(connection.host)
            self.port_entry.set_text(str(connection.port))
            self.on_refresh(None)
            if self.init_complete:
                self.config.active_connection = connection
            else:
                self.init_complete = True

    def load_connection_store(self,config):
        self.connection_store = Gtk.ListStore(str,object)
        self.connection_combobox.set_entry_text_column(0)

        active_index = 0
        index = 0
        for connection in config.connections:
            if connection.id==config.active_connection.id:
                active_index = index
            else:
                index += 1
            self.connection_store.append([connection.name,connection])

        self.connection_combobox.set_model(self.connection_store)
        self.connection_combobox.set_active(active_index)

    def host(self):
        return self.hostname_entry.get_text()

    def port(self):
        return int(self.port_entry.get_text())

    def on_refresh(self,widget):
        connection = MongoClient(self.host(),self.port())
        self.dbcombobox_store.clear()
        dbnames = connection.database_names()
        index = 0
        active = 0
        for db in dbnames:
            if db == self.active_db:
                active = index
            else:
                index += 1
            self.dbcombobox_store.append([db])
        if len(dbnames)!=0:
            self.dbcombobox.set_active(active)
        connection.close()

    def database(self):
        tree_iter = self.dbcombobox.get_active_iter()
        if tree_iter != None:
            model = self.dbcombobox.get_model()
            return model[tree_iter][0]
        else:
            None

    def run(self):
        result = self.connect_dialog.run()
        self.connect_dialog.hide()
        return result

