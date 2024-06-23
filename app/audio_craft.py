from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write

from flask import current_app


def generate_music_from_text_craft(text_input, duration, model_name):
    model = MusicGen.get_pretrained("large")
    model.set_generation_params(duration=duration)  # generate 8 seconds.

    descriptions = ["happy rock", "energetic EDM"]
    directory = current_app.config['TEMP_DIR']

    wav = model.generate(descriptions)  # generates 2 samples.
    audio_files = []

    for idx, one_wav in enumerate(wav):
        # Will save under {idx}.wav, with loudness normalization at -14 db LUFS.
        file_name = f"{directory}/{idx}.wav"
        audio_write(f'{file_name}', one_wav.cpu(), model.sample_rate, strategy="loudness")
        audio_files.append(file_name)

    return audio_files
