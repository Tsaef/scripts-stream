import cv2
import numpy as np
import pyvirtualcam
import sounddevice as sd
import queue
import time

static_img = cv2.imread("../anim-ressources/static.png")
video = cv2.VideoCapture("../anim-ressources/moving.mp4")

q = queue.Queue()

def audio_callback(indata, frames, time_info, status):
    q.put(indata.copy())
2
samplerate = 16000
sd.InputStream(device=2, channels=1, samplerate=samplerate,  blocksize=420, callback=audio_callback).start()

def is_speaking(threshold=0.0008):
    audio = None
    try:
        while True:
            audio = q.get_nowait()
    except queue.Empty:
        pass

    if audio is not None:
        volume_norm = np.linalg.norm(audio) / len(audio)
        return volume_norm > threshold, volume_norm
    return False, 0.0


with pyvirtualcam.Camera(width=640, height=480, fps=30) as cam:
    print(f"Virtual camera started: {cam.device}")
    last_print = time.time()

    while True:
        speaking, volume = is_speaking()

        if time.time() - last_print > 0.5:
            print(f"Speaking: {speaking} | Volume: {volume:.4f}")
            last_print = time.time()

        if speaking:
            ret, frame = video.read()
            if not ret:
                video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = video.read()
        else:
            frame = static_img.copy()

        frame = cv2.resize(frame, (640, 480))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        cam.send(frame)
        cam.sleep_until_next_frame()