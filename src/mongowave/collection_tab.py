from gi.repository import Gtk, Gio, Gdk, GtkSource
from mongowave.utils import *
from pymongo import MongoClient

class CollectionTab:
    def __init__(self, collection_name):
        self.collection_name = collection_name
        builder = Gtk.Builder()
        self.builder = builder
        builder.add_from_file(determine_path()+'/data/collection_tab.glade')
        self.control = builder.get_object('collection_tab')
        self.query_scroll = builder.get_object('query_scroll')

        source_buffer = GtkSource.Buffer()
        source_buffer.set_language(GtkSource.LanguageManager.get_default().get_language("json"))

        source_view = GtkSource.View()
        source_view.set_auto_indent(True)
        source_view.set_buffer(source_buffer)

        self.query_scroll.add(source_view)
        self.source_view = source_view
        source_view.show_all()

    def tab_control(self):
        return self.control