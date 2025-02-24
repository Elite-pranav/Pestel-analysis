import requests

api_key = "4b3b2436cb6b4e92a8839364fdc34ac7"
url = "https://api.bing.microsoft.com/v7.0/search?q=Tesla"

headers = {"Ocp-Apim-Subscription-Key": api_key}

response = requests.get(url, headers=headers)
print(response.status_code, response.json())
