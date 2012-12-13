from gi.repository import Gtk, Gdk, GtkSource, GObject
from mongowave.utils import *
from pymongo import MongoClient

from bson.json_util import loads

from functools import *

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

        collection_view.set_hover_expand(False)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Key", renderer, text=0)
        collection_view.append_column(column)

        renderer = Gtk.CellRendererText()
        renderer.set_property("editable",True)
        renderer.connect("edited",self.on_item_text_edited)
        column = Gtk.TreeViewColumn("Value", renderer, text=1)
        collection_view.append_column(column)

    def on_item_text_edited(self, widget, path, text):
        all_path_indicies = Gtk.TreePath(path).get_indices()
        value_iter = self.store.get_iter(Gtk.TreePath(path))
        iter = self.store.get_iter(Gtk.TreePath(str(all_path_indicies[0])))
        mongo_object = self.store.get_value(iter,2)
        string_path = []
        current_path = []
        for index in all_path_indicies:
            current_path += [str(index)]
            current_iter = self.store.get_iter(Gtk.TreePath(":".join(current_path)))
            if current_iter is not None:
                value = self.store.get_value(current_iter,0)
                string_path+=[value]
        update_key = ".".join(string_path[1:]);
        update_spec = {"_id":mongo_object["_id"]}
        update_doc = {"$set":{update_key:text}}
        self.store.set_value(value_iter,1, text)
        self.collection.update(update_spec,update_doc)

    def populate_iter(self, store, iter, object):
        if isinstance(object, dict):
            for item in object:
                representation = ""
                if not isinstance(object[item],dict):
                    print(item+": "+str(type(object[item])))
                    representation = str(object[item])
                new_iter = store.append(iter, [item,representation,None])
                self.populate_iter(store, new_iter, object[item])

    def run_query(self, widget):
        sb = self.source_buffer
        json_text = sb.get_text(sb.get_start_iter(),sb.get_end_iter(),True)
        json_obj = loads(json_text)
        collection = self.collection.find(json_obj)
        self.store = store = Gtk.TreeStore(str,str,object)
        top_iter = store.get_iter_first()
        for item in collection:
            id = item["_id"]
            iter = store.append(top_iter, [str(id),"",item])
            self.populate_iter(store, iter, item)
        self.collection_view.set_model(store)


    def tab_control(self):
        return self.control

