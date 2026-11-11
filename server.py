import os
from flask import Flask, send_from_directory, request

app = Flask(__name__, static_folder='.')

# Ruta principal: Abre la consola de DJ
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# Ruta de seguridad: Permite que el servidor responda a cualquier opción o botón de la página
@app.route('/<path:path>')
def catch_all(path):
    if os.path.exists(os.path.join('.', path)):
        return send_from_directory('.', path)
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    # Configuración del puerto oficial para Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
