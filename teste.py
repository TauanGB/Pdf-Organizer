import requests
import json

url = "https://www.sintegraws.com.br/api/v1/execute-api.php"

querystring = {"token":"XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX","cnpj":" 35962585000105","plugin":"RF"}

response = requests.request("GET", url, params=querystring)

nome = json.loads(response.text).get('nome')

print(nome)