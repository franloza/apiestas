from eve import Eve


def run(port=5000):
    app = Eve()
    app.run(debug=True, host="0.0.0.0", port=port)

