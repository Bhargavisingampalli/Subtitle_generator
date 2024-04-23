from flask import Flask, render_template, request, redirect, url_for, send_file
import os
import shutil
import moviepy.editor as mp
import speech_recognition as sr
import requests
import json

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'wav', 'mp3', 'pcm'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_audio(video_path, audio_path):
    video = mp.VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)

def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        return "Speech recognition could not understand the audio"
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"

def translate_text(text, source_language, target_language):
    api_url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl={}&tl={}&dt=t&q={}".format(source_language, target_language, text)
    response = requests.get(api_url)
    translation = json.loads(response.text)
    translated_text = translation[0][0][0]
    return translated_text

@app.route('/')
def upload_form():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        file_extension = os.path.splitext(filename)[1].lower()
        if file_extension in {".mp4", ".avi", ".mov"}:
            audio_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_audio.wav')
            extract_audio(file_path, audio_path)
            print("Audio extracted successfully.")
            transcribed_text = transcribe_audio(audio_path)
            print("Audio transcribed successfully.")
            os.remove(audio_path)
        elif file_extension in {".wav", ".mp3", ".pcm"}:
            audio_path = file_path
            transcribed_text = transcribe_audio(audio_path)
            print("Audio transcribed successfully.")
        else:
            shutil.rmtree(app.config['UPLOAD_FOLDER'])
            return "Unsupported file format."

        if transcribed_text:
            target_language = request.form.get('target_language')
            translated_text = translate_text(transcribed_text, 'en', target_language)
            print("Text translated successfully.")

            translated_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'translated_text.txt')
            with open(translated_file_path, "w", encoding="utf-8") as f:
                f.write(translated_text)
            print("Transcribed and translated text saved successfully.")
            print(translated_text)

            return render_template('result.html', translated_text=translated_text)
        else:
            shutil.rmtree(app.config['UPLOAD_FOLDER'])
            return "No transcribed text to translate."
    else:
        return "File format not allowed."

@app.route('/download')
def download_file():
    translated_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'translated_text.txt')
    return send_file(translated_file_path, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)