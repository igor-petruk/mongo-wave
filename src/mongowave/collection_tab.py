from gi.repository import Gtk, Gdk, GtkSource
from mongowave.utils import *
from pymongo import MongoClient

from bson.json_util import loads

class CollectionTab:
    def __init__(self, collection):
        self.collection = collection
        builder = Gtk.Builder()
        self.builder = builder
        builder.add_from_file(determine_path()+'/data/collection_tab.glade')
        self.control = builder.get_object('collection_tab')
        self.query_scroll = builder.get_object('query_scroll')

        run_query_button = builder.get_object('run_query')
        run_query_button.connect("clicked",self.run_query)

        source_buffer = GtkSource.Buffer()
        source_buffer.set_text("{\n\t\n}")
        source_buffer.set_language(GtkSource.LanguageManager.get_default().get_language("js"))
        self.source_buffer = source_buffer

        source_view = GtkSource.View()
        source_view.set_auto_indent(True)
        source_view.set_buffer(source_buffer)

        self.query_scroll.add(source_view)
        self.source_view = source_view
        source_view.show_all()

        self.collection_view = collection_view = builder.get_object("collection_view")

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Key", renderer, text=0)
        collection_view.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Value", renderer, text=1)
        collection_view.append_column(column)

    def populate_iter(self, store, iter, object):
        if isinstance(object, dict):
            for item in object:
                representation = ""
                if not isinstance(object[item],dict):
                    representation = str(object[item])
                new_iter = store.append(iter, [item,representation])
                self.populate_iter(store, new_iter, object[item])

    def run_query(self, widget):
        sb = self.source_buffer
        json_text = sb.get_text(sb.get_start_iter(),sb.get_end_iter(),True)
        json_obj = loads(json_text)
        collection = self.collection.find(json_obj)
        self.store = store = Gtk.TreeStore(str,str)
        top_iter = store.get_iter_first()
        for item in collection:
            id = item["_id"]
            iter = store.append(top_iter, [str(id),""])
            self.populate_iter(store, iter, item)
        self.collection_view.set_model(store)


    def tab_control(self):
        return self.control

