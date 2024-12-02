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



class GenerateWaveform:
    #Class to generate different Wave Forms based on parameters
    def __init__(self, frequency, amplitude, duration):
        #Each waveform generated must have a frequency, an amplitude, time, a duration of the audio clip played, and a typical sampling rate for 48 khz
        self.frequency = frequency
        self.amplitude = amplitude
        self.duration = duration
        self.SAMPLING_RATE = 48000
        self.time = np.linspace(0, self.duration, int(self.SAMPLING_RATE * self.duration), endpoint=False)

    def sine_wave(self):
        #Generate a sine wave
        return  self.amplitude * (np.sin(2 * np.pi * self.frequency * self.time))
    
    def triangle_wave(self):
        #Generate a square wave
        return self.amplitude * (4 * abs((self.frequency * self.time) - ((self.frequency * self.time) + (1 // 2))) - 1)  
    
    def square_wave(self): 
        return self.amplitude * np.sign(self.sine_wave())

    def sawtooth_wave(self):
        return self.amplitude * (2 * (self.time % (1/self.frequency) * self.frequency - 1)) 
    

class Audio_Playback:
    def __init__(self,waveform, volume = 0.5, sampling_rate=48000):
        self.volume = volume
        self.sampling_rate = sampling_rate
        self.normalized_waveform =  self._normalize_waveform(waveform)
        
    def _normalize_waveform(self,waveform):
        normalized = waveform / np.max(np.abs(waveform))
        return normalized * self.volume
    

    def play_waveform(self):   #Function to play the audio from any waveform from the Generate Waveform class
        sd.play(self.normalized_waveform, self.sampling_rate)
        sd.wait()
    
    def save_waveform(self, filename):
        waveform_int16 = np.int16(self.normalized_waveform * 32767)
        write(filename, self.sampling_rate, waveform_int16)



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
    @staticmethod
    def midi_to_frequency(note):
        return 440 * (2 ** ((note - 69) / 12))

    def __init__(self):
        self.currently_playing = {}


    @staticmethod
    def play_midi_notes(self, waveform_generator, amplitude=0.5, duration=1, volume=0.2):

        pygame.init()

        key_to_note = {
            pygame.K_a: 60,  # C4
            pygame.K_s: 62,  # D4
            pygame.K_d: 64,  # E4
            pygame.K_f: 65,  # F4
            pygame.K_g: 67,  # G4
            pygame.K_h: 69,  # A4
            pygame.K_j: 71,  # B4
            pygame.K_k: 72,  # C5
        }
        
        print("Press keys A, S, D, F, G, H, J, K to play notes. Press ESC to quit.")

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        running = False
               
                elif event.type == pygame.KEYDOWN:
                    if event.key in key_to_note:
                        note = key_to_note[event.key]
                        frequency = MidiProcessor.midi_to_frequency(note)

                        generator = GenerateWaveform(frequency,amplitude,duration)
                        waveform = waveform_generator(generator)

                        player = Audio_Playback(waveform,volume=volume)
                        player.play_waveform()

                        WaveformVisualizer.visualize_waveform(waveform)
                        WaveformVisualizer.plot_spectrum(waveform)
                        
                elif event.type == pygame.KEYUP:
                    if event.key in key_to_note:
                        sd.stop()
        pygame.quit()



"""
Pygame GUI Steps:

1. Model    

"""
def main():
    frequency = 440
    amplitude = 0.5
    duration = 3

    generator = GenerateWaveform(frequency,amplitude, duration)
    waveform = generator.square_wave()

    player = Audio_Playback(waveform,volume=0.1)
    player.play_waveform()
    player.save_waveform("lowwave.wav")  # Save the waveform as a file
    visualize_waveform(player.normalized_waveform,player.sampling_rate,title="Square Wave Visualizer")

main()