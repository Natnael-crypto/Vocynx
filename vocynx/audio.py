import sounddevice as sd


def get_available_microphones():
    """Returns a list of input audio devices."""
    devices = sd.query_devices()
    mics = []
    
    for idx, d in enumerate(devices):
        if d['max_input_channels'] > 0:
            mics.append(d['name'])
            
    # Always provide a fallback
    if "Default Microphone" not in mics and len(mics) > 0:
        mics.insert(0, "Default Microphone")
        
    return list(dict.fromkeys(mics))  # Remove duplicates keeping order

def get_device_index(device_name):
    """Gets the sounddevice index for a given device name."""
    if device_name == "Default Microphone":
        return sd.default.device[0] # [input_device, output_device]
        
    devices = sd.query_devices()
    for idx, d in enumerate(devices):
        if d['name'] == device_name and d['max_input_channels'] > 0:
            return idx
            
    return sd.default.device[0] # Fallback
