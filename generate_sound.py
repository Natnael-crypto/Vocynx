import wave
import math
import struct
import os

def create_modern_beep(filename, freqs_and_durations, sample_rate=44100):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for freq, duration in freqs_and_durations:
            num_samples = int(duration * sample_rate)
            for i in range(num_samples):
                t = i / float(sample_rate)
                # Slower decay to make the sound significantly louder and longer
                envelope = math.exp(-3.0 * t) 
                
                # Sine wave with a 2nd harmonic
                val = math.sin(2.0 * math.pi * freq * t) + 0.3 * math.sin(2.0 * math.pi * (freq * 2) * t)
                
                # Boost amplitude to near maximum 16-bit value
                val *= envelope * 30000.0 
                
                # Ensure value is clamped within 16-bit range
                val = max(-32768, min(32767, val))
                
                packed_value = struct.pack('h', int(val))
                wav_file.writeframes(packed_value)

# Generate a high-tech/modern start sound (two warm ascending notes)
create_modern_beep('d:/Project/Vocynx/vocynx/assets/start_rec.wav', [(523.25, 0.15), (783.99, 0.5)])
