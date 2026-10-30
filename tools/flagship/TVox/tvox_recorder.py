try:
    import sounddevice as sd
except Exception:
    sd = None

try:
    from scipy.io import wavfile
except Exception:
    wavfile = None

try:
    import numpy as np
except Exception:
    np = None

import os
import queue

class TVoxRecorder:
    def __init__(self, sample_rate=44100, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.is_recording = False
        self.q = queue.Queue()
        self.stream = None

    def is_available(self):
        return sd is not None and wavfile is not None and np is not None

    def callback(self, indata, frames, time, status):
        if status:
            print(status, flush=True)
        self.q.put(indata.copy())

    def start_recording(self):
        if not self.is_available():
            print("Audio recording libraries (sounddevice/scipy) are not installed.")
            return
        if self.is_recording:
            return

        
        # Clear queue
        while not self.q.empty():
            self.q.get()

        self.is_recording = True
        self.stream = sd.InputStream(
            samplerate=self.sample_rate, 
            channels=self.channels,
            callback=self.callback
        )
        self.stream.start()
        print("Recording started...")

    def stop_recording(self, output_filepath):
        if not self.is_recording or self.stream is None:
            return 0.0

        self.stream.stop()
        self.stream.close()
        self.is_recording = False

        # Collect data
        data_list = []
        while not self.q.empty():
            data_list.append(self.q.get())

        if not data_list:
            return 0.0

        audio_data = np.concatenate(data_list, axis=0)
        
        # Save to file
        os.makedirs(os.path.dirname(os.path.abspath(output_filepath)), exist_ok=True)
        wavfile.write(output_filepath, self.sample_rate, audio_data)
        
        duration = len(audio_data) / self.sample_rate
        print(f"Recording saved to {output_filepath} (Duration: {duration:.2f}s)")
        
        return duration

    def get_wav_duration(self, filepath):
        if wavfile is None:
            return 0.0
        try:
            samplerate, data = wavfile.read(filepath)
            duration = len(data) / samplerate
            return duration
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return 0.0
