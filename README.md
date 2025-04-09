# 🎙️ Echo Buddy (Raspberry Pi Compatible)

A conversational AI you can talk to using your voice. It listens for a wake word (e.g., `"lilo"`), records your speech, sends it to a server, and replies with generated audio. Built with Python and Speech Recognition.

Repo: [https://github.com/gadingnst/echo-buddy](https://github.com/gadingnst/echo-buddy)

---

## 🧰 Requirements

- Python 3.11
- Linux/macOS/Raspberry Pi (or Windows with `mpg123`)
- Microphone & speaker
- Internet connection (for API calls)

---

## 📦 Setup

### 1. Clone the Repository

```bash
git clone https://github.com/gadingnst/echo-buddy.git
cd echo-buddy
```

### 2. Create and Activate Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # For Linux/macOS/Raspberry Pi
# venv\Scripts\activate   # For Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If you don't have a `requirements.txt`, use:

```txt
pyaudio
speechrecognition
requests
```

> ⚠️ For Linux users, install PortAudio if needed:
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
```

> 🔊 To play audio with `mpg123`:
```bash
# macOS (with Homebrew)
brew install mpg123

# Ubuntu/Debian/Raspberry Pi
sudo apt install mpg123
```

---

## 🍓 Raspberry Pi Setup

To run Echo Buddy on a Raspberry Pi:

1. Make sure you’re using **Raspberry Pi OS (Bookworm or Bullseye)**.
2. Plug in a **USB microphone** and **speaker or 3.5mm jack speaker**.
3. Install system dependencies:

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv portaudio19-dev python3-pyaudio mpg123
```

4. Clone, create virtual environment, and install packages as shown above.
5. Test microphone and audio output:

```bash
arecord -l  # Check microphone
aplay /usr/share/sounds/alsa/Front_Center.wav  # Test speaker
```

6. Run Echo Buddy:

```bash
python server.py
```

If needed, configure audio input/output with `alsamixer` and `arecord`.

---

## 🚀 Running the Assistant

```bash
python server.py
```

Once started, the assistant will:
1. Calibrate the microphone
2. Listen for your wake word (default: `"lilo"`)
3. Record your voice
4. Send it to the API and play the AI's audio response

---

## 🔁 Auto Run on Boot (Raspberry Pi)

To enable automatic startup on boot using the provided script:

```bash
sudo ./setup_autorun.sh
```

This script will:
- Ensure `run.sh` is executable
- Create and register a systemd service
- Enable Echo Buddy to start automatically after reboot

To check or manage the service:

```bash
sudo systemctl status echobuddy
sudo systemctl restart echobuddy
sudo systemctl stop echobuddy
```

---

## 🛠️ Configuration

You can customize the assistant inside `server.py`:
- `WAKE_WORD`: Change the word that activates the assistant
- `BASE_URL`: The server that handles speech-to-speech
- `ASSETS_PATH`: Folder for audio effects like `wake-up.mp3`

---

## 📁 Assets

Put your sound files (like `wake-up.mp3`, `skip.mp3`) inside the `assets/` directory.

---

## 🧪 Troubleshooting

- Ensure microphone access is enabled in your OS
- Make sure `pyaudio` is installed correctly
- Check audio input/output devices if it doesn't respond
- Run `alsamixer` to unmute or switch input/output devices

---

## 📜 License

This project is licensed under a **Custom License**:  
See [LICENSE](LICENSE) for more details.

---

Made with ❤️ by Gading Nasution in 2025.