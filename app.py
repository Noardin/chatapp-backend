from appthings.inicializApp import *
from flask_cors import CORS

app = inicialize()
CORS(app, resources={r'/*': {"origins": "http://localhost:8080"}})

if __name__ == '__main__':
        socketio.run(app, debug=True, port=1000)
