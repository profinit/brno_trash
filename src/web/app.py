from flask import Flask, render_template, request

app = Flask(__name__)
LAT, LONG = 49.1951, 16.6068

@app.route('/', methods=['GET'])
def index():
    context = {
        "coords": [LAT, LONG]
    }
    return render_template('template.html', map=map, context=context)


@app.route('/click', methods=['POST'])
def click():
    context = {
        "coords": [LAT, LONG]
    }

    jsdata = request.form
    print(jsdata)
    return render_template('template.html', map=map, context=context)


if __name__ == '__main__':
    app.run()
