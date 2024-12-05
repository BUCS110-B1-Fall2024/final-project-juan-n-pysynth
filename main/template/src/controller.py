import pygame
import numpy as np
from .view import WaveformVisualizer, Slider, Display
from .model import MidiProcessor

class SynthesizerAppController:
    def __init__(self):
        """"
        Initialization function for the controller class  
        """
        pygame.init()
        # Screen dimensions
        self.screen_width = 800
        self.screen_height = 1000
        slider_width = 300
        slider_x = (self.screen_width - slider_width) // 2  # Center horizontally

        # Set up display
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.display = Display(self.screen)
        pygame.display.set_caption("Synthesizer Interface")
        
        # Initialize the processor
        self.processor = MidiProcessor()
        self.key_to_note = self.processor.key_to_note
        self.note_to_index = {note: i for i, note in enumerate(self.key_to_note.values())}

        # Define sliders
        self.wavetype_slider = Slider(slider_x, 30, slider_width, 20, 0, 4, 0, "Wave Type")
        self.frequency_slider = Slider(slider_x, 80, slider_width, 20, 20, 2000, 440, "Frequency")
        self.amplitude_slider = Slider(slider_x, 130, slider_width, 20,-1000, 1000, 0.2, "Volume")
        self.duration_slider = Slider(slider_x, 180, slider_width, 20,0.01, 2, 0.5, "Duration")
        self.global_volume_slider = Slider(slider_x, 230, slider_width, 20, 0, 1, 0.2, "Global Volume")

        # Load and scale the piano image
        image_path = "/Users/jnaran/Documents/FinalProject/main/template/assets/Pixel Piano 1.0 Sprite/88 Keys Pianos/Piano1.png"
        self.piano_image = pygame.image.load(image_path)
        self.piano_image = pygame.transform.scale(self.piano_image, (600, 200))
        self.piano_rect = self.piano_image.get_rect(center=(self.screen_width // 2, self.screen_height - 300))
        
    def run_synth(self):
        """"
        Main loop for our Pygame Program
        """
        running = True
        generated_waveform = np.zeros(41000)
        self.display.display_tutorial_message()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self.processor.active_keys.add(event.key)
                    generated_waveform = self.processor.play_notes()
                
                elif event.type == pygame.KEYUP:
                    if event.key in self.processor.active_keys:
                        self.processor.active_keys.remove(event.key)

                # Handle slider events
                for slider in [self.wavetype_slider, self.frequency_slider, self.amplitude_slider, self.duration_slider, self.global_volume_slider]:
                    slider.handle_event(event)

            # Get and set synthesizer parameters from sliders
            wave_type = ['sine', 'square', 'triangle', 'sawtooth'][int(self.wavetype_slider.value)]
            frequency = self.frequency_slider.value
            amplitude = self.amplitude_slider.value
            duration = self.duration_slider.value
            global_volume = self.global_volume_slider.value

            self.processor.set_parameters(wave_type, frequency, amplitude, duration)
            self.processor.play_notes(global_volume=global_volume)

            # Clear and redraw screen
            self.screen.fill((128, 128, 255))
            self.wavetype_slider.draw(self.screen)
            self.frequency_slider.draw(self.screen)
            self.amplitude_slider.draw(self.screen)
            self.duration_slider.draw(self.screen)
            self.global_volume_slider.draw(self.screen)
            self.screen.blit(self.piano_image, self.piano_rect.topleft)


            visualizer_rect = pygame.Rect(50, 400, 700, 200)
            pygame.draw.rect(self.screen, (0, 0, 0), visualizer_rect)  # Black background for waveform area

            WaveformVisualizer.visualize_waveform_pygame(self.screen.subsurface(visualizer_rect), generated_waveform)

            pygame.display.flip()

        pygame.quit()