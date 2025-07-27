# =============================================================================
# Shiva Voice Assistant
#
# Author: Shyam Yadav
# GitHub: https://github.com/shyamyadavji
#
# Description: An advanced desktop voice assistant built with Python, featuring
#              real-time noise reduction, local system control, and AI integration.
# =============================================================================

import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import threading
import asyncio
import pyttsx3
import datetime
import wikipedia
import webbrowser
import os
import time
import speech_recognition as sr
import google.generativeai as genai
import re
import numpy as np
import noisereduce as nr
from dotenv import load_dotenv # <<< ADD THIS LINE

# Load environment variables from .env file
load_dotenv() # <<< ADD THIS LINE

# =====================================
# Configuration
# =====================================
print("--- Configuration Phase ---")

# --- API Key Configuration (Securely Loaded from .env file) ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

GENERATIVE_MODEL_NAME = "gemini-1.5-flash" # Or "gemini-pro"

google_ai_configured = False
ai_model_loaded = False # Flag specifically for model loading success

if not GOOGLE_API_KEY or "YOUR_API_KEY" in GOOGLE_API_KEY:
    print("\n!!! WARNING: GOOGLE_API_KEY is not set correctly! AI will fail. !!!\n")
    GOOGLE_API_KEY = None
else:
    print(f"Using GOOGLE_API_KEY from .env file, starting with: {GOOGLE_API_KEY[:4]}...{GOOGLE_API_KEY[-4:]}")
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        print("Google AI SDK configured successfully using hardcoded key.")
        google_ai_configured = True
    except Exception as e:
        print(f"\n!!! ERROR configuring Google AI SDK: {e} !!!\n")
        GOOGLE_API_KEY = None

# --- Other Settings ---
GIF_OVERLAY_ALPHA = 160
ENABLE_NOISE_REDUCTION = True
DEFAULT_MUSIC_FOLDER = r"C:\Users\SHYAM YADAV\Music"
DEFAULT_PDF_PATH = r"C:\Users\SHYAM YADAV\Downloads\Shivavoice\SHIVA_PDF.3[1].pdf"
DEFAULT_WORD_PATH = r"C:\Users\SHYAM YADAV\Downloads\Shivavoice\project_report_shyam[1].docx"
DEFAULT_VIDEO_PATH = r"C:\Users\SHYAM YADAV\OneDrive\Desktop\Shivavoice\videoplayback.mp4"
DEFAULT_GIF_PATH = r"C:\Users\SHYAM YADAV\OneDrive\Desktop\Shivavoice\Generated shiva.gif"

print("--- End Configuration Phase ---")

# =====================================
# Shiva: Voice Assistant Class
# =====================================
class Shiva:
    def __init__(self):
        global ai_model_loaded
        print("\n--- Initializing Shiva ---")
        self.engine = pyttsx3.init(); self.recognizer = sr.Recognizer(); self.name = "Shiva"; self.genai_model = None; ai_model_loaded = False; self.ambient_noise_adjusted = False
        if google_ai_configured:
            print(f"Attempting load: '{GENERATIVE_MODEL_NAME}'...");
            try:
                self.genai_model = genai.GenerativeModel(GENERATIVE_MODEL_NAME)
                print(f"Successfully loaded Google AI Model: '{GENERATIVE_MODEL_NAME}'.")
                ai_model_loaded = True
            except Exception as e:
                print(f"\n!!! ERROR loading AI Model '{GENERATIVE_MODEL_NAME}': {e} !!!\n")
        else: print("Google AI SDK not configured, skipping AI model loading.")
        try:
            with sr.Microphone() as source: print("Adjusting noise..."); self.recognizer.adjust_for_ambient_noise(source, duration=2.0); self.ambient_noise_adjusted = True; print("Noise adjust done.")
        except OSError as e: print(f"\n!!! Mic OS Error: {e} !!!");
        except Exception as e: print(f"Mic init error: {e}");
        self.recognizer.pause_threshold = 1.0; self.recognizer.dynamic_energy_threshold = True; print("--- Shiva Initialized ---")

    async def speak(self, text):
        if not text: return; print(f"Shiva: {text[:100]}{'...' if len(text)>100 else ''}")
        try: self.engine.say(text); self.engine.runAndWait()
        except Exception as e: print(f"Speech synthesis error: {e}")
    async def take_command(self):
        query = "none";
        try:
            with sr.Microphone() as source:
                print("Listening...");
                try:
                    audio_data = self.recognizer.listen(source, timeout=7, phrase_time_limit=10); print("Processing...")
                    if ENABLE_NOISE_REDUCTION:
                        try:
                            raw_data=audio_data.get_raw_data(); sr_rate=audio_data.sample_rate; sw=audio_data.sample_width; dtype={1:np.int8, 2:np.int16, 4:np.int32}.get(sw,np.int16)
                            if sw not in [1,2,4]: print(f"Warn: Sample width {sw}");
                            aud_samp=np.frombuffer(raw_data,dtype=dtype);
                            if np.max(np.abs(aud_samp))>0:
                                aud_fl=aud_samp.astype(np.float32)/np.iinfo(dtype).max; red_fl=nr.reduce_noise(y=aud_fl,sr=sr_rate,stationary=True,prop_decrease=0.85); red_samp=(red_fl*np.iinfo(dtype).max).astype(dtype); proc_raw=red_samp.tobytes(); audio_data=sr.AudioData(proc_raw,sr_rate,sw); print("Noise reduction applied.")
                            else: print("Silent audio, skipping NR.")
                        except ImportError: print("NR libs missing.");
                        except Exception as nr_e: print(f"NR error: {nr_e}");
                    print("Recognizing..."); query=self.recognizer.recognize_google(audio_data, language='en-in'); print(f"User: {query}"); return query.lower()
                except sr.WaitTimeoutError: print("No speech.");
                except sr.UnknownValueError: print("Audio unclear.");
                except sr.RequestError as e: print(f"Recognition API error: {e}");
                except Exception as e: print(f"Listen/Recognize error: {e}");
        except OSError as e: print(f"\n!!! Mic OS Error: {e} !!!"); await self.speak("Mic connection lost."); await asyncio.sleep(5)
        except Exception as mic_e: print(f"General mic access error: {mic_e}");
        return "none"
    async def ask_google_ai(self, question):
        if not self.genai_model:
            print("DEBUG: ask_google_ai called but self.genai_model is None.")
            if not google_ai_configured: return "My apologies. The AI connection setup failed, likely due to the API key."
            else: return f"My apologies. I couldn't load the specific AI model ('{GENERATIVE_MODEL_NAME}') during startup."
        if not question: return "What would you like to ask?"
        print(f"DEBUG: Sending to AI ({GENERATIVE_MODEL_NAME}): '{question}'");
        try:
            response = await self.genai_model.generate_content_async(question);
            if response.prompt_feedback and response.prompt_feedback.block_reason: reason = response.prompt_feedback.block_reason; print(f"AI blocked: {reason}"); return "Safety restrictions prevent response." if 'SAFETY' in str(reason).upper() else f"AI blocked: {reason}"
            answer = None;
            if response.candidates and response.candidates[0].content and response.candidates[0].content.parts: answer = "".join(part.text for part in response.candidates[0].content.parts).strip()
            if not answer and response.parts: answer = "".join(part.text for part in response.parts).strip()
            if not answer: finish_reason = response.candidates[0].finish_reason if response.candidates else "Unknown"; print(f"AI empty response. Finish Reason: {finish_reason}"); return "AI response unclear/empty."
            print(f"DEBUG: AI response received: {answer[:100]}..."); return answer
        except Exception as e:
            print(f"!!! Google AI API Error during generation: {e}"); err_msg = str(e).lower(); user_message = "Sorry, an error occurred while contacting the AI module."
            if "api key not valid" in err_msg or "permission denied" in err_msg: user_message = "The AI API key seems invalid or lacks permission."
            elif "quota" in err_msg or "resource exhausted" in err_msg: user_message = "The AI service is busy or the usage limit was reached."
            elif "model" in err_msg and ("not found" in err_msg or "404" in err_msg): user_message = f"The AI model '{GENERATIVE_MODEL_NAME}' could not be found or is unavailable."
            elif "connection" in err_msg or "network" in err_msg or "deadline exceeded" in err_msg: user_message = "I'm having trouble connecting to the AI service."
            print(f"DEBUG: AI Error User Message: {user_message}"); return user_message

    def _clean_query_for_builtin(self, query):
        cleaned = re.sub(r'^\s*shiva\b', '', query, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r'\b(please|can you|could you|tell me|what is|who is|open|play|start|show|display|search|set|get me|find)\b', '', cleaned, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    async def tell_time(self): await self.speak(f"Time is {datetime.datetime.now().strftime('%I:%M %p')}.")
    async def tell_date(self): await self.speak(f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}.")
    async def open_website(self, url, name):
        if not url.startswith("http"): url = "https://" + url;
        try: webbrowser.open(url); await self.speak(f"Opening {name}")
        except Exception as e: await self.speak(f"Couldn't open {name}. Error: {e}")
    async def play_music(self, music_dir=DEFAULT_MUSIC_FOLDER):
        try:
            if not os.path.isdir(music_dir): await self.speak(f"Music dir not found: {music_dir}"); return
            songs=os.listdir(music_dir); music_files=[s for s in songs if s.lower().endswith(('.mp3','.wav','.ogg','.flac','.m4a','.aac','.wma'))]
            if music_files:
                import random; song=random.choice(music_files); file=os.path.join(music_dir,song); name=os.path.splitext(song)[0];
                speak_name=re.sub(r'[_\-.]',' ',name).strip(); speak_name=re.sub(r'\[.*?\]|\(.*?\)|[\d\W]+$','',speak_name).strip(); speak_name=re.sub(r'\s+',' ',speak_name).strip();
                if len(speak_name)>50: speak_name=speak_name[:50]+"..."
                if not speak_name: speak_name="a song"
                print(f"Playing: {file}"); os.startfile(file); await self.speak(f"Playing {speak_name}.")
            else: await self.speak("No music found.")
        except Exception as e: print(f"Music error: {e}"); await self.speak("Error playing music.")
    async def search_wikipedia(self, search_term):
        if not search_term: await self.speak("What topic for Wikipedia?"); return
        try:
            await self.speak(f"Searching Wikipedia for {search_term}..."); wikipedia.set_lang("en");
            results = wikipedia.summary(search_term, sentences=3, auto_suggest=True, redirect=True)
            await self.speak(f"Wikipedia says: {results}")
        except wikipedia.exceptions.PageError: await self.speak(f"No Wikipedia page for '{search_term}'.")
        except wikipedia.exceptions.DisambiguationError as e: options=e.options[:3]; await self.speak(f"'{search_term}' could mean: {', '.join(options)}. Be specific?")
        except wikipedia.exceptions.WikipediaException as we: print(f"Wiki error: {we}"); await self.speak(f"Issue searching Wiki: {we}")
        except Exception as e: print(f"Wiki search error: {e}"); await self.speak("Error searching Wikipedia.")
    async def open_application(self, app_alias):
        app_map = {"notepad": "notepad.exe", "calculator": "calc.exe", "paint": "mspaint.exe", "command prompt": "cmd.exe", }
        app_to_open = app_map.get(app_alias.lower(), app_alias)
        try:
            print(f"Opening app: {app_to_open}"); os.startfile(app_to_open);
            speak_name=os.path.basename(app_to_open).replace('.exe','').replace('_',' '); await self.speak(f"Opening {speak_name}.")
        except FileNotFoundError: await self.speak(f"App not found '{app_to_open}'.")
        except Exception as e: await self.speak(f"Couldn't open app. Error: {e}")
    async def find_and_open_file(self, file_type, extensions, default_path, raw_query):
        path_match = re.search(r'((?:[a-zA-Z]:\\|\/)[^\s]+\.(?:' + '|'.join(extensions) + '))', raw_query, re.IGNORECASE)
        file_path = None;
        if path_match:
            extracted=path_match.group(1); print(f"Path extracted: {extracted}");
            if os.path.exists(extracted): file_path=extracted
            else: await self.speak(f"Specified {file_type} path doesn't exist. Trying default.")
        if not file_path:
             if default_path and os.path.exists(default_path): file_path=default_path; print(f"Using default {file_type}: {file_path}")
             else: await self.speak(f"Default {file_type} path invalid/not set."); return
        if file_path and os.path.exists(file_path) and file_path.lower().endswith(tuple('.'+ext for ext in extensions)):
            try: print(f"Opening {file_type}: {file_path}"); os.startfile(file_path); await self.speak(f"Opening the {file_type} file.")
            except Exception as e: await self.speak(f"Couldn't open {file_type}. Error: {e}")
        elif file_path: await self.speak(f"File ({os.path.basename(file_path)}) not a valid {file_type}.")
    async def open_pdf_file(self, raw_query): await self.find_and_open_file("PDF", ["pdf"], DEFAULT_PDF_PATH, raw_query)
    async def open_word_document(self, raw_query): await self.find_and_open_file("Word document", ["docx", "doc"], DEFAULT_WORD_PATH, raw_query)
    async def open_video_file(self, raw_query): await self.find_and_open_file("video", ["mp4", "avi", "mov", "mkv", "wmv"], DEFAULT_VIDEO_PATH, raw_query)
    async def set_timer(self, raw_query):
        try:
            match = re.search(r'(\d+(\.\d+)?)\s*(minute|min|second|sec|hour|hr)s?', raw_query, re.IGNORECASE)
            if not match: await self.speak("Specify duration like 'timer 5 minutes'."); return
            value=float(match.group(1)); unit=match.group(3).lower(); duration=0;
            if "min" in unit: duration=value*60
            elif "sec" in unit: duration=value
            elif "hr" in unit or "hour" in unit: duration=value*3600
            else: await self.speak("Invalid time unit."); return
            if duration<=0: await self.speak("Duration must be positive."); return
            if duration>=3600: speak_dur=f"{value} hour{'s' if value!=1 else ''}"
            elif duration>=60: speak_dur=f"{value} minute{'s' if value!=1 else ''}"
            else: speak_dur=f"{value} second{'s' if value!=1 else ''}"
            await self.speak(f"Timer set: {speak_dur}."); threading.Thread(target=self.timer_thread, args=(duration, speak_dur), daemon=True).start()
        except ValueError: await self.speak("Didn't understand duration.")
        except Exception as e: print(f"Timer error: {e}"); await self.speak("Error setting timer.")
    def timer_thread(self, duration_seconds, speak_duration):
        print(f"Timer started: {speak_duration} ({duration_seconds}s)."); time.sleep(duration_seconds); print(f"Timer finished: {speak_duration}");
        try:
            loop = asyncio.get_running_loop()
            loop.call_soon_threadsafe(asyncio.create_task, self.speak(f"Time's up! Your {speak_duration} timer is done."))
        except RuntimeError:
            print("Timer alert: Event loop not running. Trying synchronous speak.")
            try: self.engine.say(f"Time's up! Your {speak_duration} timer is done."); self.engine.runAndWait()
            except Exception as speak_e: print(f"Fallback timer speak error: {speak_e}")
        except Exception as e: print(f"Error scheduling timer alert: {e}")

    # --- PROCESS COMMAND (Implicit AI Fallback Logic) ---
    async def process_command(self, raw_query):
        """ Processes voice commands, prioritizing built-ins, then falling back to AI. """
        global root_window_ref
        if not raw_query or raw_query == "none": return

        l_raw_query = raw_query.lower()
        print(f"DEBUG: ---> Processing Raw Query: '{raw_query}' <---") # DEBUG
        command_handled = False

        # --- 1. Check for Exit Command ---
        if any(p in l_raw_query for p in ["stop listening", "stop now", "exit", "quit", "shutdown", "goodbye", "bye", "stop shiva"]):
             print("DEBUG: Exit command detected.") # DEBUG
             await self.speak("Goodbye! Shutting down.")
             stop_voice_loop.set()
             if root_window_ref and root_window_ref.winfo_exists():
                  print("DEBUG: Scheduling window close."); root_window_ref.after(50, on_close) # DEBUG
             return # Exit command takes precedence

        # --- 2. Check for Built-in Commands ---
        cleaned_for_builtin = self._clean_query_for_builtin(raw_query)
        print(f"DEBUG: Cleaned query for built-in check: '{cleaned_for_builtin}'") # DEBUG

        # Using elif chain for built-ins
        if "how are you" in cleaned_for_builtin: print("DEBUG: Matched built-in: how are you"); await self.speak("I am operational!"); command_handled = True # DEBUG
        elif "your name" in cleaned_for_builtin: print("DEBUG: Matched built-in: your name"); await self.speak(f"My name is {self.name}."); command_handled = True # DEBUG
        elif any(p in cleaned_for_builtin for p in ["who created you", "developer"]): print("DEBUG: Matched built-in: creator"); await self.speak("I was developed by Shyam Yadav."); command_handled = True # DEBUG
        elif any(p in cleaned_for_builtin for p in ["time"]): print("DEBUG: Matched built-in: time"); await self.tell_time(); command_handled = True # DEBUG
        elif any(p in cleaned_for_builtin for p in ["date"]): print("DEBUG: Matched built-in: date"); await self.tell_date(); command_handled = True # DEBUG
        elif "youtube" in cleaned_for_builtin: print("DEBUG: Matched built-in: youtube"); await self.open_website("https://www.youtube.com", "YouTube"); command_handled = True # DEBUG
        elif "google" in cleaned_for_builtin: print("DEBUG: Matched built-in: google"); await self.open_website("https://www.google.com", "Google"); command_handled = True # DEBUG
        elif l_raw_query.startswith(("open website", "shiva open website")): # Check raw query prefix for this specific one
             print("DEBUG: Matched built-in prefix: open website"); url_part = re.sub(r'^(shiva\s)?open\s+(website|site)\s*', '', raw_query, flags=re.IGNORECASE).strip() # DEBUG
             if url_part and '.' in url_part and ' ' not in url_part: await self.open_website(url_part, url_part)
             else: await self.speak("Which website?")
             command_handled = True # Set handled=True whether it opened or asked "which"
        elif any(p in cleaned_for_builtin for p in ["music", "song"]): print("DEBUG: Matched built-in: music"); await self.play_music(); command_handled = True # DEBUG
        elif any(p in cleaned_for_builtin for p in ["video"]): print("DEBUG: Matched built-in: video"); await self.open_video_file(raw_query); command_handled = True # DEBUG
        elif "pdf" in cleaned_for_builtin: print("DEBUG: Matched built-in: pdf"); await self.open_pdf_file(raw_query); command_handled = True # DEBUG
        elif any(p in cleaned_for_builtin for p in ["word document", "word doc", "word file"]): print("DEBUG: Matched built-in: word"); await self.open_word_document(raw_query); command_handled = True # DEBUG
        elif "notepad" in cleaned_for_builtin: print("DEBUG: Matched built-in: notepad"); await self.open_application("notepad"); command_handled = True # DEBUG
        elif "calculator" in cleaned_for_builtin: print("DEBUG: Matched built-in: calculator"); await self.open_application("calculator"); command_handled = True # DEBUG
        elif "paint" in cleaned_for_builtin: print("DEBUG: Matched built-in: paint"); await self.open_application("paint"); command_handled = True # DEBUG
        elif "command prompt" in cleaned_for_builtin: print("DEBUG: Matched built-in: cmd"); await self.open_application("command prompt"); command_handled = True # DEBUG
        elif "wikipedia" in cleaned_for_builtin:
            print("DEBUG: Matched built-in: wikipedia"); search_term = cleaned_for_builtin.replace("wikipedia", "").strip(); await self.search_wikipedia(search_term); command_handled = True # DEBUG
        elif "weather" in cleaned_for_builtin: # Uses AI internally
            print("DEBUG: Matched built-in: weather"); city = "your location"; match = re.search(r'weather in\s+(.+)', raw_query, re.IGNORECASE); # DEBUG
            if match: city = match.group(1).strip()
            weather_query = f"Briefly, what is the current weather in {city}?"; print("DEBUG: AI Query for weather...") # DEBUG
            info = await self.ask_google_ai(weather_query); await self.speak(info); command_handled = True
        elif any(p in cleaned_for_builtin for p in ["fun fact", "fact"]): # Uses AI internally
             print("DEBUG: Matched built-in: fact"); print("DEBUG: AI Query for fact...") # DEBUG
             fact = await self.ask_google_ai("Tell me an interesting short fun fact."); await self.speak(fact); command_handled = True
        elif "timer" in cleaned_for_builtin: print("DEBUG: Matched built-in: timer"); await self.set_timer(raw_query); command_handled = True # DEBUG
        elif "send email" in cleaned_for_builtin: print("DEBUG: Matched built-in: email"); await self.speak("Sorry, I cannot send emails."); command_handled = True # DEBUG
        elif any(p in cleaned_for_builtin for p in ["hold on", "wait", "pause"]):
             print("DEBUG: Matched built-in: pause"); await self.speak("Pausing for 30 seconds."); await asyncio.sleep(30); await self.speak("Listening again."); command_handled = True # DEBUG

        # --- 3. IMPLICIT AI Fallback (if no built-in command was handled) ---
        if not command_handled:
            print("DEBUG: No built-in match found. Attempting AI fallback.") # DEBUG
            # Check if AI is available before calling
            if self.genai_model:
                # Use the raw query for the AI, as cleaning might remove context
                ai_question = raw_query
                print(f"DEBUG: Sending to AI (Fallback): '{ai_question}'") # DEBUG
                # Optional: Add a brief lead-in phrase
                # await self.speak("Let me check that...")
                answer = await self.ask_google_ai(ai_question)
                await self.speak(answer)
            else:
                # AI is not available (config or model load failed)
                print("DEBUG: AI fallback attempted, but AI model not loaded.") # DEBUG
                await self.speak("Sorry, I didn't understand that command, and my AI helper is unavailable.")
            # Fallback case is always considered "handled" now, even if AI is unavailable
            command_handled = True

        # --- Redundant Fallback - Can be removed if above handled=True is set ---
        # if not command_handled: # This should ideally not be reached anymore
        #    print(f"DEBUG: Command fell through all checks: '{raw_query}'") # DEBUG
        #    await self.speak("Sorry, I couldn't process that command.")


    async def greet(self): # Neutral greeting
        hour=datetime.datetime.now().hour; greet="Good morning!" if 0<=hour<12 else "Good afternoon!" if 12<=hour<18 else "Good evening!"
        await self.speak(f"{greet} This is Shiva. How may I assist?")

# ===============================================
# UI Component: Animated GIF Background Label (FIXED ANIMATION LOGIC)
# ===============================================
class AnimatedGIFLabel(tk.Label):
    """ A Tkinter Label that displays an animated GIF with overlay. """
    def __init__(self, master, gif_path, delay=100, overlay_alpha=128, **kwargs):
        super().__init__(master, **kwargs)
        self.gif_path = gif_path
        self.delay = delay
        self.overlay_alpha = overlay_alpha
        self.frames = []
        self.idx = 0
        self._job = None # Stores the job ID from root.after
        self._is_running = False # Flag to control animation loop
        print(f"Loading GIF: {self.gif_path}")
        self.load_gif() # Load frames during initialization

        if self.frames:
            print(f"GIF loaded: {len(self.frames)} frames.")
            # Configure the label with the first frame
            self.config(image=self.frames[self.idx], bg="black")
            # Start the animation loop
            self.start_animation()
        else:
            # Handle GIF loading failure
            print("Failed GIF load.")
            err_text = f"Error loading GIF:\n{os.path.basename(self.gif_path)}\nCheck path/file."
            self.config(text=err_text, fg="red", bg="black", font=("Arial", 16), wraplength=master.winfo_screenwidth()-100)

    def load_gif(self):
        """ Loads and processes GIF frames. """
        if not os.path.exists(self.gif_path):
            print(f"ERR: GIF file not found: {self.gif_path}")
            self.frames = []
            return
        try:
            # Open the GIF
            self.gif = Image.open(self.gif_path)
            self.frames = []
            self.master.update_idletasks() # Ensure window size is available
            # Get target size (usually fullscreen)
            screen_w, screen_h = self.master.winfo_width(), self.master.winfo_height()
            if screen_w < 100 or screen_h < 100 : # Fallback if window not ready
                screen_w, screen_h = self.master.winfo_screenwidth(), self.master.winfo_screenheight()
            print(f"Target size for GIF frames: {screen_w}x{screen_h}")

            # Iterate through frames, apply overlay, resize, and store as PhotoImage
            for i, frame in enumerate(ImageSequence.Iterator(self.gif)):
                frame = frame.convert("RGBA") # Ensure RGBA for transparency handling
                overlay = Image.new("RGBA", frame.size, (0, 0, 0, self.overlay_alpha)) # Create overlay
                blended = Image.alpha_composite(frame, overlay) # Blend frame and overlay
                resized = blended.resize((screen_w, screen_h), Image.Resampling.LANCZOS) # Resize
                self.frames.append(ImageTk.PhotoImage(resized)) # Convert to Tkinter format

            self._original_gif_img = self.gif # Keep reference to original PIL image
            print(f"GIF processing complete: {len(self.frames)} frames.")
        except Exception as e:
            print(f"ERR processing GIF: {e}")
            import traceback
            traceback.print_exc()
            self.frames = [] # Reset frames list on error

    # --- CORRECTED animate METHOD ---
    def animate(self):
        """ Cycles through GIF frames. This is the core animation loop step. """
        # Check if we should continue animating
        if not self._is_running or not self.frames or not self.winfo_exists():
             # If stopped, no frames, or widget destroyed, stop the process.
             self._is_running = False
             if self._job:
                 self.after_cancel(self._job)
                 self._job = None
             return

        # Move to the next frame index
        self.idx = (self.idx + 1) % len(self.frames)

        try:
            # Update the label's image to the next frame
            self.config(image=self.frames[self.idx])

            # Schedule the *next* call to this animate method after the delay
            # This creates the loop.
            self._job = self.after(self.delay, self.animate)

        except tk.TclError:
             # This often happens if the window is closed while animation is pending
             print("TclError during animation (widget likely destroyed). Stopping animation.")
             self._is_running = False
             if self._job: self.after_cancel(self._job); self._job = None
        except Exception as e:
            print(f"Error during GIF animation step: {e}")
            self._is_running = False # Stop on other errors
            if self._job: self.after_cancel(self._job); self._job = None
    # --- END animate CORRECTION ---

    def start_animation(self):
        """ Starts the animation loop if frames are loaded and it's not already running. """
        if self.frames and not self._is_running:
            print("Starting GIF animation loop...")
            self._is_running = True
            # Cancel any potentially lingering job before starting fresh
            if self._job:
                self.after_cancel(self._job)
                self._job = None
            # Call animate for the first time to kick off the loop
            self.animate()

    def stop_animation(self):
        """ Stops the animation loop gracefully. """
        if self._is_running: # Only print if it was actually running
             print("Stopping GIF animation loop...")
        self._is_running = False # Signal the animate loop to stop scheduling itself
        # Cancel the *next* scheduled job, if one exists
        if self._job:
            self.after_cancel(self._job)
            self._job = None

    def destroy(self):
        """ Cleans up resources when the widget is destroyed. """
        print("Destroying AnimatedGIFLabel...")
        self.stop_animation() # Ensure animation is stopped
        self.frames = [] # Release image data references
        self.config(image='') # Clear current image from label
        self._original_gif_img = None # Release PIL image reference
        super().destroy() # Call parent destroy method


# ===============================================
# Background Voice Loop & UI Start/Management (Syntax Fixed)
# ===============================================
stop_voice_loop = threading.Event(); root_window_ref = None
def voice_loop(shiva_instance):
    """ The main loop for listening and processing commands in a background thread. """
    global root_window_ref; print("Starting voice loop thread..."); loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
    while not stop_voice_loop.is_set():
        try:
            if not root_window_ref or not root_window_ref.winfo_exists():
                if not stop_voice_loop.is_set(): print("Root window closed. Exiting voice loop."); break
        except Exception as win_check_e:
            if not stop_voice_loop.is_set(): print(f"Win check error: {win_check_e}. Exiting loop."); break
        try:
            command = loop.run_until_complete(shiva_instance.take_command())
            if stop_voice_loop.is_set(): break
            if command and command != "none": loop.run_until_complete(shiva_instance.process_command(command));
            time.sleep(0.1)
        except RuntimeError as e:
             if "cannot schedule" in str(e) or "closed" in str(e):
                 if not stop_voice_loop.is_set(): print("Asyncio loop shutdown. Exiting voice loop."); break
             else: print(f"RuntimeError in voice loop: {e}"); time.sleep(1)
        except Exception as e: print(f"Unexpected Error in voice loop: {e}"); import traceback; traceback.print_exc(); time.sleep(2)
    print("Voice loop thread finished.");
    try: # Corrected loop closing block
        if not loop.is_closed():
             loop.close(); print("Voice thread asyncio loop closed.")
        else: print("Voice thread asyncio loop was already closed.")
    except Exception as loop_close_e: print(f"Error closing voice loop's loop: {loop_close_e}")
def on_close():
    global root_window_ref; print("on_close triggered.");
    if not stop_voice_loop.is_set(): print("Signaling voice loop stop..."); stop_voice_loop.set()
    if root_window_ref:
        try:
            for widget in root_window_ref.winfo_children():
                if isinstance(widget, AnimatedGIFLabel): print("Stopping GIF anim..."); widget.stop_animation(); break
            print("Destroying Tkinter root..."); root_window_ref.destroy(); root_window_ref = None; print("Tkinter root destroyed.")
        except tk.TclError as e: print(f"TclError during close: {e}"); root_window_ref = None
        except Exception as e: print(f"Error during on_close: {e}"); root_window_ref = None
    else: print("Root window ref already gone in on_close.")
def start_ui(shiva):
    global root_window_ref; print("Creating Tkinter root..."); root = tk.Tk(); root.title("Shiva Voice Assistant"); root.attributes('-fullscreen', True); root.configure(bg="black"); root_window_ref = root;
    def exit_fullscreen(event=None): print("Exiting fullscreen."); root.attributes('-fullscreen', False)
    root.bind('<Escape>', exit_fullscreen); bg_label = AnimatedGIFLabel(root, gif_path=DEFAULT_GIF_PATH, delay=90, overlay_alpha=GIF_OVERLAY_ALPHA); bg_label.place(x=0, y=0, relwidth=1, relheight=1); bg_label.lower();
    print("Starting voice loop thread..."); voice_thread = threading.Thread(target=voice_loop, args=(shiva,), daemon=True); voice_thread.start(); root.protocol("WM_DELETE_WINDOW", on_close);
    print("Starting Tkinter mainloop...");
    try: root.mainloop()
    except KeyboardInterrupt: print("\nCtrl+C in mainloop."); on_close()
    finally: # Corrected finally block indentation
        print("Tkinter mainloop finished.")
        if not stop_voice_loop.is_set():
            print("Ensuring voice loop stop signal is set post-mainloop.")
            stop_voice_loop.set()

# ===============================================
# Main Execution Block (Unchanged)
# ===============================================
async def run_app(): shiva = Shiva(); await shiva.greet(); start_ui(shiva)
if __name__ == "__main__":
    print("\n========================================"); print("   Shiva Voice Assistant - Starting Up  "); print("========================================")
    if os.name == 'nt': asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    # --- Pre-run Checks / Info ---
    # Check status based on hardcoded key config
    if not google_ai_configured: print("\n*** NOTICE: Google AI SDK config failed (check hardcoded API Key/Permissions). AI commands likely fail. ***\n")
    elif not ai_model_loaded: print("\n*** NOTICE: Google AI Model loading failed (check model name/key permissions). AI commands may fail. ***\n")
    else: print("\n*** Google AI appears configured and ready. It will answer unrecognized commands. ***\n") # Updated message
    if not os.path.exists(DEFAULT_GIF_PATH): print(f"\n*** WARNING: GIF not found: {DEFAULT_GIF_PATH} ***\n*** Background animation will fail. ***\n")
    # --- Run ---
    try: asyncio.run(run_app())
    except KeyboardInterrupt: print("\nCtrl+C detected. Exiting.")
    except Exception as e: print(f"\n--- FATAL ERROR ---"); print(f"Error: {e}"); import traceback; print("\n--- Traceback ---"); traceback.print_exc(); print("-----------------\n"); os._exit(1)
    finally: print("========================================"); print("   Shiva Voice Assistant - Shut Down    "); print("========================================")

# =============================================================================