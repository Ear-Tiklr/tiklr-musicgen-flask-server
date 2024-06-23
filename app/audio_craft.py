from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write
import re
from flask import current_app
import scipy


def generate_music_from_text_craft(text_input, duration, model_name):
    model = MusicGen.get_pretrained(model_name)
    model.set_generation_params(duration=duration)  # generate 8 seconds.

    directory = current_app.config['TEMP_DIR']

    wav = model.generate(text_input)  # generates 2 samples.
    audio_files = []

    for idx, one_wav in enumerate(wav):
        sanitized_filename = sanitize_filename(text_input[idx])
        output_path = f"{directory}{sanitized_filename}"
        audio_write(f'{output_path}', one_wav.cpu(), model.sample_rate, strategy="loudness")
        print(f'Saved: {output_path}')
        audio_files.append({"name": sanitized_filename, "path": f'{output_path}.wav'})

    return audio_files


def sanitize_filename(text):
    # Remove non-alphanumeric characters and replace spaces with underscores
    return re.sub(r'[^a-zA-Z0-9]', '_', text)
