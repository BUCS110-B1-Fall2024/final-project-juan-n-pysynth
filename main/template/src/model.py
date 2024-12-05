import numpy as np
import pygame
from view import AudioPlayback

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
        #Generates a square wave
        return self.amplitude * np.sign(self.sine_wave())

    def sawtooth_wave(self):
        #Generaters a sawtooth wwave
        return self.amplitude * (2 * (self.time * self.frequency % 1) - 1)
        
    def generate_waveform(self,wave_type):
        """"
        Method used to update wavetype arguments at runtime
        """
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
        """"
        Generates and normalizes a waveform to int16 and initalizes that sound in the pygame mixer
        """
        waveform = self.generate_waveform(wave_type)
        waveform_int16 = np.int16(waveform * 32767)
        sound = pygame.sndarray.make_sound(waveform_int16)
        return sound
    
class MidiProcessor:
    def __init__(self):
        self.active_keys = set()
        self.wave_type = "sine"
        self.amplitude = 0.2
        self.duration = 0.5
        self.frequency = 440
        self.waveform = None
        self.key_to_note = {pygame.K_a: 60, pygame.K_s: 62, pygame.K_d: 64, pygame.K_f: 65, pygame.K_g: 67, pygame.K_h: 69, pygame.K_j: 71, pygame.K_k: 72}
        self.key_to_name = {
            pygame.K_a: "C4",  # MIDI 60
            pygame.K_s: "D4",  # MIDI 62
            pygame.K_d: "E4",  # MIDI 64
            pygame.K_f: "F4",  # MIDI 65
            pygame.K_g: "G4",  # MIDI 67
            pygame.K_h: "A4",  # MIDI 69
            pygame.K_j: "B4",  # MIDI 71
            pygame.K_k: "C5"   # MIDI 72
        }

    def set_parameters(self, wave_type,frequency, amplitude, duration):
        self.wave_type = wave_type
        self.frequency = frequency
        self.amplitude = amplitude
        self.duration = duration
        self.generate_waveform()

    def generate_waveform(self):
        self.waveform = GenerateWaveform(self.frequency, self.amplitude)

    def play_notes(self, global_volume=0.2):
        """
        Function dedicated to taking in user input data, converting them into midi notes, and passing the corresponding data to the waveform
        """
        if not self.active_keys:
            return np.zeros(41000)  # Return silence if no keys are active

        waveforms = []
        for key in self.active_keys:
            note = self.key_to_note.get(key, None)
            frequency = self.midi_to_frequency(note) if note else 0
            generator = GenerateWaveform(frequency, self.amplitude, self.duration)
            waveform = generator.generate_waveform(self.wave_type)
            waveforms.append(waveform)

        combined_waveform = np.sum(waveforms, axis=0)

        if np.max(np.abs(combined_waveform)) > 0:
            combined_waveform /= np.max(np.abs(combined_waveform))  # Normalize

        combined_waveform *= global_volume
        player = AudioPlayback(combined_waveform, global_volume)
        player.play_waveform()  # Play the audio
        
        return combined_waveform
    
     #Normalizing frequency to 12-Tet musical notes
    def midi_to_frequency(self, midi_note):
        return 440.0 * 2**((midi_note - 69) / 12.0)