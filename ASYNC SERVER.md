Включаем async сервер
````
daphne myproject.asgi:application
```` 

Сихронизация БД
````
python manage.py migrate --run-syncdb 
```` 
