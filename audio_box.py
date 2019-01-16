import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from morse import morse_encode


class AudioBOX:
    sample_rate = None
    stream = None
    p = None

    @staticmethod
    def init(sample_rate=44100):
        AudioBOX.sample_rate = sample_rate
        AudioBOX.p = pyaudio.PyAudio()
        AudioBOX.stream = AudioBOX.p.open(format=pyaudio.paInt32,
                                          channels=1,
                                          rate=AudioBOX.sample_rate,
                                          output=True)

    @staticmethod
    def beep(freq, duration, volume=1.0):
        stream = sine_stream_gen(freq, duration, volume)
        AudioBOX.stream.write(stream, num_frames=len(stream))

    @staticmethod
    def sine_stream_gen(freq, duration, volume=1.0):
        T = duration
        t = np.arange(0, T, 1 / AudioBOX.sample_rate)
        x = 0.5 * np.sin(2 * np.pi * freq * t)
        x = (x * (2 ** 31)).astype(np.int32)
        return x

    @staticmethod
    def fade_sample(sample, time_s):
        n_samples = time_s * AudioBOX.sample_rate
        ds = 0
        i = 0
        while ds < 1.0 and i < len(sample):
            sample[i] *= ds
            sample[-i - 1] *= ds
            ds += 1 / n_samples
            i += 1

    @staticmethod
    def plot_sample(x):
        tm = np.linspace(0, len(x), len(x), endpoint=True)
        plt.plot(tm, x)
        plt.show()

    @staticmethod
    def play_sample(x):
        AudioBOX.stream.write(x, num_frames=len(x))

    @staticmethod
    def play_morse(text, dot_len=0.15, volume=1.0, freq=300):
        FADE_TIME = 0.006
        dot = AudioBOX.sine_stream_gen(freq, dot_len, volume)
        dash = AudioBOX.sine_stream_gen(freq, 3 * dot_len, volume)
        bit_pause = AudioBOX.sine_stream_gen(0, dot_len, 0)
        char_pause = AudioBOX.sine_stream_gen(0, dot_len, 0)
        pipe_pause = char_pause
        AudioBOX.fade_sample(dot, FADE_TIME)
        AudioBOX.fade_sample(dash, FADE_TIME)
        # AudioAPI.plot_sample(dot)
        # AudioAPI.plot_sample(dash)
        code = morse_encode(text)
        stream = np.array([0])
        for ch in code:
            stream = np.append(stream, {
                '.': dot,
                '-': dash,
                '|': pipe_pause,
                ' ': char_pause
            }[ch])
            stream = np.append(stream, bit_pause)
        AudioBOX.play_sample(stream)

    @staticmethod
    def destroy():
        AudioBOX.stream.stop_stream()
        AudioBOX.stream.close()
        AudioBOX.p.terminate()
