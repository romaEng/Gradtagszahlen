import requests

class CrudHandler():
    def __init__(self, base_url):
        self.base_url = base_url
        self.headers = {'Content-Type': 'application/json'}

    def get(self, endpoint):
        response = requests.get(f"{self.base_url}/{endpoint}", headers=self.headers)
        return response.json()

    def post(self, endpoint, data):
        response = requests.post(f"{self.base_url}/{endpoint}", json=data, headers=self.headers)
        return response.json()

    def put(self, endpoint, data):
        response = requests.put(f"{self.base_url}/{endpoint}", json=data, headers=self.headers)
        return response.json()

    def delete(self, endpoint):
        response = requests.delete(f"{self.base_url}/{endpoint}", headers=self.headers)
        return response.status_code
    
    def patch(self, endpoint, data):
        response = requests.patch(f"{self.base_url}/{endpoint}", json=data, headers=self.headers)
        return response.json()
    
    def head(self, endpoint):
        response = requests.head(f"{self.base_url}/{endpoint}", headers=self.headers)
        return response.headers
    
