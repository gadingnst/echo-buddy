import os
import pyaudio
import wave
import requests
import io
import urllib.parse
import webrtcvad
import collections
import time
import struct
import math
import speech_recognition as sr

# API configuration
WAKE_WORD = "lilo"
ASSETS_PATH = "assets/"
BASE_URL = "http://192.168.1.103:3000"
SPEECH_TO_SPEECH_API = f"{BASE_URL}/api/speech-to-speech/generate?key=gadingnst&format="

# Audio configuration
SAMPLE_RATE = 48000 # Sample rate for audio recording (allowed values: 8000, 16000, 32000, 48000)
FRAME_DURATION = 20  # ms (allows 10ms, 20ms, 30ms frames)
VAD_MODE = 3  # 0-3, 0 is least aggressive, 3 is most aggressive
CHANNELS = 1  # Number of audio channels (1 for mono, 2 for stereo)
FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
BYTES_PER_SAMPLE = 2  # Bytes per sample
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION / 1000)  # Number of audio frames per buffer

# Silence configuration
ENERGY_THRESHOLD = 600  # higher threshold to avoid noise misfire
SILENCE_DURATION = 1.2  # detect silence if 1.2 seconds of silence


def log_ai_headers(response):
  """Display AI-Text-Request and AI-Text-Response headers if available"""
  request_text = response.headers.get("AI-Text-Request", "N/A")
  response_text = response.headers.get("AI-Text-Response", "N/A")
  request_text = urllib.parse.unquote(request_text) if request_text != "N/A" else "N/A"
  response_text = urllib.parse.unquote(response_text) if response_text != "N/A" else "N/A"
  print("\n🧾 Response Headers:")
  print(f"---\n📥 AI-Text-Request:\n'{request_text}'\n")
  print(f"📤 AI-Text-Response:\n'{response_text}'\n---\n")


def play_local_audio(filename):
  """Play an MP3 audio file from the assets folder"""
  path = ASSETS_PATH + filename
  with open(path, "rb") as f:
    play_audio(f.read())


def is_loud_enough(frame, threshold=ENERGY_THRESHOLD):
  # Convert frame to 16-bit signed integers
  count = len(frame) // 2
  shorts = struct.unpack(f"{count}h", frame)

  # Calculate RMS
  sum_squares = sum(sample**2 for sample in shorts)
  rms = math.sqrt(sum_squares / count)

  return rms > threshold


def record_with_vad(timeout=10, idle_timeout=15):
  """Record audio while voice is detected using VAD with filtering and timeout"""
  vad = webrtcvad.Vad()
  vad.set_mode(VAD_MODE)

  pa = pyaudio.PyAudio()
  stream = pa.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=SAMPLE_RATE,
    input=True,
    frames_per_buffer=FRAME_SIZE
  )

  print("🎤 Listening with VAD (waiting for real voice)...")
  frames = []
  ring_buffer = collections.deque(maxlen=15)
  triggered = False
  start_time = time.time()
  voice_start_time = None
  silence_start = None

  try:
    while True:
      current_time = time.time()

      # Exit if idle timeout passed and no speech triggered
      if not triggered and (current_time - start_time > idle_timeout):
        print("🛑 Idle timeout reached (no voice detected).")
        break

      try:
        frame = stream.read(FRAME_SIZE, exception_on_overflow=False)
      except IOError as e:
        print(f"⚠️ Stream read error: {e}")
        continue

      if len(frame) < FRAME_SIZE * BYTES_PER_SAMPLE:
        print("⚠️ Incomplete frame, skipping...")
        continue

      is_speech = vad.is_speech(frame, SAMPLE_RATE)

      if not triggered:
        ring_buffer.append((frame, is_speech))
        num_voiced = sum(1 for _, speech in ring_buffer if speech and is_loud_enough(_))

        if num_voiced > 0.9 * ring_buffer.maxlen:
          triggered = True
          voice_start_time = current_time
          print("🎙️ Voice detected. Start recording...")
          frames.extend(f for f, _ in ring_buffer)
          ring_buffer.clear()

      else:
        frames.append(frame)
        ring_buffer.append((frame, is_speech))

        if not is_speech:
          if silence_start is None:
            silence_start = current_time
          elif current_time - silence_start > SILENCE_DURATION:
            print("🛑 Silence detected, stopping recording.")
            break
        else:
          silence_start = None

        if current_time - voice_start_time > timeout:
          print("⏱️ Max recording time reached.")
          break

  finally:
    stream.stop_stream()
    stream.close()
    pa.terminate()

  if not frames:
    print("⚠️  No voice data recorded.")
    return None

  # Save and return WAV data
  wav_buffer = io.BytesIO()
  with wave.open(wav_buffer, "wb") as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(BYTES_PER_SAMPLE)
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(b''.join(frames))

  # Optional: save to temp file for debugging
  with open("temp_record.wav", "wb") as f:
    f.write(wav_buffer.getvalue())

  return wav_buffer.getvalue()


def send_audio_to_api(audio_data):
  """Send WAV audio to API and receive MP3 response"""
  print("⏳ Processing recorded audio...")
  headers = {"content-type": "audio/wav"}
  response = requests.post(SPEECH_TO_SPEECH_API, headers=headers, data=audio_data)

  if response.status_code == 200:
    print("📩 Received response audio!")
    log_ai_headers(response)
    return response.content
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
  """Enter listen mode with VAD-based recording"""
  while True:
    audio_data = record_with_vad()
    if audio_data:
      response_audio = send_audio_to_api(audio_data)
      if response_audio:
        play_audio(response_audio)
    else:
      print("⌛️ Returning to standby mode...")
      play_local_audio("standby.mp3")
      print("🔁 Returned to standby mode.\n---\n\n")
      print("🤖 Say 'lilo' to wake up the assistant.")
      print("🎧 Listening for wake word...")
      break


def wake_word_detection():
  """Detect wake word using speech recognition"""
  recognizer = sr.Recognizer()
  try:
    mic = sr.Microphone()
  except Exception as e:
    print(f"❌ Error initializing microphone: {e}")
    return

  try:
    with mic as source:
      print("🎤 Adjusting for ambient noise...")
      # recognizer.energy_threshold = 350  
      # recognizer.pause_threshold = 0.8  # waktu hening antar kata (opsional)
      recognizer.adjust_for_ambient_noise(source, duration=1.5)
      print("✅ Noise adjustment completed.")
  except Exception as e:
    print(f"❌ Error during noise adjustment: {e}")
    return

  print(f"\n🤖 Say '{WAKE_WORD}' to wake up the assistant.")
  print("🎧 Listening for wake word...")
  while True:
    try:
      with mic as source:
        audio = recognizer.listen(source)
      text = recognizer.recognize_google(audio).lower()
      print(f"🦻 Heard: {text}")

      if WAKE_WORD in text:
        print(f"\n🚀 Wake word '{WAKE_WORD}' detected in: '{text}'")
        play_local_audio("wake-up.mp3")
        listen_mode()
      else:
        print("❌ Skipping, because it's not a wake word\n")
        play_local_audio("skip.mp3")
        print(f"🤖 Say '{WAKE_WORD}' to wake up the assistant.")
        print("🎧 Listening for wake word...")

    except sr.UnknownValueError:
      pass  # No speech detected or unrecognized speech
    except sr.RequestError:
      print("❌ Speech recognition service unavailable\n")
    except KeyboardInterrupt:
      print("👋 Stopping wake word detection...")
      break
    except Exception as e:
      print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
  wake_word_detection()
