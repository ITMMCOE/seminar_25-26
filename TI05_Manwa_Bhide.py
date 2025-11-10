import os, threading, time, random
import numpy as np
import tkinter as tk
from tkinter import messagebox, simpledialog

# --- Gemini AI import (stub for now, ready for integration if API key supplied) ---
try:
    import google.generativeai as genai
except ImportError:
    import subprocess, sys; subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai"])
    import google.generativeai as genai

# --- Robust speaker verification (resemblyzer) ---
try:
    from resemblyzer import VoiceEncoder, preprocess_wav
except ImportError:
    import subprocess, sys; subprocess.check_call([sys.executable, "-m", "pip", "install", "resemblyzer"])
    from resemblyzer import VoiceEncoder, preprocess_wav

try:
    import soundfile as sf
    import sounddevice as sd
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "soundfile", "sounddevice"])
    import soundfile as sf
    import sounddevice as sd

try:
    import pyttsx3
except ImportError:
    import subprocess, sys; subprocess.check_call([sys.executable, "-m", "pip", "install", "pyttsx3"])
    import pyttsx3

try:
    import speech_recognition as sr
except ImportError:
    import subprocess, sys; subprocess.check_call([sys.executable, "-m", "pip", "install", "SpeechRecognition"])
    import speech_recognition as sr

EMBEDDING_FILE = "manwa_enroll_embed.npy"
PASSWORD_FILE = "manwa_locker.txt"
GEMINI_KEY = "YOUR_GEMINI_KEY"  # ← Put your key here!

def speak(text):
    engine = pyttsx3.init()
    # Prefer a female voice: pick the first with 'female' or 'zira' in name
    for v in engine.getProperty('voices'):
        if 'female' in v.name.lower() or 'zira' in v.name.lower():
            engine.setProperty('voice', v.id)
            break
    engine.setProperty('rate', 175)
    engine.setProperty('volume', 1.0)
    engine.say(text)
    engine.runAndWait()

def record_audio(filename, duration=3, samplerate=16000):
    speak("Voice recording started")
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)
    sd.wait()
    sf.write(filename, recording, samplerate)
    speak(f"Recording complete")
    return filename

def enroll_speaker_multi(samples=3, locker_pwd=None):
    encoder = VoiceEncoder()
    all_embeds = []
    for i in range(samples):
        fname = f"enroll_voice_{i+1}.wav"
        # Only neutral progress voice
        speak(f"Recording {i+1} started")
        record_audio(fname)
        wav = preprocess_wav(fname)
        embed = encoder.embed_utterance(wav)
        all_embeds.append(embed)
        speak(f"Sample {i+1} complete")
    avg_embed = np.mean(all_embeds, axis=0)
    np.save(EMBEDDING_FILE, avg_embed)
    if locker_pwd:
        with open(PASSWORD_FILE,"w") as f: f.write(locker_pwd)
    speak("Your voice has been trained and saved.")

def check_locker_password():
    if not os.path.exists(PASSWORD_FILE):
        return True
    with open(PASSWORD_FILE) as f: correct_pwd = f.read().strip()
    password = simpledialog.askstring("Voice Locker", "Enter password to overwrite voice:", show='*')
    return password == correct_pwd

def test_speaker(filename):
    if not os.path.exists(EMBEDDING_FILE):
        speak("No enrolled voice found.")
        return False
    ref_embed = np.load(EMBEDDING_FILE)
    wav = preprocess_wav(filename)
    encoder = VoiceEncoder()
    test_embed = encoder.embed_utterance(wav)
    similarity = np.dot(ref_embed, test_embed)/(np.linalg.norm(ref_embed)*np.linalg.norm(test_embed))
    return similarity > 0.75

def recognize_phrase(filename):
    r = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = r.record(source)
    try:
        txt = r.recognize_google(audio).lower()
        txt = txt.replace(".", " ").replace(",", " ").strip()
        return txt
    except: return ""

def is_wake_phrase(phrase):
    # Accepts "hello agent, this is manwa"
    return phrase.startswith("hello agent") and "this is manwa" in phrase

# ---- DESIGN + FLOW ----

class FuturisticVoiceUI:
    def __init__(self, master):
        self.master = master
        master.title("NOVA: Secure Voice Unlocker")
        master.attributes('-fullscreen', True)
        master.configure(bg="#0b1321")
        self.is_animating = True
        self.listening = False
        self.speaking = False
        self.unlocked = False
        self.waveform = np.zeros(80)
        self.detected_phrase = ""
        # Canvas for ring/wave+bg
        self.canvas = tk.Canvas(master, bg="#0b1321", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.particles = [self._random_particle() for _ in range(46)]

        # Title at top center
        self.title_label = tk.Label(master, text="NOVA | SECURE VOICE UNLOCK", font=("Consolas", 26, "bold"),
                                   bg="#052043", fg="#47f7fa", bd=0, relief=tk.FLAT)
        self.title_label.place(relx=0.5, rely=0.06, anchor=tk.CENTER)

        # Main "lock/unlock" status
        self.center_label = tk.Label(master, text="System Locked", font=("Consolas", 21, "bold"),
                                     bg="#0b1321", fg="#54cafe", justify="center")
        self.center_label.place(relx=0.5, rely=0.72, anchor=tk.CENTER)

        # Phrase display (real-time)
        self.phrase_label = tk.Label(master, text="", font=("Cascadia Mono", 19, "bold"),
                                     bg="#051e32", fg="#a2ffe8", bd=0, relief=tk.FLAT)
        self.phrase_label.place(relx=0.5, rely=0.63, anchor=tk.CENTER)

        # Status label at bottom
        self.status_label = tk.Label(master, text="Listening for wake phrase...", font=("Consolas", 14, "bold"),
                                     bg="#0b1321", fg="#2ad2ff")
        self.status_label.place(relx=0.5, rely=0.94, anchor=tk.CENTER)

        # Right corners: buttons
        self.btn_fr = tk.Frame(master, bg="#0b1321", bd=0)
        self.btn_fr.place(relx=0.965, rely=0.14, anchor=tk.NE)
        self.btn_enroll = self._make_button("🎙️ Train", "#32e6fa", "#1eeec7", self._enroll_voice)
        self.btn_test = self._make_button("🔍 Test", "#dedc61", "#52ff5e", self._test_voice)
        self.btn_locker = self._make_button("🛡️ Locker", "#fd4477", "#6be7ff", self._change_voice)
        self.btn_exit = self._make_button("❌ Exit", "#c65bff", "#d11a1a", master.quit)
        for b,i in zip([self.btn_enroll, self.btn_test, self.btn_locker, self.btn_exit], range(4)):
            b.grid(row=i, column=0, pady=8, ipadx=10, ipady=5, sticky="ew")

        # Animations
        threading.Thread(target=self._background_animation, daemon=True).start()
        threading.Thread(target=self._ring_and_wave_animation, daemon=True).start()
        threading.Thread(target=self._wakeword_listen_loop, daemon=True).start()

    def _make_button(self, label, fg_from, fg_to, cmd):
        # Futuristic glass button
        btn = tk.Button(
            self.btn_fr, text=label, font=("Consolas", 15, "bold"),
            bg="#0d2747", fg=fg_from, activebackground="#203463",
            activeforeground=fg_to, bd=0, relief=tk.FLAT, cursor="hand2",
            command=lambda: self._wrap_action(cmd)
        )
        def on_enter(e, btn=btn, color=fg_to): btn.config(fg=color, bg="#11366b")
        def on_leave(e, btn=btn, color=fg_from): btn.config(fg=color, bg="#0d2747")
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    def _wrap_action(self, func):
        self.speaking = True
        self.status_label.update(); self.master.update()
        threading.Thread(target=self._reset_speaking, daemon=True).start()
        try: func()
        finally: pass

    def _reset_speaking(self): time.sleep(4.2); self.speaking = False

    def _random_particle(self):
        c = random.choice(["#15faff", "#00d1fb", "#0145b9", "#083f7e", "#47f7fa"])
        return [random.randint(90, 1700), random.randint(140, 900), random.randint(14, 46),
                random.uniform(-0.4,1.1), random.uniform(-0.8,0.6), c]

    def _background_animation(self):
        while self.is_animating:
            self.canvas.delete("all")
            for p in self.particles:
                x,y,r,dx,dy,c = p
                self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=c+"2E", outline=c, width=1 + r//20)
                p[0] += dx; p[1] += dy
                if not (60 < p[0] < 1780): p[3]*=-1; p[0]=max(61,min(1779,p[0]))
                if not (110 < p[1] < 980): p[4]*=-1; p[1]=max(120,min(960,p[1]))
            self.master.update_idletasks()
            self.canvas.after(28)

    def _ring_and_wave_animation(self):
        base = (950, 430, 180)
        n_wave = len(self.waveform)
        angle = 0
        while self.is_animating:
            self.canvas.delete("ring")
            for i in range(n_wave):
                th = (2 * np.pi * i / n_wave) + angle
                amp = 48 + 36 * self.waveform[i]
                x = base[0] + (base[2]+amp//3) * np.cos(th)
                y = base[1] + (base[2]+amp//3) * np.sin(th)
                self.canvas.create_oval(x-amp//8, y-amp//8, x+amp//8, y+amp//8,
                    fill="#3af0e6" if self.listening or self.speaking else "#124c8c",
                    outline="", tags="ring")
            n_parts = 27
            for i in range(n_parts):
                seg_angle = (2 * np.pi * i / n_parts) + angle
                rad2 = base[2] + ((17 if self.speaking else (24 if self.listening else 7)) * np.sin(angle+i))
                x1 = base[0] + (rad2) * np.cos(seg_angle)
                y1 = base[1] + (rad2) * np.sin(seg_angle)
                x2 = base[0] + (rad2 + (16 if self.listening or self.speaking else 8)) * np.cos(seg_angle)
                y2 = base[1] + (rad2 + (16 if self.listening or self.speaking else 8)) * np.sin(seg_angle)
                c = "#4affff" if self.speaking else ("#159ffc" if self.listening else "#014a96")
                self.canvas.create_line(x1,y1,x2,y2,fill=c,width=7 if self.speaking else 3,capstyle=tk.ROUND,tags="ring")
            self.canvas.create_oval(base[0]-104, base[1]-104, base[0]+104, base[1]+104, fill="#061224", outline="#28f7fb" if self.unlocked else "#1e3750", width=7, tags="ring")
            angle += 0.052 + (0.03 if self.speaking else 0)
            self.master.update_idletasks()
            self.canvas.after(35)

    def _wakeword_listen_loop(self):
        while True:
            self.status_label.config(text="Listening for: 'Hello Agent, this is manwa'", fg="#21c9ff")
            self.center_label.config(text="System Locked", fg="#54cafe")
            self.phrase_label.config(text="")
            self.listening = True; self.waveform = np.zeros_like(self.waveform)

            # Live record/display phrase/animation
            samplerate, duration = 16000, 4
            buffer, transcribed = [], ""
            def callback(indata, frames, time, status):
                vol = np.abs(indata).mean()
                self.waveform = np.roll(self.waveform, -1)
                self.waveform[-1] = min(1.0, 3.7*vol)
                buffer.extend(indata[:,0].tolist())
            self.master.update()
            with sd.InputStream(channels=1, samplerate=samplerate, callback=callback):
                time.sleep(duration)
            buf_np = np.array(buffer)
            tmp_file = "temp_unlock_test.wav"
            sf.write(tmp_file, buf_np, samplerate)
            self.listening = False

            # Recognize, display detected phrase
            phrase = recognize_phrase(tmp_file)
            self.phrase_label.config(text="DETECTED:  " + phrase.upper())
            self.master.update()
            matched_phrase = is_wake_phrase(phrase)
            matched_voice = test_speaker(tmp_file)
            if matched_phrase and matched_voice:
                self.status_label.config(text="Welcome Boss, voice recognized and system unlocked.", fg="#10ff3a")
            
                speak("Welcome boss, voice recognized successfully. Unlocked the system. How can I help you today?")
                self.unlocked = True
                #--------------------------
                if matched_phrase and matched_voice:
                    self.status_label.config(text="Unlocked and listening, awaiting your command...", fg="#14fabf")
                    self.center_label.place_forget()
                    self.phrase_label.place_forget()
                    speak("Welcome boss, voice recognized successfully. System unlocked. Nova is listening.")
                    self.unlocked = True
                    # ------- Now enter Gemini/Jarvis command loop --------
                    while True:
                        self.status_label.config(text="Listening for your command...", fg="#31e8ea")
                        self.listening = True; self.waveform = np.zeros_like(self.waveform)
                        samplerate, duration = 16000, 4
                        buffer = []
                        def callback(indata, frames, time, status):
                            vol = np.abs(indata).mean()
                            self.waveform = np.roll(self.waveform, -1)
                            self.waveform[-1] = min(1.0, 3.7*vol)
                            buffer.extend(indata[:,0].tolist())
                        self.master.update()
                        with sd.InputStream(channels=1, samplerate=samplerate, callback=callback):
                            time.sleep(duration)
                        buf_np = np.array(buffer)
                        command_file = "nova_command_temp.wav"
                        sf.write(command_file, buf_np, samplerate)
                        self.listening = False
                        user_command = recognize_phrase(command_file)
                        # Display command on screen for a moment
                        self.status_label.config(text="Command: " + user_command, fg="#69eaff")
                        self.master.update()
                        # Here, send to Gemini and get the response
                        if user_command.strip():
                            # Placeholder for Gemini call
                            try:
                                if GEMINI_KEY and GEMINI_KEY != "YOUR_API_KEY_HERE":
                                    genai.configure(api_key=GEMINI_KEY)
                                    model = genai.GenerativeModel("gemini-2.0-flash-exp")
                                    response = model.generate_content(user_command+" response in a short manner, remember you are an Helpful AI assistant. and keep it concise.")
                                    output_text = response.text.strip()
                                else:
                                    output_text = "Gemini not configured. (API Key missing or wrong.)"
                            except Exception as e:
                                output_text = f"Gemini error: {e}"
                        else:
                            output_text = "Sorry, I couldn't hear your command."
                        # Speak and display Gemini output
                        self.status_label.config(text=output_text, fg="#ffec6b")
                        speak(output_text)
                        time.sleep(2)

                #------------------------
                  # Agent logic ready for next phase
                
            elif not matched_phrase:
                self.status_label.config(text="Wrong phrase, try again.", fg="#fd4747")
                self.phrase_label.config(text="Phrase Not Recognized!", fg="#ffadad")
                speak("Sorry, the spoken phrase did not match.")
            elif not matched_voice:
                self.status_label.config(text="Voice not recognized!", fg="#ef4141")
                self.phrase_label.config(fg="#fdc8c8")
                speak("Sorry, your voice was not recognized.")
            self.unlocked = False
            time.sleep(2)

    def _enroll_voice(self):
        try:
            self.status_label.config(text="Recording multiple enrollment samples...", fg="#52fff8")
            self.phrase_label.config(text="")
            self.master.update()
            enroll_speaker_multi(samples=3)
            self.status_label.config(text="Voice enrolled & trained!", fg="#38f8f8")
        except Exception as e:
            self.status_label.config(text=f"Error: {e}", fg="#ff2626")
            speak("Training error.")

    def _test_voice(self):
        try:
            self.status_label.config(text="Recording for verification...", fg="#fdff78")
            self.phrase_label.config(text="")
            self.master.update()
            test_file = "test_manwa_voice.wav"
            record_audio(test_file, duration=3)
            phrase = recognize_phrase(test_file)
            self.phrase_label.config(text="DETECTED:  " + phrase.upper())
            self.master.update()
            if test_speaker(test_file):
                self.status_label.config(text="Access granted: manwa voice matched.", fg="#8aff7a")
            else:
                self.status_label.config(text="Access rejected: Voice not matched.", fg="#ff7979")
        except Exception as e:
            self.status_label.config(text=f"Error: {e}", fg="#ff4c4c")
            speak("Verification error.")

    def _change_voice(self):
        if check_locker_password():
            locker_pwd = simpledialog.askstring("Set New Locker Password", "Enter new password:", show='*')
            self.status_label.config(text="Overwriting enrolled voice...", fg="#ffe29b")
            self.phrase_label.config(text="")
            self.master.update()
            enroll_speaker_multi(samples=3, locker_pwd=locker_pwd)
            self.status_label.config(text="Voice & password updated.", fg="#69fff5")
            speak("New voice and password enrolled.")
        else:
            self.status_label.config(text="Incorrect password.", fg="#ff2626")
            speak("Incorrect password. Cannot change voice.")

def main():
    root = tk.Tk()
    app = FuturisticVoiceUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

