#!/usr/bin/python

from gi.repository import Gtk, Gio, Gdk
from pymongo import MongoClient

class ConnectDialog:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.uifile = 'connect.glade'
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

class MainWindow:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.uifile = 'main.glade'
        self.builder.add_from_file(self.uifile)
        self.window = self.builder.get_object('main_window')
        self.window.connect("delete-event", Gtk.main_quit)
        self.db = None
        self.connection = None

        self.connect_menu_item = self.builder.get_object('connect_menu_item')
        self.connect_menu_item.connect("activate", self.on_connect_menu_item_click)

        self.disconnect_menu_item = self.builder.get_object('disconnect_menu_item')
        self.disconnect_menu_item.connect("activate", self.on_disconnect_menu_item_click)

        self.add_collection = self.builder.get_object('add_collection')
        self.remove_collection = self.builder.get_object('remove_collection')
        self.refresh_collections = self.builder.get_object('refresh_collections')
        self.refresh_collections.connect("clicked",self.on_refresh_collections_view)

        self.collections_view_store = self.builder.get_object('collections_view_store')
        self.connect_dialog = ConnectDialog()

        self.window.show_all()

    def on_refresh_collections_view(self,widget):
        self.refresh_collections_view()

    def refresh_collections_view(self):
        self.collections_view_store.clear()
        if self.db is not None:
            collnames = self.db.collection_names()
            for collection in collnames:
                self.collections_view_store.append([collection])

    def activate_db_buttons(self,active):
        self.add_collection.set_sensitive(active)
        self.remove_collection.set_sensitive(active)
        self.refresh_collections.set_sensitive(active)
        self.disconnect_menu_item.set_sensitive(active)

    def set_db(self,connection,db):
        if self.connection is not None:
            self.connection.close()
        self.connection = connection
        self.db = db;
        self.activate_db_buttons(db!=None)
        self.refresh_collections_view()

    def on_disconnect_menu_item_click(self,action_group):
        self.set_db(None,None)

    def on_connect_menu_item_click(self,action_group):
        if self.connect_dialog.run()==1:
            connection = MongoClient(self.connect_dialog.host(),self.connect_dialog.port())
            db = connection[self.connect_dialog.database()]
            self.set_db(connection,db)
        else:
            self.set_db(None,None)

if __name__ == '__main__':
    window = MainWindow()
    Gtk.main()