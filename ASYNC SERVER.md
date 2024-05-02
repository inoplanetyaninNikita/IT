Включаем async сервер
````
daphne myproject.asgi:application
```` 

Сихрон
````
python manage.py migrate --run-syncdb 
```` 
