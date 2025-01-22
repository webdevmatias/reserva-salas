from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# URL dos serviços de destino
AUTH_SERVICE_URL = 'http://auth-service:3001'
USER_SERVICE_URL = 'http://user-service:3002'

"""
    Redireciona a requisição para o serviço de destino
"""
def proxy_request(service_url, path):
    # Faz a requisição para o serviço de destino
    resp = requests.request(
        method=request.method,
        url=f"{service_url}/{path}",
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False)
    
    # Remove os headers que não devem ser enviados ao cliente
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]

    # Retorna a resposta para o cliente com os headers corretos
    response = jsonify(resp.json())
    response.status_code = resp.status_code
    for header in headers:
        response.headers[header[0]] = header[1]
    return response

@app.route('/api/users/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def users_proxy(path):
    return proxy_request(USER_SERVICE_URL, path)

@app.route('/api/auth/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def auth_proxy(path):
    return proxy_request(AUTH_SERVICE_URL, path)

@app.route('/', methods=['GET'])
def index():
    return jsonify({'message': 'API Gateway'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
