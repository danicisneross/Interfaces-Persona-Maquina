from __future__ import annotations
import time
from herramientas import *
from typing import Callable, Protocol

import locale
import gettext

import gi
import os
import math

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('GdkPixbuf', '2.0')

from gi.repository.GdkPixbuf import Pixbuf

from gi.repository import Gtk, Gio, GObject, GLib

_ = gettext.gettext

def run(application_id: str, on_activate: Callable) -> None:
    app = Gtk.Application(application_id=application_id)
    app.connect('activate', on_activate)
    app.run()

class ViewHandler(Protocol):
    def on_search_cocktail_by_name_clicked_multithread(self, entry: str) -> None: pass
    def on_search_cocktail_by_ingredient_clicked_multithread (self, id: str) -> None: pass
    def get_missing_fields(self, cocktailId: str)  -> list: pass
    def get_image(self, url: str): pass
    def next_page_multithread(self) -> None: pass
    def prev_page_multithread(self) -> None: pass
    def update_cocktail_multithread(self, object) -> None: pass

class CocktailObject(GObject.GObject):
    def __init__(self, name, instructions, ingredients, glass, url, cocktailId):
        super().__init__()
        self._name = name
        self._instructions = instructions
        self._ingredients = ingredients
        self._glass = glass
        self._thumb = None
        self._image_url = url
        self._cocktailId = cocktailId
    
    @GObject.Property(type=str)
    def name(self):
        return self._name

    @GObject.Property(type=str)
    def instructions(self):
        return self._instructions 
    
    @GObject.Property(type=str)
    def ingredients(self):
        return self._ingredients 
    
    @GObject.Property(type=str)
    def glass(self):
        return self._glass 
    
    @GObject.Property
    def thumb(self):
        return self._thumb
    
    def thumb_setter(self, value):
        self._thumb = value

    @GObject.Property
    def image_url(self):
        return self._image_url
    
    @GObject.Property
    def cocktailId(self):
        return self._cocktailId
    
    def __repr__(self):
        return f"ExampleObjectG(name={self._name}, instructions={self._instructions}, ingredients={self._ingredients}, glass={self._glass}, thumb={self._thumb}, cocktailId={self._cocktailId})"
    
class View:
    def __init__(self):
        
        self.handler = None
        self.data_model_cocktail = Gio.ListStore(item_type=CocktailObject)
        self.pivot_list = Gio.ListStore(item_type=CocktailObject)
        self.page = 0
        

    def set_handler(self, handler: ViewHandler) -> None:
        self.handler = handler
                
    def on_activate(self, app: Gtk.Application) -> None:
        self.build(app)

    def build(self, app: Gtk.Application) -> None:



        #------------------------------- Creación de los elementos principales de la vista -----------------------------
        #------------------------------------- win, header, box principal y listview  -----------------------------

        self.window = win = Gtk.ApplicationWindow(title=_("Cocktails' App"))
        app.add_window(win)
        win.connect("destroy", lambda win: win.close())

        #Añadimos una cabecera a la ventana principal
        header = Gtk.HeaderBar()
        win.set_titlebar(header)

        #Creamos la lista de cócteles que nos aparecerá en la parte izquierda
        self.cocktail_listview = self.build_listview(self.on_listview_cocktail_selection_changed, self.pivot_list)
    
        
        
        #Creamos la box principal de nuestra ventana, que contendrá todos los widgets
        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12,
            margin_top=12,
            margin_bottom=12,
            margin_start=12,
            margin_end=12)
        #Cambiamos tamaño de la ventana
        win.set_default_size(width = 1080, height = 900)
        #Mostramos la ventana
        win.present()


        #------------------------------- Creación de la barra buscadora de cocktails -----------------------------

        es_grid = Gtk.Grid(halign = Gtk.Align.CENTER, row_spacing = 3)

        self.search_entry = Gtk.SearchEntry(halign = Gtk.Align.CENTER)
        self.entry_text = ""

        #Establece el ancho y alto
        self.search_entry.set_size_request(410,40) 
    
        #Conectamos la función de cambio de contenido en la barra de búsqueda
        self.search_entry.connect(
            'search-changed',lambda _wg: self.on_search_entry_changed())
        
        self.es_label = Gtk.Label()
        self.es_label.set_visible(False)

        es_grid.attach(self.search_entry, 0, 0, 1, 1)
        es_grid.attach(self.es_label, 0, 1, 1, 1)
        
        #Añadimos la barra de búsqueda a la box principal     
        box.append(es_grid)

        
        #------------------------------- Creación de botones de "buscar por nombre" y "buscar por ingredeinte"  -----------------------------
               
        search_by_name = Gtk.Button(label=_("SEARCH BY NAME"))
        search_by_name.set_size_request(200,40) #Establece el ancho y alto
        search_by_ingredient = Gtk.Button(label=_("SEARCH BY INGREDIENT"))
        search_by_ingredient.set_size_request(200,40) #Establece el ancho y alto

        grid = Gtk.Grid(halign = Gtk.Align.CENTER)

        grid.attach(search_by_name, 0, 0, 1, 1)
        grid.attach(search_by_ingredient, 1, 0, 1, 1)
        box.append(grid)

        grid.set_column_spacing(10)

        #Conectamos los botones a las funciones de clickado
        search_by_name.connect(
            'clicked', lambda _wg: self.handler.on_search_cocktail_by_name_clicked_multithread(self.entry_text)
        )

        search_by_ingredient.connect(
            'clicked', lambda _wg: self.handler.on_search_cocktail_by_ingredient_clicked_multithread(self.entry_text)
        )
        

        #------------------------------- Creación de la ScrollWindow de listado de cocktails -----------------------------

        #Creamos la box horizontal que contendrá las dos ScrollWindows (una al lado de otra)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        
        #Creamos la scrolledWindow de listado de cocktails
        self.scrolledWindow_list = Gtk.ScrolledWindow(vexpand = True)
        self.scrolledWindow_list.set_child(self.cocktail_listview)
        #Numero de cocktails a mostrar en el listviwew
        self.N = 10 
        #Creación de botón next
        self.next = Gtk.Button()
        #Creación de botón prev
        self.prev = Gtk.Button()
        #Para que no aparezcan al iniciar la app
        self.next.set_visible(False)
        self.prev.set_visible(False)

        left_arrow_icon = Gtk.Image.new_from_file(os.path.abspath("images/left_arrow.png"))
        right_arrow_icon = Gtk.Image.new_from_file(os.path.abspath("images/right_arrow.png"))

        self.next.set_child(right_arrow_icon)
        self.prev.set_child(left_arrow_icon)
        #Creación del grid de los botones
        button_grid = Gtk.Grid(halign = Gtk.Align.CENTER)
        button_grid.attach(self.prev, 0, 0, 1, 1)
        button_grid.attach(self.next, 1, 0, 1, 1)

        button_grid.set_column_spacing(50)

        self.next.connect(
            'clicked', lambda _wg: self.handler.next_page_multithread()
        )

        self.prev.connect(
            'clicked', lambda _wg: self.handler.prev_page_multithread()
        )

        #Creando el spinner izquierdo
        self.spinner_left = Gtk.Spinner(margin_top = 400, hexpand = True)


        #Creamos la box que contendrá la scrollwindow y los botones
        scroll_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        scroll_box.append(self.scrolledWindow_list)
        scroll_box.append(self.spinner_left)
        scroll_box.append(button_grid)
        
        
        #Añadimos la scrolledWindow a la box horizontal 
        #Como es la primera en ser añadida, se coloca a la izquierda
        hbox.append(scroll_box)           

        #------------------------------- Creación de la ScrollWindow de información de cocktail -----------------------------

        self.scrolledWindow_cocktail = Gtk.ScrolledWindow()

        #Creamos las etiquetas "Cocktail", "Ingredients", "Instructions", "Glass"
        self.caption_cocktail_label = Gtk.Label(hexpand = True, halign=Gtk.Align.CENTER)
        self.caption_ingredients_label = Gtk.Label(halign=Gtk.Align.CENTER)
        self.caption_instructions_label = Gtk.Label(halign=Gtk.Align.CENTER)
        self.caption_glass_label = Gtk.Label(halign=Gtk.Align.CENTER)

        #Creamos las etiquetas que se van a ir rellenando según seleccionemos los cócteles
        self.ingredients_label = Gtk.Label(halign=Gtk.Align.CENTER,  justify = Gtk.Justification.CENTER)
        self.thumb_image = Gtk.Image(pixel_size = 350)
        self.instructions_label = Gtk.Label(halign=Gtk.Align.CENTER, justify = Gtk.Justification.CENTER)
        self.glass_label = Gtk.Label(halign=Gtk.Align.CENTER)
        
        #Aplicamos algunos formatos a las etiquetas
        self.caption_cocktail_label.add_css_class("title-1")
        self.caption_ingredients_label.add_css_class("heading")
        self.caption_instructions_label.add_css_class("heading")
        self.caption_glass_label.add_css_class("heading")

        #Creamos el box que llevará adjuntas las labels
        self.cocktail_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12,
            margin_top=6,
            margin_bottom=6,
            hexpand = True,
            vexpand = True,
            )

        self.cocktail_box.append(self.caption_cocktail_label)
        self.cocktail_box.append(self.thumb_image)
        self.cocktail_box.append(self.caption_ingredients_label)
        self.cocktail_box.append(self.ingredients_label)
        self.cocktail_box.append(self.caption_instructions_label)
        self.cocktail_box.append(self.instructions_label)
        self.cocktail_box.append(self.caption_glass_label)
        self.cocktail_box.append(self.glass_label)

        #Añadimos la box a la ScrollWindow de información del cóctel
        self.scrolledWindow_cocktail.set_child(self.cocktail_box)

        #Añadimos la scrollWindow a la box horizontal
        #Como es la segunda en ser añadida, se coloca a la deracha
        hbox.append(self.scrolledWindow_cocktail)
        
        #Añadimos la box horizontal a la box principal
        box.append(hbox)

        #Añadimos la box principal a la ventana
        win.set_child(box)

        #Aplicamos formato a la listview
        self.cocktail_listview.add_css_class("navigation-sidebar")

    
    #------------------------------- Creación de la Listview ---------------------------------

    def build_listview(self, selection_func, data_model) -> Gtk.ListView:
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self.on_listview_setup)
        factory.connect("bind", self.on_listview_bind)
        selection = Gtk.SingleSelection(model=data_model)

        selection.connect('selection-changed', selection_func)

        listview = Gtk.ListView(model=selection,
                                factory=factory,
                                hexpand=True,
                                vexpand=True)
        
        listview.set_size_request(100, 200)

        
        return listview
    

    def start_spinner_left(self):
        GLib.idle_add(self.next.set_visible, False)
        GLib.idle_add(self.prev.set_visible,False)
        GLib.idle_add(self.scrolledWindow_list.set_visible, False)
        GLib.idle_add(self.spinner_left.set_visible, True)
        GLib.idle_add(self.spinner_left.start)
       
    def stop_spinner_left(self):
       GLib.idle_add(self.spinner_left.stop)
       GLib.idle_add(self.spinner_left.set_visible, False)
       GLib.idle_add(self.scrolledWindow_list.set_visible, True)
       GLib.idle_add(self.next_prev_buttom_state)

    

    #Inicialización de la listview 

    def on_listview_setup(self, factory: Gtk.SignalListItemFactory, list_item: Gtk.ListItem) -> None:
        #Se crea una cuadrícula para meter el nombre y la foto del cocktail
        grid_List = Gtk.Grid()
        label = Gtk.Label(hexpand=True, halign=Gtk.Align.START)
        image = Gtk.Image(hexpand=True, halign=Gtk.Align.END, pixel_size = 100)
        grid_List.attach(label, 0, 0, 1, 1)
        grid_List.attach(image, 1, 0, 1, 1)
        #Cada elemento de la lista contendra una Gtk.Grid() como su contenido
        list_item.set_child(grid_List)
        
    
    #Vinculación de datos a un elemento en la list view 

    def on_listview_bind(self, factory: Gtk.SignalListItemFactory, list_item: Gtk.ListItem) -> None:
        #Obtenemos el grid
        widget = list_item.get_child()
        #Volvemos a obtener el label y la imagen (widget)
        widget1 = widget.get_first_child()
        widget2 = widget.get_last_child()
        #Se obtiene el objeto de datos asociado a ese elemento de la lista (CocktailObject)
        item = list_item.get_item()
        #Se obtiene el atributo name y la imagen de CocktailObject para mostrar en la lista
        widget1.set_text(item.name)
        widget2.set_from_pixbuf(item.thumb)
        
        
        

    #Función para cuando se selecciona un cocktail en la lista

    def on_listview_cocktail_selection_changed(self, model: Gtk.SelectionModel, position: int, n_items: int) -> None:
        selection = model.get_selection()
        idx = selection.get_nth(0)
        self.handler.update_cocktail_multithread(self.pivot_list[idx])


    #------------------------------- Actualización de la información en la ScrollWindow de cocktail ---------------------------------

    def update_cocktail(self, data: CocktailObject):
        GLib.idle_add(self.__update_cocktail__, data)
        
    def __update_cocktail__(self, data: CocktailObject) -> None:

        child = self.scrolledWindow_cocktail.get_child()
        if child != None: 
            child.unparent()
            self.scrolledWindow_cocktail.set_child(self.cocktail_box)
        #Si updateamos el cocktail desde la busqueda por ingredientes
        if data.ingredients == None:
            missing_fields = self.handler.get_missing_fields(data.cocktailId)
            #Si get_missing_fields devuelve None (da un error)
            if missing_fields != None:
                self.ingredients_label.set_text(missing_fields[0])
                self.instructions_label.set_text(missing_fields[1])
                self.glass_label.set_text(missing_fields[2])
        else:
            self.ingredients_label.set_text(data.ingredients)
            self.instructions_label.set_text(data.instructions)
            self.glass_label.set_text(data.glass)

        self.caption_cocktail_label.set_text(data.name)
        self.thumb_image.set_from_pixbuf(data.thumb)
       
       #Añadimos formato a las labels
        self.caption_ingredients_label.set_text(_("Ingredients"))
        self.caption_instructions_label.set_text(_("Instructions"))
        self.caption_glass_label.set_text(_("Glass"))


    def on_search_entry_changed(self):
        self.entry_text = self.search_entry.get_text()
     
    def update_cocktail_data_model(self, data: list) -> None:
        self.data_model_cocktail.remove_all()
        for item in data:   
            example_object = CocktailObject(item["name"], item["instructions"], item["ingredients"], item["glass"], item["url"], item["cocktailId"])
            self.data_model_cocktail.append(example_object)
      

    def load_images(self) -> None:
        start_index = (self.page - 1) * self.N
        data_model_cocktail_len = len(self.data_model_cocktail)
        final_page = int(math.ceil(data_model_cocktail_len / self.N)) 
        module = data_model_cocktail_len % self.N 

        if self.page == final_page and module != 0:
            end_index = (self.page-1) * self.N + module
        else:
            end_index = self.page * self.N 
            
        #Limpiamos toda la lista pivote (la que llevara la listview)
        GLib.idle_add(self.pivot_list.remove_all)
        for i in range(start_index, end_index):
            #Vamos cargando las imagenes en data model
            item: CocktailObject = self.data_model_cocktail[i]
            #El presenter devolvera un input stream (de la capa modelo)
            input_stream = self.handler.get_image(item.image_url)
            #Creamos el pixbuf y lo metemos en thumb
            pixbuf = Pixbuf.new_from_stream(input_stream, None)
            item.thumb_setter(pixbuf)
            GLib.idle_add(self.pivot_list.append, item)
        
            
        
    def create_first_page(self, data: list) -> None:
        GLib.idle_add(self.unparentear)
        self.page = 1
        if data != []:
            self.update_cocktail_data_model(data)
            self.load_images()
            GLib.idle_add(self.next_prev_buttom_state)
            GLib.idle_add(self.show_first_cocktail)

    
    def show_first_cocktail(self):
        self.__update_cocktail__(self.pivot_list[0])   
        
    def unparentear(self):
        child = self.scrolledWindow_list.get_child()
        if child != None : 
                child.unparent()
        self.scrolledWindow_list.set_child(self.cocktail_listview)        

    def next_page(self) -> None:
        self.start_spinner_left()
        #No comprobamos nada porque en la ultima pagina no hay boton next
        self.page += 1
        self.load_images()
        GLib.idle_add(self.next_prev_buttom_state)
        self.stop_spinner_left()
        self.show_first_cocktail()

    def prev_page(self) -> None:
        self.start_spinner_left()
        #No comprobamos nada porque en la primera pagina no hay boton prev
        self.page -= 1
        self.load_images()
        GLib.idle_add(self.next_prev_buttom_state)
        self.stop_spinner_left()
        self.show_first_cocktail()

    def next_prev_buttom_state(self):
            data_model_cocktail_len = len(self.data_model_cocktail)
            final_page = int(math.ceil(data_model_cocktail_len / self.N)) 

            #Primera pagina y sin mas datos en las siguientes
            if self.page == 0 or self.page == 1 and data_model_cocktail_len <= self.N: 
                self.next.set_visible(False)
                self.prev.set_visible(False)
            #Tenemos datos tanto en la siguiente pagina como en la anterior    
            elif self.page == 1:
                self.next.set_visible(True)
                self.prev.set_visible(False)
            #Estamos en la pagina final    
            elif self.page == final_page:
                self.next.set_visible(False)
                self.prev.set_visible(True)
            #Estamos en la primera pagina y hay mas info en la siguiente    
            elif self.page != final_page and data_model_cocktail_len > self.N:
                self.next.set_visible(True)
                self.prev.set_visible(True)
                 

    #------------------------------- Creación de error operación E/S en curso ---------------------------------
    

    #------------------------------- Creación de errores ---------------------------------

    def server_error_build_view(self) -> Gtk.Box:
        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            halign = Gtk.Align.CENTER,
            valign = Gtk.Align.CENTER,
            spacing = 20
        ) 

        image = Gtk.Image(hexpand=True, halign=Gtk.Align.CENTER, pixel_size = 200)
        image.set_from_file(os.path.abspath("images/serverdown.png"))
        title_err = Gtk.Label(label=_("SERVERS DOWN!"), hexpand = True, halign = Gtk.Align.CENTER)
        content_err = Gtk.Label(label = formating_text(_("The cocktail party on our server is temporarily paused!"
                                                       "Our team of party experts is working at full speed to bring the fun back.")),
                                                   hexpand = True, halign = Gtk.Align.CENTER, justify = Gtk.Justification.CENTER)
        
        title_err.add_css_class("title-1")
        content_err.add_css_class("title-2")

        box.append(image)
        box.append(title_err)
        box.append(content_err)
        return box
    
    def connection_error_build_view(self) -> Gtk.Box:
        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            halign = Gtk.Align.CENTER,
            valign = Gtk.Align.CENTER,
            spacing = 20
        )   
        image = Gtk.Image(hexpand=True, halign=Gtk.Align.CENTER, pixel_size = 200)
        image.set_from_file(os.path.abspath("images/connectionerror.png"))    
        title_err = Gtk.Label(label=_("NO INTERNET!"), hexpand = True, halign = Gtk.Align.CENTER)
        content_err = Gtk.Label(label = formating_text(_("Oops! We're mixing the signal, not the cocktails. Please connect to the Internet"
                                                       " to enjoy our wide selection of refreshing beverages.")),
                                                   hexpand = True, halign = Gtk.Align.CENTER, justify = Gtk.Justification.CENTER)
        
        title_err.add_css_class("title-1")
        content_err.add_css_class("title-2")

        box.append(image)
        box.append(title_err)
        box.append(content_err)
        return box
    
    def not_found_error_build_view(self) -> Gtk.Box:
        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            halign = Gtk.Align.CENTER,
            valign = Gtk.Align.CENTER,
            spacing = 20
        )   
        image = Gtk.Image(hexpand=True, halign=Gtk.Align.CENTER, pixel_size = 200)
        image.set_from_file(os.path.abspath("images/not_found.png"))    
        title_err = Gtk.Label(label=_("COCKTAIL NOT FOUND!"), hexpand = True, halign = Gtk.Align.CENTER)
        content_err = Gtk.Label(label = formating_text(_("Houston, we have a problem! This cocktail "
                                                       "is hiding quite well in our database. How about trying another one?")),
                                                   hexpand = True, halign = Gtk.Align.CENTER, justify = Gtk.Justification.CENTER)
        
        title_err.add_css_class("title-1")
        content_err.add_css_class("title-2")

        box.append(image)
        box.append(title_err)
        box.append(content_err)
        return box

    def left_window_err(self, new_child : Gtk.Box) -> None:
        GLib.idle_add(self.__left_window_err__, new_child)


    def __left_window_err__(self, new_child : Gtk.Box) -> None:
        self.page = 0
        child = self.scrolledWindow_list.get_child()
        if child != None : 
            child.unparent()
        self.scrolledWindow_list.set_child(new_child)
        self.next.set_visible(False)
        self.prev.set_visible(False)

    def right_window_err(self, new_child : Gtk.Box) -> None:
        GLib.idle_add(self.__right_window_err__, new_child)
    

    def __right_window_err__(self, new_child : Gtk.Box) -> None:
        self.page = 0
        child = self.scrolledWindow_cocktail.get_child()
        if child != None : 
            child.unparent()
        self.scrolledWindow_cocktail.set_child(new_child)
        self.next.set_visible(False)
        self.prev.set_visible(False)

    def set_es_label_visible (self, visibility : bool) -> None:
        self.es_label.set_visible(visibility)
    
    def set_es_label_text (self, err_type : str) -> None:
        if err_type == "search_in_progress" :
            self.es_label.set_text(_("Search in progress... Try again when this message disappears"))
        elif err_type == "empty_search_field" :
            self.es_label.set_text(_("Empty search field, type something to search!"))
