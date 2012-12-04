from gi.repository import Gtk, Gio, Gdk

from mongowave.utils import *;

class InputDialog:
    def __init__(self,caption,message,default=""):
        self.builder = Gtk.Builder()
        self.uifile = determine_path()+'/data/input_dialog.glade'
        self.builder.add_from_file(self.uifile)
        self.input_dialog = self.builder.get_object('input_dialog')
        self.input_dialog.set_title(caption)
        self.message_label = self.builder.get_object('message_label')
        self.message_label.set_text(message)
        self.text_entry = self.builder.get_object('text_entry')
        self.text_entry.set_text(default)

    def run(self):
        result = self.input_dialog.run()
        self.input_dialog.hide()
        if result==0:
            return self.text_entry.get_text()
        else:
            return None

