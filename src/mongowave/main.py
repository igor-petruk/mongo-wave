from gi.repository import Gtk, Gdk
from pymongo import MongoClient

from mongowave.utils import *
from mongowave.connect_dialog import *
from mongowave.input_dialog import InputDialog
from mongowave.collection_tab import CollectionTab
from mongowave.configuration import ConfigurationManager

class MainWindow:
    def __init__(self):
        self.config = ConfigurationManager()
        self.builder = Gtk.Builder()
        self.uifile = determine_path()+'/data/main.glade'
        self.builder.add_from_file(self.uifile)
        self.window = self.builder.get_object('main_window')
        self.window.connect("delete-event", self.on_quit)
        self.db = None
        self.connection = None
        self.selected_collection = None
        self.collection_tabs = {}

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
        self.collections_view.connect("row_activated",self.on_collections_row_activated)
        cv_selection = self.collections_view.get_selection()
        cv_selection.connect("changed",self.on_collections_view_selection_changed)
        self.connect_dialog = ConnectDialog(self.config)

        self.collections_notebook = self.builder.get_object('collections_notebook')

        self.window.show_all()

    def on_quit(self,w,e):
        self.config.save()
        Gtk.main_quit(w,e)

    def on_collections_row_activated(self,widget,path,column):
        selected_collection = self.collections_view_store[path][0]
        if selected_collection not in self.collection_tabs:
            collection_tab = CollectionTab(self.db[selected_collection])
            page = collection_tab.tab_control()

            label_box = Gtk.Box(spacing=3)
            label_box.set_orientation(Gtk.Orientation.HORIZONTAL)

            label = Gtk.Label()
            label.set_text(selected_collection)
            label_box.pack_start(label,True,True,0)

            close_image = Gtk.Image()
            close_image.set_from_stock(Gtk.STOCK_CLOSE,Gtk.IconSize.SMALL_TOOLBAR)
            close_button = Gtk.Button()
            close_button.set_image(close_image)
            close_button.set_relief(Gtk.ReliefStyle.NONE)
            close_button.connect("clicked",self.on_collections_tab_close_button_click, selected_collection)
            label_box.pack_start(close_button,True,True,0)

            label_box.show_all()

            page_index = self.collections_notebook.append_page(page,label_box)
            page.show_all()
            self.collections_notebook.set_current_page(page_index)
            self.collection_tabs[selected_collection] = page_index
        else:
            self.collections_notebook.set_current_page(self.collection_tabs[selected_collection])

    def on_collections_tab_close_button_click(self,widget,tab_name):
        self.remove_tab_named(tab_name)

    def remove_tab_named(self, name):
        if name in self.collection_tabs:
            index_to_remove = self.collection_tabs[name]
            self.collections_notebook.remove_page(index_to_remove)
            for tab in self.collection_tabs:
                index = self.collection_tabs[tab]
                if index>index_to_remove:
                    self.collection_tabs[tab] = index-1
            del self.collection_tabs[name]
        self.refresh_collections_view()

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
        self.remove_tab_named(self.selected_collection)

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
