# kitoboy-pie

Сервис детекции персональных данных в тексте.

# Запуск сервера

```bash
$ fastapi run app/main.py --port 8001
```

# Тестовый запрос

```bash
$ curl -X POST http://localhost:8001/v2/models/pie/infer -H "Content-Type: application/json" -d '{"inputs":[{"name":"text_input","shape":[3,1],"datatype":"BYTES","data":["+79099444970", "скиньте деньги на поесть 1111 1111 1111 1111 имя Никита", "помогите мне"]}]}'
```