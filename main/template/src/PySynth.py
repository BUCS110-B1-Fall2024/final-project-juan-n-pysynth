import librosa
import pandas
import scipy 
import math
import numpy as np
import sounddevice as sd
import soundfile as sf
from matplotlib import pyplot as plt
from scipy.io.wavfile import write
import mido
from pynput import keyboard
import pygame


#Model class handling the basic generation and parameters of a waveform
class GenerateWaveform:
     #Class to generate different Wave Forms based on parameters
    def __init__(self, frequency, amplitude=0.5, duration=0.5,sample_rate=44100):
        #Each waveform generated must have a frequency, an amplitude, time, a duration of the audio clip played, and a typical sampling rate for 48 khz
        self.frequency = frequency
        self.amplitude = amplitude
        self.duration = duration
        self.sample_rate = sample_rate
        self.samples = int(sample_rate * duration)
        self.time = np.linspace(0, self.duration, self.samples, endpoint=False)

    def sine_wave(self):
        #Generate a sine wave
        return  self.amplitude * (np.sin(2 * np.pi * self.frequency * self.time))
    
    def triangle_wave(self):
        #Generate a square wave
        return self.amplitude * (2 * np.abs(2 * (self.time * self.frequency % 1) - 1) - 1)
        
    def square_wave(self): 
        return self.amplitude * np.sign(self.sine_wave())

    def sawtooth_wave(self):
        return self.amplitude * (2 * (self.time * self.frequency % 1) - 1)
        
    def generate_waveform(self,wave_type):
        waveforms = {
        "sine": self.sine_wave,
        "triangle": self.triangle_wave,
        "square": self.square_wave,
        "sawtooth": self.sawtooth_wave
        }
        if wave_type not in waveforms:
            raise ValueError(f"Unsupported Wave Type {wave_type}")
        waveform = waveforms[wave_type]()
        return self.convert_to_stereo(waveform)

    def convert_to_stereo(self, waveform):
        # Convert mono (1D) waveform to stereo (2D) by duplicating the waveform for both channels
        return np.column_stack((waveform,waveform))

    def get_sound(self,wave_type):
        waveform = self.generate_waveform(wave_type)
        waveform_int16 = np.int16(waveform * 32767)
        sound = pygame.sndarray.make_sound(waveform_int16)
        return sound
    

class AudioPlayback:
    def __init__(self, waveform):
        self.waveform = waveform
        self.sample_rate = 44100

    def play_waveform(self):
        # Convert waveform to 16-bit PCM format
        waveform_int16 = np.int16(self.waveform * 32767)
        
        # Initialize pygame mixer
        try:
            pygame.mixer.init(frequency=self.sample_rate)
        except pygame.error as e:
            print(f"Pygame mixer error: {e}")
        
        # Create a sound object
        sound = pygame.sndarray.make_sound(waveform_int16)
        
        # Play the sound
        sound.play()



class WaveformVisualizer:
    @staticmethod
    def visualize_waveform(waveform, sampling_rate = 48000, title="Waveform Visualizer"):
        time = np.linspace(0, len(waveform) / sampling_rate, num = len(waveform))
        plt.figure(figsize=(10, 4))
        plt.plot(time, waveform, color='blue')
        plt.title(title)
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_spectrum(waveform,sampling_rate=48000):
        
        #Compute Fast Fourier Transform
        spectrum = np.fft.fft(waveform)
        frequency = np.fft.fftfreq(len(waveform), d=1/sampling_rate)

        #Seperate positive and negative frequencies
        positive_frequencies = frequency[:len(frequency)//2]
        magnitude = np.abs(spectrum[:len(spectrum)//2])
        
        # Create the frequency spectrum plot
        plt.figure(figsize=(10, 4))
        plt.plot(positive_frequencies, magnitude, color='red', label='Frequency Spectrum')
        plt.title("Frequency Spectrum")
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Magnitude")
        plt.grid(True)
        plt.tight_layout()
        plt.show()


class MidiProcessor:
    def __init__(self):
        self.active_keys = set()
        self.wave_type = "sine"
        self.amplitude = 0.5
        self.duration = 0.5
        self.key_to_note = {pygame.K_a: 60, pygame.K_s: 62, pygame.K_d: 64, pygame.K_f: 65, pygame.K_g: 67, pygame.K_h: 69, pygame.K_j: 71, pygame.K_k: 72}

    def set_parameters(self, wave_type, amplitude, duration):
        self.wave_type = wave_type
        self.amplitude = amplitude
        self.duration = duration

    def play_notes(self):
        if not self.active_keys:
            return

        waveforms = []
        for key in self.active_keys:
            note = self.key_to_note.get(key, None)
            
            if note is not None:
                frequency = self.midi_to_frequency(note)
            else: 
                frequency = 0 
            generator = GenerateWaveform(frequency, self.amplitude, self.duration)
            waveform = generator.generate_waveform(self.wave_type)
            waveforms.append(waveform)

        combined_waveform = np.sum(waveforms, axis=0)
        if np.max(np.abs(combined_waveform)) != 0:
            combined_waveform /= np.max(np.abs(combined_waveform))

        player = AudioPlayback(combined_waveform)
        player.play_waveform()

    #Normalizing frequency to 12-Tet 
    def midi_to_frequency(self, midi_note):
        return 440.0 * 2**((midi_note - 69) / 12.0)


class SynthesizerApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((400,300))
        pygame.display.set_caption("Synthesizer interface")
        self.processor = MidiProcessor()

    def run_synth(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    self.processor.active_keys.add(event.key)
                    self.processor.play_notes()

                elif event.type == pygame.KEYUP:
                    if event.key in self.processor.active_keys:
                        self.processor.active_keys.remove(event.key)

        pygame.quit()

if __name__ == "__main__":
    app = SynthesizerApp()
    app.run_synth()



