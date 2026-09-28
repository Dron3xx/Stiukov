from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
from app.voice.speak import speak


def volume_command(function):
    # Use the default Windows speaker endpoint for all volume commands.
    devices = AudioUtilities.GetSpeakers()
    volume = devices.EndpointVolume
    
    if function == "up":
        current_volume = volume.GetMasterVolumeLevelScalar()
        new_volume = min(current_volume + 0.1, 1.0)
        volume.SetMasterVolumeLevelScalar(new_volume, None)
        speak("Volume up")
        return True

    elif function == "down":
        current_volume = volume.GetMasterVolumeLevelScalar()
        new_volume = max(current_volume - 0.1, 0.0)
        volume.SetMasterVolumeLevelScalar(new_volume, None)
        speak("Volume down")
        return True

    elif function == "unmute":
        volume.SetMute(0, None)
        speak("Unmuting")
        return True

    elif function == "mute":
        volume.SetMute(1, None)
        speak("Muting")
        return True

    return False