from bottle import Bottle


app = Bottle()

@app.route('/')
def index():
    return 'Hello from Bottle'

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)