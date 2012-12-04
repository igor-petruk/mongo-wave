from gi.repository import Gtk, Gio, Gdk
from pymongo import MongoClient

from mongowave.utils import *

class ConnectDialog:
    def __init__(self):
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

    def host(self):
        return self.hostname_entry.get_text()

    def port(self):
        return int(self.port_entry.get_text())

    def on_refresh(self,widget):
        connection = MongoClient(self.host(),self.port())
        self.dbcombobox_store.clear()
        dbnames = connection.database_names()
        for db in dbnames:
            self.dbcombobox_store.append([db])
        if len(dbnames)!=0:
            self.dbcombobox.set_active(0)
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

