import requests
from gi.repository import Gio
import urllib 
import textwrap

#Funcion que le pasamos un json de la petición y devuelve una lista de cocktails con
#los campos que nos interesan.
def json_to_cocktail_list(jsonF: dict):
    cocktail_dict_list = jsonF["drinks"] #Nos quedamos con la lista de cocktails que son diccionarios
    cocktail_list = []
    #Comprobamos que hay algo en el diccionario mas externo jsonF
    if cocktail_dict_list != None:
        for i in cocktail_dict_list: 
            #Nos quedamos con los campos que nos interesan y los metemos en un diccionario
            cocktail_dic = dict(name = i["strDrink"], 
                                instructions = formating_text(i["strInstructions"]) if "strInstructions" in i else None, #Formateamos el string de instrucciones
                                ingredients= join_ingredients_measure(i) if "strIngredient1" in i else None, #Unimos los ingredientes con sus respectivas cantidades
                                glass = i["strGlass"]if "strGlass" in i else None,
                                url = i["strDrinkThumb"],
                                cocktailId = i["idDrink"])
            cocktail_list.append(cocktail_dic)   
    return cocktail_list    

#Función para unir los ingredientes a sus respectivas medidasy devolverlos todos en un solo string formateado
def join_ingredients_measure(cocktail_dict: dict):
    ingredient_list = []
    i = 1
    #Los campos de los ingredientes es del tipo "strIngredient<numero>" y el de las medidas "strMeasure<numero>"
    #ambos comienzan en 1
    while(cocktail_dict["strIngredient"+str(i)] != None): #Recorremos hasta que nos encontremos un campo ingrdiente vacio
        ing_mea_str: str = cocktail_dict["strIngredient"+str(i)]
        if (cocktail_dict["strMeasure"+str(i)] != None): #Verificamos si un ingrediente tiene una medida y la unimos a su ingrediente
                ing_mea_str = cocktail_dict["strMeasure"+str(i)] +" "+ ing_mea_str
        ingredient_list.append(ing_mea_str)
        i+=1
    ingredient_str = '\n'.join(ingredient_list)
    return ingredient_str

def formating_text(text: str): 
    #Especificamos el ancho maximo de cada linea 
    tight_lines = textwrap.wrap(text, width=55)        

    #Convertimos la lista de lienas en un solo string con saltos de linea
    formatted_text = "\n".join(tight_lines)
   
    return formatted_text
