import requests
import urllib 

from herramientas import *


class Model:
    def __init__(self):
        pass
    #Función para buscar cocktails por nombre.
    def search_cocktail_by_name(self, c_name: str) -> list:
        url_string = "http://www.thecocktaildb.com/api/json/v1/1/search.php?s=" + c_name

        request = requests.get(url_string, timeout=2)
        request.raise_for_status()  
        cocktail_list = []
        #Si la cadena c_name es espacio vacío o no tiene nada devolvemos lista vacía
        if not c_name.isspace() and c_name != "":
            cocktail_list = json_to_cocktail_list(request.json())
        return cocktail_list
    
    #Función para buscar un cocktail específico por un id
    def search_cocktails_by_id(self, id: str) -> list:
        url_string = "https://www.thecocktaildb.com/api/json/v1/1/lookup.php?i=" + id
        request = requests.get(url_string, timeout=2)
        request.raise_for_status()
        dic = request.json()["drinks"][0]
        return [join_ingredients_measure(dic), formating_text(dic["strInstructions"]), dic["strGlass"]]

    #MODIFICAR ESTA FUNCION PARA QUE FUNCIONE PARECIDO A SEARCH COCKTAIL
    #Función para buscar cocktails por un ingrediente en su composición 
    def search_cocktail_by_ingredient(self, ingredient: str) -> list:
        url_string = "https://www.thecocktaildb.com/api/json/v1/1/filter.php?i=" + ingredient
        request = requests.get(url_string, timeout=2)
        request.raise_for_status()
        cocktail_list = []
        try:
            jsonF = request.json()
        except:
            return cocktail_list
        else:
            cocktail_list = json_to_cocktail_list(jsonF)
            return cocktail_list

    def get_image(self, url:str):
        response = urllib.request.urlopen(url) #Hacemos la peticion de la imagen
        input_stream = Gio.MemoryInputStream.new_from_data(response.read(), None) #Convertimos la imagen en un imput stream
        #Hay que hacer gestion de errores
        return input_stream