import wave
import math
import struct
import os

def create_loud_beep(filename, freq=440, duration=1.0, sample_rate=44100):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        num_samples = int(duration * sample_rate)
        for i in range(num_samples):
            t = i / float(sample_rate)
            val = math.sin(2.0 * math.pi * freq * t) * 32000.0 
            packed_value = struct.pack('h', int(val))
            wav_file.writeframes(packed_value)

create_loud_beep('d:/Project/Vocynx/vocynx/assets/start_rec.wav')
