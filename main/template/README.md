# PySynth: Interactive Wavetable Synthesizer 
## CS110 B1 Final Project  Fall, 2024 

## Developer
Juan Naranjo

***

## Project Description

PySynthesizer is a simple sound synthesizer made from scratch in Python using Numpy and Pygame. Play around with the parameters and use the keys ASDFGHJK to control the synthesizer!

***    

## GUI Design
### Final Design

![final gui](main/template/assets/PySynthGUI.png)

## Program Design

### Features

1. Parameter: WaveType. Change the waveform equation to whatever one you'd like to be generated
2. Parameter: Frequency. Change the frequency of the generation of the waveform.
3. Parameter: Amplitude/Volume. Change the amplitude and volume of the waveform.
4. Parameter: Duration/ Sustain. CHange how long the sound is played for 
5. Feature: Audio Playback with Keys. Hear back the Audio you've created with the ASDFGHJK Keys!
5. Feature: Waveform Visualization. Visualize how your waveform changes along with the p

### Classes
## View Classes:
- class AudioPlayback: Handles audio playback between pygame and the model
- class WaveformVisualizer: Displays generated waveform from the model
- class Display: Display widgets and other surfaced for pygame
- class Slider: Creates a class for generating sliders to use in parameters
## Model Classes:
- class GenerateWaveform: Calculates the waveform based on user parameters, converts to pygames audio format and transfers data to controller
- class MidiProcessor: Takes in user input from pygame and adjusts parameters in the generate waveform class based on the users input
## Controller Class:
- class SynthesizerAppController: Handles data interactions between model and view classes, runs and maintains the main loop for pygame

## ATP

Test Case 1:
    Description: Change the waveform type from "sine" to "square" and verify the waveform type is updated.
    Steps:
        1. Set the waveform type to "sine".
        2. Verify that the waveform type is "sine".
        3. Change the waveform type to "square".
        4. Verify that the waveform type is updated to "square".
    Expected Outcome:
        The waveform type should successfully switch from "sine" to "square".

Test Case 2:
    Description: Change the frequency of the synth to test if the frequency parameter is updated correctly.
    Steps:
        1. Set the frequency to 440Hz (A4).
        2. Verify that the frequency is set to 440Hz.
        3. Change the frequency to 880Hz (A5).
        4. Verify that the frequency is updated to 880Hz.
    Expected Outcome:
        The frequency should be correctly updated from 440Hz to 880Hz.

Test Case 3:
    Description: Test the change in amplitude and verify the sound output volume change.
    Steps:
        1. Set the amplitude to 0.2.
        2. Verify that the amplitude is set to 0.2.
        3. Change the amplitude to 0.5.
        4. Verify that the amplitude is updated to 0.5.
    Expected Outcome:
        The amplitude should update correctly and correspond to a louder or softer sound.

Test Case 4:
    Description: Test if the synth properly handles the duration of a note, ensuring the sound plays for the correct amount of time.
    Steps:
        1. Set the duration parameter to 0.5 seconds.
        2. Press a key to play a note (e.g., key 'a').
        3. Verify that the note plays for approximately 0.5 seconds before stopping.
        4. Change the duration to 1.0 second.
        5. Press the same key again.
        6. Verify that the note plays for approximately 1.0 second before stopping.
    Expected Outcome:
        The duration of the note should correspond to the set duration value (0.5 seconds and 1.0 second).

Test Case 5:
    Description: Test that changing the amplitude of the synth correctly scales the volume.
    Steps:
        1. Set the amplitude to 0.1 (very quiet).
        2. Press a key to play a note (e.g., key 'f').
        3. Verify that the note plays at a low volume.
        4. Change the amplitude to 1.0 (maximum volume).
        5. Press the same key again.
        6. Verify that the note plays at a significantly louder volume.
    Expected Outcome:
        The amplitude change should result in a noticeable difference in volume, from quiet (0.1) to loud (1.0).
