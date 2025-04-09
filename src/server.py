import os
import pyaudio
import wave
import requests
import speech_recognition as sr
import io
import urllib.parse

# API configuration
WAKE_WORD = "lilo"
ASSETS_PATH = "assets/"
BASE_URL = "http://192.168.1.101:3000"
SPEECH_TO_SPEECH_API = f"{BASE_URL}/api/speech-to-speech/generate?key=gadingnst&format="

SAMPLE_RATE = 48000  # Use 48000 Hz sample rate

def log_ai_headers(response):
  """Display AI-Text-Request and AI-Text-Response headers if available"""
  request_text = response.headers.get("AI-Text-Request", "N/A")
  response_text = response.headers.get("AI-Text-Response", "N/A")

  # Decode URI if the header is not empty
  request_text = urllib.parse.unquote(request_text) if request_text != "N/A" else "N/A"
  response_text = urllib.parse.unquote(response_text) if response_text != "N/A" else "N/A"

  # Only log if the text is not "N/A"
  print("\n🧾 Response Headers:")
  print(f"---\n📥 AI-Text-Request:\n'{request_text}'\n")
  print(f"📤 AI-Text-Response:\n'{response_text}'\n---\n")

def play_local_audio(filename):
  """Play an MP3 audio file from the assets folder"""
  path = ASSETS_PATH + filename
  with open(path, "rb") as f:
    play_audio(f.read())

def record_dynamic_audio():
  """Record voice using 48000 Hz"""
  recognizer = sr.Recognizer()
  mic = sr.Microphone(sample_rate=SAMPLE_RATE)  # Ensure 48000 Hz is used

  print("🎤 Recording... Speak now!")
  with mic as source:
    recognizer.adjust_for_ambient_noise(source)
    try:
      audio = recognizer.listen(source, timeout=10, phrase_time_limit=3)
    except sr.WaitTimeoutError:
      print("⏳ No response detected, returning to standby mode...")
      return None

  # Save into a WAV buffer
  wav_buffer = io.BytesIO()
  with wave.open(wav_buffer, "wb") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)  # 16-bit PCM
    wf.setframerate(SAMPLE_RATE)  # Ensure 48000 Hz
    wf.writeframes(audio.frame_data)

  return wav_buffer.getvalue()

def send_audio_to_api(audio_data):
  """Send WAV audio to API and receive MP3 response"""
  print("✈️  Sending recorded audio...")
  headers = {"content-type": "audio/wav"}
  response = requests.post(SPEECH_TO_SPEECH_API, headers=headers, data=audio_data)

  if response.status_code == 200:
    print("📩 Received response audio!")
    log_ai_headers(response)  # Log AI headers
    return response.content  # Return MP3 audio from API
  else:
    print("❌ Error:", response.status_code, response.text)
    return None

def play_audio(audio_data):
  """Play MP3 audio using mpg123"""
  print("🔊 Playing response audio...")
  with open("temp_audio.mp3", "wb") as f:
    f.write(audio_data)
  os.system("mpg123 -q temp_audio.mp3")
  print("✅ Audio playback completed!\n\n")

def listen_mode():
  """Enter listen mode and stay until no voice is detected"""
  while True:
    audio_data = record_dynamic_audio()
    if audio_data:
      response_audio = send_audio_to_api(audio_data)
      if response_audio:
        play_audio(response_audio)
    else:
      print("🔕 No more response, returning to standby mode...\n\n\n\n")
      break  # Exit listen mode if no voice detected

def wake_word_detection():
  recognizer = sr.Recognizer()
  try:
    mic = sr.Microphone()
  except Exception as e:
    print(f"❌ Error initializing microphone: {e}")
    return

  try:
    with mic as source:
      recognizer.adjust_for_ambient_noise(source)
      print("🎤 Say something to calibrate the microphone (e.g. 'Test')...")
      audio = recognizer.listen(source)
  except Exception as e:
    print(f"❌ Error during listening: {e}")

  print(f"🤖 Say '{WAKE_WORD}' to wake up the assistant.")
  while True:
    with mic as source:
      try:
        print("🎧 Listening for wake word...")
        audio = recognizer.listen(source)
        text = recognizer.recognize_google(audio).lower()
        print(f"🦻 Heard: {text}")

        if WAKE_WORD in text:
          print(f"\n🚀 Wake word '{WAKE_WORD}' detected in: '{text}'")
          
          # Play sound when wake word is detected
          play_local_audio("wake-up.mp3")
          
          # Enter listen mode after the first response
          listen_mode()
          print("🔁 Returning to standby mode...")
        else:
          print("❌ Skipping, because it's not a wake word\n")
          play_local_audio("skip.mp3")
          print(f"🤖 Say '{WAKE_WORD}' to wake up the assistant.")
          pass

      except sr.UnknownValueError:
        print("No wake word detected\n")
      except sr.RequestError:
        print("Speech recognition service unavailable\n")

if __name__ == "__main__":
  wake_word_detection()
