import alsaaudio as aa
import math

def get_mic(sample_time: float = 1.0, sample_rate: int = 44100) -> aa.PCM:
    assert sample_time > 0.0
    assert sample_rate > 0

    devices = aa.pcms(pcmtype=aa.PCM_CAPTURE)
    valid_devices = [dev for dev in devices if 'plughw' in dev]

    if len(valid_devices) == 0:
        raise IOError("No microphone detected by alsaaudio")
    elif len(valid_devices) > 1:
        raise IOError("Multiple microphones detected, unable to proceed")

    device = valid_devices[0]  # from above, len(valid_devices) == 1
    return aa.PCM(type=aa.PCM_CAPTURE,
                  mode=aa.PCM_NONBLOCK,
                  device=device,
                  channels=1,
                  rate=sample_rate,
                  format=aa.PCM_FORMAT_S16_LE,  # LINEAR16
                  periodsize=int(sample_rate*sample_time)
                 )

def get_audio(mic: aa.PCM) -> bytes:
    """Return a period"""
    read = (0, b'')
    while read[0] == 0:
        read = mic.read()
    assert read[0] > 0
    return read[1]
