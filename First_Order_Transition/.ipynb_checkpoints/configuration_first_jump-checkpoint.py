



pulse_len= 2000 #2_000_000
pulse_amp=0.125

#octave lo 250 MHZ

#Flux line 
LO_fluxline=8.5e9    #octave lo 250 MHZ #octave lo 250 MHZ
IF_fluxline=0.1959e9       # 0.24299e9

twoPhoton_len= 1000 #2_000_000
twoPhoton_amp=0.125

#Readout 
IF_readout = 0.318e9
LO_readout = 4.2e9


config = {
    "version": 1,
    "controllers": {
        "con1": {
            "analog_outputs": {
                1: {"offset": 0.0},
                2: {"offset": 0.0},
                3: {"offset": 0.0},
                4: {"offset": 0.0},
                5: {"offset": 0.0},
                6: {"offset": 0.0},
                7: {"offset": 0.0},
                8: {"offset": 0.0},
                9: {"offset": 0.0},
                10: {"offset": 0.0},
            },
            "digital_outputs": {
                1: {},
                2: {},
                3: {},
                4: {},
                5: {},
            },
            "analog_inputs": {
                1: {"offset": +0.0},
                2: {"offset": +0.0},
            },
        }
    },
    
    
 ###### Elements #######   
    
    "elements": {
        
        "resonator": {
            "mixInputs": {
                    "I": ("con1", 1), # Input of the resonator going out of the OPX 
                    "Q": ("con1", 2),
                    "lo_frequency": LO_readout,
                    "mixer": "octave_octave1_1", # Mixer connected to the resonator (first mixer of the octave) 
                },
            "intermediate_frequency": IF_readout,
            "operations": {
                "cw": "const",
                "fake_readout": "zero_pulse" #"zero_pulse"
            },
            "digitalInputs": {
                "switch": {
                    "port": ("con1", 1),
                    "delay": 0,
                    "buffer": 0,
                },
            },
            "outputs": {
                "out1": ("con1", 1), # Output of the resonator going into the OPX 
                "out2": ("con1", 2),
            },
            "time_of_flight": 24,
            "smearing": 0,
        },
        
        "fluxline": {
            "mixInputs": {
                    "I": ("con1", 3), # Input of the fluxluine going out of the OPX 
                    "Q": ("con1", 4),
                    "lo_frequency": LO_fluxline,
                    "mixer": "octave_octave1_2", # Mixer connected to the fluxline (second mixer of the octave) 
                },
            "intermediate_frequency": IF_fluxline,
            "operations": {
                "pumping":"twoPhoton", #Only operation is twoPhoton (a pump on the fluxline)
            },
               "digitalInputs": {
                "switch": {
                    "port": ("con1", 3),
                    "delay": 0,
                    "buffer": 0,
                },
            },
        },
        
        
        
    },
     
    "pulses": {
            "const": {
                "operation": "measurement",
                "length": pulse_len,
                "waveforms": {
                    "I": "const_wf",
                    "Q": "zero_wf",
                },
                "integration_weights": {
                "cos": "cosine_weights",
                "sin": "sine_weights",
                "minus_sin": "minus_sine_weights",
            },
                "digital_marker": "ON",
            },
        
          "zero_pulse": {
                "operation": "measurement",
                "length": pulse_len,
                "waveforms": {
                    "I": "zero_wf",
                    "Q": "zero_wf",
                },
                "integration_weights": {
                "cos": "cosine_weights",
                "sin": "sine_weights",
                "minus_sin": "minus_sine_weights",
            },
                "digital_marker": "ON",
            },
        
        
          "twoPhoton": {
                "operation": "measurement",
                "length": twoPhoton_len,
                "waveforms": {
                    "I":  "twoPhoton_wf",
                    "Q": "zero_wf",
                },
                "integration_weights": {
                "cos": "cosine_weights",
                "sin": "sine_weights",
                "minus_sin": "minus_sine_weights",
            },
                "digital_marker": "ON",
            },
        
        
        
        },
    
    
    "waveforms": {
        "zero_wf": {
            "type": "constant",
            "sample": 0.0,
        },
        "const_wf": {
            "type": "constant",
            "sample": pulse_amp,
        },
         "twoPhoton_wf": {
            "type": "constant",
            "sample": twoPhoton_amp,
        },
        "readout_wf": {
            "type": "constant",
            "sample": pulse_amp,
        },
    },
    "digital_waveforms": {
        "ON": {"samples": [(1, 0)]},
        "OFF": {"samples": [(0, 0)]},
    },
    "integration_weights": {
        "cosine_weights": {
            "cosine": [(1.0, pulse_len)],
            "sine": [(0.0, pulse_len)],
        },
        "sine_weights": {
            "cosine": [(0.0, pulse_len)],
            "sine": [(1.0, pulse_len)],
        },
        "minus_sine_weights": {
            "cosine": [(0.0, pulse_len)],
            "sine": [(-1.0, pulse_len)],
        },
        },
    "mixers": {
            "octave_octave1_1": [
                {
                    "intermediate_frequency": IF_readout,
                    "lo_frequency": LO_readout,
                    "correction": (1, 0, 0, 1),
                },
            ],
         "octave_octave1_2": [
                {
                    "intermediate_frequency": IF_fluxline,
                    "lo_frequency": LO_fluxline,
                    "correction": (1, 0, 0, 1),
                },
            ],       
        },
}