# app/routes.py

from flask import Blueprint, request, jsonify, current_app
import cloudinary.uploader, re

from app.audio_craft import generate_music_from_text_craft
from app.audio_gen import generate_music_from_text
from flask_cors import CORS, cross_origin

bp = Blueprint('main', __name__)
CORS(bp, resources={r"/*": {"origins": "*", "methods": "*", "allow_headers": "*"}})


@bp.route('/generate/MUSIC_GEN', methods=['POST'])
@cross_origin()
def generate():
    data = request.get_json()
    text = data.get('prompts')

    token_len = request.args.get('token_len', default=5, type=int)
    model_name = current_app.config['AUDIOGEN_MODEL']

    model = request.args.get('model_name', default=model_name, type=str)

    if not text:
        return jsonify({'error': 'Text input is required'}), 400

    # Generate music from text
    audio_file_path = generate_music_from_text(text, token_len, model)
    upload_results = []
    for i, text in enumerate(audio_file_path):
        # Upload the generated music to Cloudinary
        upload_result = cloudinary.uploader.upload(text['path'], resource_type="video", public_id=text['name'])
        upload_results.append(upload_result['secure_url'])

    return jsonify({'urls': upload_results})


@bp.route('/generate/AUDIO_CRAFT', methods=['POST'])
@cross_origin()
def generate_audio_craft():
    data = request.get_json()
    text = data.get('prompts')

    duration = request.args.get('duration', default=10, type=int)
    model_name = current_app.config['AUDIOCRAFT_MODEL']

    model = request.args.get('model_name', default=model_name, type=str)

    if not text:
        return jsonify({'error': 'Text input is required'}), 400

    # Generate music from text
    audio_file_path = generate_music_from_text_craft(text, duration, model)
    upload_results = []
    index = 0
    for i, text in enumerate(audio_file_path):
        # Upload the generated music to Cloudinary
        print(f'text:{text} i:{i},, idx:{index}')
        f_name = sanitize_filename(text[index])
        upload_result = cloudinary.uploader.upload(text['path'], resource_type="video", public_id=f_name)
        upload_results.append(upload_result['secure_url'])
        index += 1

    return jsonify({'urls': upload_results})


def sanitize_filename(text):
    # Remove non-alphanumeric characters and replace spaces with underscores
    return re.sub(r'[^a-zA-Z0-9]', '_', text)
