import pygame 
import numpy as np

class AudioPlayback:
    """
    Instantiates Pygame's Mixer and plays the updataed sound from 
    """
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
    def visualize_waveform_pygame(screen, waveform, sampling_rate=41000, window_size=1024):
        screen.fill((30, 30, 30))  # Dark grey background

        width, height = screen.get_size()
        scale = height / 2
        midline = height // 2

        # If waveform is stereo (2D), convert to mono by averaging channels
        if len(waveform.shape) == 2 and waveform.shape[1] == 2:
            waveform = np.mean(waveform, axis=1)  # Average over the second dimension (channels)

        # Normalize waveform to fit vertically on the screen
        max_value = np.max(np.abs(waveform))
        if max_value != 0:
            normalized_waveform = waveform / max_value * scale
        else:
            # If the max value is zero, we avoid dividing by zero by just using a zero array
            normalized_waveform = np.zeros_like(waveform)
    
        points = []
        for i in range(len(normalized_waveform)):  # Make sure we're iterating over normalized_waveform
            x = int(i / len(normalized_waveform) * width)
            
            # Ensure normalized_waveform[i] is a scalar (not an array)
            value = float(normalized_waveform[i])  # This ensures it's a scalar value
                        
            y = int(midline - value)
            points.append((x, y))

        pygame.draw.aalines(screen, (0, 255, 255), False, points)
        pygame.display.update()  # Update only this section of the screen

class Display:
    def __init__(self, screen):
        self.screen = screen
        self.processor = None  # Create an empty variable to lazy import MidiProcesso
        self.font = pygame.font.SysFont("Arial", 24)
    def set_processor(self,processor):
        self.processor = processor

    def display_tutorial_message(self):
        # Tutorial message
        tutorial_text = [
            "Welcome to the Synthesizer Program!",
            "Please turn your volume down to half!",
            "Use the following keys to play notes:",
            "A - C4 | S - D4 | D - E4 | F - F4 | G - G4",
            "H - A4 | J - B4 | K - C5",
            "Press any key to start..."
        ]

        # Clear screen
        self.screen.fill((0, 0, 0))  # Fill the screen with black

        # Render the text and position it
        for i, line in enumerate(tutorial_text):
            text_surface = self.font.render(line, True, (255, 255, 255))  # White text
            text_rect = text_surface.get_rect(center=(400, 300 + i * 40))  # Adjust positions
            self.screen.blit(text_surface, text_rect)

        pygame.display.flip()  # Update the display

        # Wait for a key press to continue
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    waiting = False  # Exit the loop once a key is pressed

    def display_key_and_note(self, key):
        from model import MidiProcessor
        # Access the key_to_name dictionary directly, not as a callable
        key_to_name = self.processor.key_to_name  # Remove the parentheses

        # Get the note name based on the key pressed
        note_name = key_to_name.get(key, "")  # Default to "" if key not found

        # Set up the font and text rendering
        text_surface = self.font.render(f"Key: {pygame.key.name(key)} Note: {note_name}", True, (255, 255, 255))  # White text

        # Position to display the text
        text_rect = text_surface.get_rect(center=(400, 350))  # Adjust the position as needed

        # Draw the text on the screen
        self.screen.blit(text_surface, text_rect)
        pygame.display.flip()


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
        """"
        Following the basic drawing logic for the
        """

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

    