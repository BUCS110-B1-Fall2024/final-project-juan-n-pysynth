import pandas
import scipy 
import math
import numpy as np
import sounddevice as sd
import soundfile as sf
from matplotlib import pyplot as plt
from scipy.io.wavfile import write
import mido
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
    def __init__(self, waveform, global_volume):
        self.waveform = waveform
        self.global_volume = global_volume
        self.sample_rate = 44100

    def play_waveform(self):
        # Convert waveform to 16-bit PCM format
        waveform_int16 = np.int16(self.waveform * 32767)
        
        # Initialize pygame mixer
        try:
            pygame.mixer.init(frequency=self.sample_rate,size=-16,channels=2)
        except pygame.error as e:
            print(f"Pygame mixer error: {e}")
        
        # Create a sound object
        sound = pygame.sndarray.make_sound(waveform_int16)
        sound.set_volume(self.global_volume)
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
        self.amplitude = 0.2
        self.duration = 0.5
        self.frequency = 440
        self.waveform = None
        self.key_to_note = {pygame.K_a: 60, pygame.K_s: 62, pygame.K_d: 64, pygame.K_f: 65, pygame.K_g: 67, pygame.K_h: 69, pygame.K_j: 71, pygame.K_k: 72}

    def set_parameters(self, wave_type,frequency, amplitude, duration):
        self.wave_type = wave_type
        self.frequency = frequency
        self.amplitude = amplitude
        self.duration = duration
        self.generate_waveform()

    def generate_waveform(self):
        self.waveform = GenerateWaveform(self.frequency, self.amplitude)

    def play_notes(self,global_volume=0.2):
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

        player = AudioPlayback(combined_waveform,global_volume)
        player.play_waveform()

    #Normalizing frequency to 12-Tet 
    def midi_to_frequency(self, midi_note):
        return 440.0 * 2**((midi_note - 69) / 12.0)

class Slider:
    def __init__(self, x, y, width, height, min_value, max_value, initial_value, label=""):
        self.rect = pygame.Rect(x, y, width, height)  # Main slider rectangle
        self.slider_rect = pygame.Rect(x, y, width, height)  # Knob rectangle (the part that moves)
        self.slider_rect.width = 20

        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.font = pygame.font.SysFont("Arial", 24)
        self.label = label
        self.dragging = False

    def draw(self, screen):
        # Draw the base slider
        pygame.draw.rect(screen, (200, 200, 200), self.rect)
        # Draw the slider knob
        pygame.draw.rect(screen, (255, 0, 0), self.slider_rect)
        # Label and value display
        label = self.font.render(self.label, True, (0, 0, 0))
        label_pos = self.rect.x - 175
        screen.blit(label, (label_pos, self.rect.y))
        if self.label == "Wave Type":
            wave_names = ["Sine", "Square", "Triangle", "Sawtooth"]
            
            # Round and clamp the value to prevent out-of-range errors
            index = max(0, min(round(self.value), len(wave_names) - 1))
            
            wave_type = wave_names[index]
            text = self.font.render(wave_type, True, (0, 0, 0))
            
            label_x_position = self.rect.x + self.rect.width + 20
            screen.blit(text, (label_x_position, self.rect.y))
        else:
            value_text = self.font.render(f"{self.value:.2f}", True, (0, 0, 0))
            screen.blit(value_text, (self.rect.x + self.rect.width + 10, self.rect.y))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.dragging = True  # Start dragging when clicked inside slider
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False  # Stop dragging when mouse is released

        if event.type == pygame.MOUSEMOTION and self.dragging:
            # Update the slider knob position
            self.slider_rect.x = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.width - self.slider_rect.width))
            # Update the value based on knob position
            self.value = self.min_value + (self.slider_rect.x - self.rect.x) / self.rect.width * (self.max_value - self.min_value)
            self.value = round(self.value, 2)  # Ensure value has two decimal precision


class SynthesizerAppController:
    def __init__(self):
        pygame.init()
        screen_width = 800
        slider_width = 300
        slider_x = (screen_width - slider_width) // 2  # Center horizontally
        slider = Slider(slider_x, 100, slider_width, 20, 0, 3, 0, label="Wave Type")
        self.screen = pygame.display.set_mode((1000, screen_width))
        pygame.display.set_caption("Synthesizer interface")
        
        self.processor = MidiProcessor()

        # Define sliders for wave type, frequency, amplitude, and duration
        self.wavetype_slider = Slider(slider_x, 30, slider_width, 20, 0, 3, 0, "Wave Type")
        self.frequency_slider = Slider(slider_x, 60, slider_width, 20, 20, 2000, 440, "Frequency")
        self.amplitude_slider = Slider(slider_x, 90, slider_width, 20, -1000, 1000, 0.2, "Volume")
        self.duration_slider = Slider(slider_x, 120, slider_width, 20, 0.01, 2, 0.5, "Duration")
        self.global_volume_slider = Slider(slider_x, 150, slider_width, 20, 0, 1, 0.2, "Global Volume")


        self.font = pygame.font.SysFont("Arial", 24)

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

                # Handle events for all sliders
                for slider in [self.wavetype_slider, self.frequency_slider, self.amplitude_slider, self.duration_slider,self.global_volume_slider]:
                    slider.handle_event(event)

            # Set parameters for the synthesizer based on the slider values
            wave_type = ['sine', 'square', 'triangle', 'sawtooth'][int(self.wavetype_slider.value)]  # Ensure only integer values for wave type
            frequency = self.frequency_slider.value
            amplitude = self.amplitude_slider.value
            duration = self.duration_slider.value
            global_volume = self.global_volume_slider.value

            self.processor.set_parameters(wave_type, frequency, amplitude, duration)
            self.processor.play_notes(global_volume=global_volume)

            # Clear and redraw the screen
            self.screen.fill((255, 255, 255))  # Background color
            self.wavetype_slider.draw(self.screen)
            self.frequency_slider.draw(self.screen)
            self.amplitude_slider.draw(self.screen)
            self.duration_slider.draw(self.screen)
            self.global_volume_slider.draw(self.screen)  # Draw the new volume slider


            pygame.display.flip()  # Update the display

        pygame.quit()

if __name__ == "__main__":
    app = SynthesizerAppController()
    app.run_synth()



