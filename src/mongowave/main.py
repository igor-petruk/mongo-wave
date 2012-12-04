from gi.repository import Gtk, Gio, Gdk
from pymongo import MongoClient

from mongowave.utils import *
from mongowave.connect_dialog import *
from mongowave.input_dialog import InputDialog

class MainWindow:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.uifile = determine_path()+'/data/main.glade'
        self.builder.add_from_file(self.uifile)
        self.window = self.builder.get_object('main_window')
        self.window.connect("delete-event", Gtk.main_quit)
        self.db = None
        self.connection = None
        self.selected_collection = None

        self.connect_menu_item = self.builder.get_object('connect_menu_item')
        self.connect_menu_item.connect("activate", self.on_connect_menu_item_click)

        self.disconnect_menu_item = self.builder.get_object('disconnect_menu_item')
        self.disconnect_menu_item.connect("activate", self.on_disconnect_menu_item_click)

        self.add_collection = self.builder.get_object('add_collection')
        self.add_collection.connect("clicked",self.on_add_collections_view)

        self.remove_collection = self.builder.get_object('remove_collection')
        self.remove_collection.connect("clicked",self.on_remove_collections_view)

        self.refresh_collections = self.builder.get_object('refresh_collections')
        self.refresh_collections.connect("clicked",self.on_refresh_collections_view)

        self.collections_view_store = self.builder.get_object('collections_view_store')
        self.collections_view = self.builder.get_object('collections_view')
        cv_selection = self.collections_view.get_selection()
        cv_selection.connect("changed",self.on_collections_view_selection_changed)
        self.connect_dialog = ConnectDialog()

        self.window.show_all()

    def on_collections_view_selection_changed(self,selection):
        model, treeiter = selection.get_selected()
        self.remove_collection.set_sensitive(treeiter is not None)
        if treeiter is not None:
            self.selected_collection = model[treeiter][0]
        else:
            self.selected_collection = None

    def on_add_collections_view(self,widget):
        collection = InputDialog("New collection","Please, enter new collection name","new_collection").run()
        if collection is not None:
            self.db.create_collection(collection)
            self.refresh_collections_view()
        self

    def on_remove_collections_view(self,widget):
        self.db[self.selected_collection].drop()
        self.refresh_collections_view()

    def on_refresh_collections_view(self,widget):
        self.refresh_collections_view()

    def refresh_collections_view(self):
        self.collections_view_store.clear()
        if self.db is not None:
            collnames = self.db.collection_names()
            for collection in collnames:
                icon = "gtk-dnd-multiple"
                if collection.startswith("system."):
                    icon = "gtk-preferences"
                self.collections_view_store.append([collection,icon])

    def activate_db_buttons(self,active):
        self.add_collection.set_sensitive(active)
        self.remove_collection.set_sensitive(active and (self.selected_collection is not None))
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

def run():
    window = MainWindow()
    Gtk.main()

if __name__ == '__main__':
    run()