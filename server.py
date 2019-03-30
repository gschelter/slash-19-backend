from flask import Flask, request, jsonify, abort
from requests.exceptions import MissingSchema

from podcasts import find_podcast_by_website

PORT = 80

app = Flask(__name__)


@app.route('/podcast-by-website')
def flask_podcast_by_website():
    try:
        url = request.args.get('url')

        return jsonify(find_podcast_by_website(url))
    except MissingSchema as e:
        abort(422, str(e))


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=PORT)
