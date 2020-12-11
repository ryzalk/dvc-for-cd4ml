import os
import pathlib
import flask
import tensorflow as tf


APP = flask.Flask(__name__)


def load_model(model_file_repath='./models/text-classification-model'):
    """Loads trained model for inferencing to be done.

    Parameters
    ----------
    model_file_repath : str, optional
        Relative path of saved model, by default './models/text-classification-model'

    Returns
    -------
    model : tf.keras.Model
        Loaded trained model.
    """
    curr_path = pathlib.Path().absolute()
    model_file_abs_path = curr_path / model_file_repath
    loaded_model = tf.keras.models.load_model(model_file_abs_path)
    return loaded_model


MODEL = load_model()


@APP.route('/predict', methods=["POST"])
def predict():
    """Flask resource for:
    - receiving request with text input
    - respond with binary sentiment (positive/negative)

    Returns
    -------
    res_output : flask.response object
        Response object with the application/json mimetype.
    """

    if flask.request.method == "POST":

        req_input = flask.request.json
        model_prediction = MODEL.predict([req_input['text']])

        if model_prediction > 0.5:
            sentiment = 'positive'
        else:
            sentiment = 'negative'

        res_output = flask.jsonify({'sentiment': sentiment})

    return res_output


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 80))
    APP.run(host='0.0.0.0', port=port)
