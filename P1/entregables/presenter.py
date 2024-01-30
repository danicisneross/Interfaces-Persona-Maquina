
from model import Model
from view import View, run
import requests
import threading

class Presenter:

    def __init__(self, model: Model, view: View):
        self.model = model
        self.view = view
        self.search_in_progress = False
        self.mutex = threading.Lock()
    
    def run(self, application_id: str):
        self.view.set_handler(self)
        run(application_id=application_id, on_activate=self.view.on_activate)
    
    def __on_search_cocktail_by_name_clicked__(self, entry: str) -> None:
        self.mutex.acquire()
        if not self.search_in_progress:
            self.search_in_progress = True
            self.mutex.release()
            if not entry.isspace() and entry != "":
                try:
                    self.view.start_spinner_left()
                    result = self.model.search_cocktail_by_name(entry)
                except requests.exceptions.ConnectionError:
                    ##codigo que ejecuta la pantalla de error
                    error = self.view.connection_error_build_view()
                    self.view.stop_spinner_left()
                    self.view.left_window_err(error)
                except (requests.exceptions.HTTPError, requests.exceptions.Timeout):  
                    error = self.view.server_error_build_view()
                    self.view.stop_spinner_left() 
                    self.view.left_window_err(error)
                else:
                    if result != []:        
                        self.view.create_first_page(result)
                    else:
                        error = self.view.not_found_error_build_view()
                        self.view.left_window_err(error)
                    self.view.stop_spinner_left()
                    
                self.view.set_es_label_visible(False)
            else:
                #Mostrar Pantalla de busqueda vacia 
                self.view.set_es_label_text("empty_search_field")
                self.view.set_es_label_visible(True)       
            self.mutex.acquire()
            self.search_in_progress = False 
            self.mutex.release()
        else:
            self.mutex.release()
            self.view.set_es_label_text("search_in_progress")
            self.view.set_es_label_visible(True) 


    def __on_search_cocktail_by_ingredient_clicked__(self, ingredientName: str) -> None:
        self.mutex.acquire()
        if not self.search_in_progress:
            self.search_in_progress = True
            self.mutex.release()
            if not ingredientName.isspace() and ingredientName != "":
                try:
                    self.view.start_spinner_left()
                    result = self.model.search_cocktail_by_ingredient(ingredientName)
                except requests.exceptions.ConnectionError:
                    ##codigo que ejecuta la pantalla de error
                    error = self.view.connection_error_build_view()
                    #self.view.stop_spinner_left()
                    self.view.left_window_err(error)
                    
                except (requests.exceptions.HTTPError, requests.exceptions.Timeout):  
                    error = self.view.server_error_build_view()
                    #self.view.stop_spinner_left()   
                    self.view.left_window_err(error)  
                else:
                    if result != []:
                        self.view.create_first_page(result)
                    else :
                        error = self.view.not_found_error_build_view()
                        self.view.left_window_err(error)
                    

                self.view.set_es_label_visible(False)    
            else:
                #Mostrar Pantalla de busqueda vacia 
                self.view.set_es_label_text("empty_search_field")
                self.view.set_es_label_visible(True)         
            self.mutex.acquire()
            self.search_in_progress = False 
            self.mutex.release()
            self.view.stop_spinner_left()
            
        else:
            self.mutex.release()
            self.view.set_es_label_text("search_in_progress")
            self.view.set_es_label_visible(True)

    def get_missing_fields(self, cocktailId: str)  -> list:
        try:   
            return self.model.search_cocktails_by_id(cocktailId)
        except requests.exceptions.ConnectionError:
            ##codigo que ejecuta la pantalla de error
            error = self.view.connection_error_build_view()
            self.view.right_window_err(error)
        except (requests.exceptions.HTTPError, requests.exceptions.Timeout):  
            error = self.view.server_error_build_view()
            self.view.left_window_err(error)     

    def get_image(self, url: str): 
          return self.model.get_image(url)
    
    def on_search_cocktail_by_name_clicked_multithread(self, entry: str) -> None:
        thread = threading.Thread(target = self.__on_search_cocktail_by_name_clicked__, args=(entry,))
        thread.daemon = True
        thread.start()
      
    def on_search_cocktail_by_ingredient_clicked_multithread(self, ingredientName: str) -> None:
        thread = threading.Thread(target = self.__on_search_cocktail_by_ingredient_clicked__, args=(ingredientName,))
        thread.daemon = True
        thread.start()

    def __next_page_multithread__(self) -> None:
        self.mutex.acquire()
        if not self.search_in_progress:
            self.search_in_progress = True
            self.mutex.release()
            self.view.next_page()
            self.mutex.acquire()
            self.search_in_progress = False 
            self.mutex.release()
            self.view.set_es_label_visible(False)
            
        else: 
            self.mutex.release()
            self.view.set_es_label_text("search_in_progress")
            self.view.set_es_label_visible(True)

    def __prev_page_multithread__(self) -> None:
        self.mutex.acquire()
        if not self.search_in_progress:
            self.search_in_progress = True
            self.mutex.release()
            self.view.prev_page()
            self.mutex.acquire()
            self.search_in_progress = False 
            self.mutex.release()
            self.view.set_es_label_visible(False)
        else:
            self.mutex.release()
            self.view.set_es_label_text("search_in_progress")
            self.view.set_es_label_visible(True)
            
        
    def __update_cocktail_multithread__(self, list_object) -> None:
        thread = threading.Thread(target = self.view.update_cocktail, args = (list_object,))
        thread.daemon = True
        thread.start()
        
    def next_page_multithread(self) -> None:
        thread = threading.Thread(target = self.__next_page_multithread__)
        thread.daemon = True
        thread.start()

    def prev_page_multithread(self) -> None:
        thread = threading.Thread(target = self.__prev_page_multithread__)
        thread.daemon = True
        thread.start()
        
    def update_cocktail_multithread(self, list_object) -> None:
        thread = threading.Thread(target = self.__update_cocktail_multithread__, args=(list_object,))
        thread.daemon = True
        thread.start()
        
                