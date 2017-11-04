from flask import Flask, jsonify, abort, request, make_response, url_for, render_template
from apiestas.arbs import ArbsFinder

app = Flask(__name__, static_url_path="")


def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)
    # return 403 instead of 401 to prevent browsers from displaying the default auth dialog


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/', methods=['GET'])
def render_arbs_page():
    return render_template('arbs.html')


@app.route('/', methods=['POST'])
def get_arbs():
    arbs = ArbsFinder().find_arbs()
    return jsonify(arbs)

if __name__ == '__main__':
    app.run(debug=True)