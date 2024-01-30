
from model import Model
from view import View
from presenter import Presenter
from pathlib import Path

import locale
import gettext


if __name__ == "__main__":

    # Primero vamos a inicalizar el soporte de traducciones.

    # El primer paso es configurar el módulo `locale` con el locale de
    # la usuaria.
    # En windows esta configuración no se hace con las variables de entorno.
    locale.setlocale(locale.LC_ALL, '')

    # Establecemos las BBDD de traducciones. En gettext se llaman _dominios_.
    # Primero calculamos el directorio donde se encuentran.
    # En un FHS sería `/usr/share/locale`, ...

    LOCALE_DIR = Path(__file__).parent / "locale"
    # Relacionamos el nombre de las BBDD y el directorio donde buscar.
    # Las BBDD se llaman igual para todos los idiomas, sólo cambia el
    # directorio donde están.
    locale.bindtextdomain('App', LOCALE_DIR)
    gettext.bindtextdomain('App', LOCALE_DIR)
    # Configuramos el nombre de la BD de traducciones a usar
    gettext.textdomain('App')

    presenter = Presenter(model=Model(), view=View())
    presenter.run(application_id="es.udc.fic.ipm.CocktailApp") 
