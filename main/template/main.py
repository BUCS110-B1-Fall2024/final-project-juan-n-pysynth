import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from src.controller import SynthesizerAppController

def main():
        
    #Creates an instance of Synthesizer App Controller
    #Mainloop is called
    app =  SynthesizerAppController()
    app.run_synth()

if __name__ == '__main__':
    main()


