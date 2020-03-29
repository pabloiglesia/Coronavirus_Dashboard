# Dashboard del Coronavirus en tiempo real

En este repositorio puedes encontrar todo lo necesario para crear un dashboard del coronavirus en timepo resl. Este dashboard se puede ver en http://webbuildeer.com:8050/, pero también puedes crear tu propia versión a partir de este código.

Para ejecutarlo solo debes clonar el proyecto, instalar python y pipenv, y ejecutar los siguientes comandos
  
         pipenv install
         pipenv run gunicorn coronavirus:server -b :8050
