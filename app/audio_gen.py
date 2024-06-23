# app/audio_gen.py

import subprocess
import math

import torch
from transformers import AutoProcessor, MusicgenForConditionalGeneration
import scipy
import re

import os
import glob

# def generate_music_from_text(text):
#     # Load the Audiogen model from config
#     model_name = current_app.config['AUDIOGEN_MODEL']
#     model = audiogen.load_model(model_name)
#
#     # Generate audio from text
#     audio = model.generate(text)
#
#     # Save the generated audio to a file
#     output_path = 'output.wav'
#     audiogen.save_wav(audio, output_path)
#
#     return output_path


from flask import current_app


def sanitize_filename(text):
    # Remove non-alphanumeric characters and replace spaces with underscores
    return re.sub(r'[^a-zA-Z0-9]', '_', text)


def delete_files_in_directory(directory):
    files = glob.glob(os.path.join(directory, '*'))
    for file in files:
        try:
            os.remove(file)
            print(f"Deleted: {file}")
        except Exception as e:
            print(f"Failed to delete {file}. Reason: {e}")


def generate_music_from_text(text_input, token_len, model_name):
    directory = current_app.config['TEMP_DIR']

    processor = AutoProcessor.from_pretrained(model_name)
    model = MusicgenForConditionalGeneration.from_pretrained(model_name)

    # Move model to GPU if available
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    print(f'{text_input}')

    inputs = processor(
        text=text_input,
        padding=True,
        return_tensors="pt",
    )

    # Move inputs to GPU if available
    inputs = {k: v.to(device) for k, v in inputs.items()}
    print(f'{inputs}')

    # Generate audio on GPU with fine-tuning parameters
    # audio_values = model.generate(
    #     **inputs,
    #     max_new_tokens=512,  # Adjust to control length; start with a high value for longer audio
    #     do_sample=True,  # Use sampling
    #     temperature=0.7,  # Temperature for sampling
    #     top_k=50,  # Top-k filtering
    #     top_p=0.95,  # Top-p (nucleus) filtering
    #     repetition_penalty=1.2  # Repetition penalty
    # )

    audio_values = model.generate(**inputs, max_new_tokens=token_len, do_sample=True)

    # Move output back to CPU for saving
    audio_values = audio_values.cpu()

    sampling_rate = model.config.audio_encoder.sampling_rate
    delete_files_in_directory(directory)
    output_paths = []
    for i, text in enumerate(text_input):
        sanitized_filename = sanitize_filename(text)
        output_path = f"{directory}{sanitized_filename}.wav"
        scipy.io.wavfile.write(output_path, rate=sampling_rate, data=audio_values[i, 0].numpy())
        print(f'Saved: {output_path}')
        output_paths.append({"name": sanitized_filename, "path": output_path})

    return output_paths


def duration_to_token_len(duration_sec):
    """
    Converts duration in seconds to token length based on the established relationship.

    Args:
    duration_sec (int or float): Duration in seconds

    Returns:
    int: Corresponding token length
    """
    # Example relationship: 512 tokens correspond to 5 seconds
    tokens_per_sec = 512 / 5
    n = int(duration_sec * tokens_per_sec)
    return 2 ** round(math.log2(n))