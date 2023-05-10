



pulse_len=1_000_000    #10000   #1_000_000 
pulse_amp=0.125
IF = 0.3195e9
LO = 4e9

#octave lo 250 MHZ

#Flux line 
LO_fluxline=8.6e9    #octave lo 250 MHZ
IF_fluxline=57.6e6   # 0.24299e9

twoPhoton_len=600_000_000   #1_000_000_000  #600_000_000   #600_000_000 #15
twoPhoton_amp=0.125




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
    "elements": {
        
        
        "fluxline": {
            "mixInputs": {
                    "I": ("con1", 3), # fluxline input of the flux line 
                    "Q": ("con1", 4),
                    "lo_frequency": LO_fluxline,
                    "mixer": "octave_octave1_2", # is the rf 2 
                },
            "intermediate_frequency": IF_fluxline,
            "operations": {
                "pumping":"twoPhoton",
            },
                "digitalInputs": {
                "switch": {
                    "port": ("con1", 3),
                    "delay": 600_000_000,  #delay time before sending the trigger once the pulse has been sent. 
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
                    "intermediate_frequency": IF,
                    "lo_frequency": LO,
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