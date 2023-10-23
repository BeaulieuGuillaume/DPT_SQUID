
# Single QUA script generated at 2023-09-02 00:31:09.229739
# QUA library version: 1.0.1

from qm.qua import *

with program() as prog:
    v1 = declare(int, )
    v2 = declare(int, )
    v3 = declare(fixed, )
    v4 = declare(fixed, )
    v5 = declare(int, )
    wait((4+(0*(Cast.to_int(v3)+Cast.to_int(v4)))), "resonator")
    update_frequency("resonator", 150000000.0, "Hz", False)
    update_frequency("fluxline", 100000000.0, "Hz", False)
    play("pumping"*amp(0), "fluxline")
    wait(100000, "resonator")
    with for_(v1,0,(v1<15000000),(v1+1)):
        measure("fake_readout", "resonator", None, dual_demod.full("cos", "out1", "sin", "out2", v3), dual_demod.full("minus_sin", "out1", "cos", "out2", v4))
        r1 = declare_stream()
        save(v3, r1)
        r2 = declare_stream()
        save(v4, r2)
        wait(16, )
        with if_((v1==14999999)):
            wait(500, )
            ramp_to_zero("fluxline")
    play("pumping"*amp(0), "fluxline")
    wait(100000, "resonator")
    with for_(v1,0,(v1<15000000),(v1+1)):
        measure("fake_readout", "resonator", None, dual_demod.full("cos", "out1", "sin", "out2", v3), dual_demod.full("minus_sin", "out1", "cos", "out2", v4))
        save(v3, r1)
        save(v4, r2)
        wait(16, )
        with if_((v1==14999999)):
            wait(500, )
            ramp_to_zero("fluxline")
    with stream_processing():
        r1.with_timestamps().save_all("I")
        r2.with_timestamps().save_all("Q")


config = {
    'version': 1,
    'controllers': {
        'con1': {
            'analog_outputs': {
                '1': {
                    'offset': -0.0030517578125,
                },
                '2': {
                    'offset': 0.0526123046875,
                },
                '3': {
                    'offset': -0.2633056640625,
                },
                '4': {
                    'offset': 0.0357666015625,
                },
                '5': {
                    'offset': 0.0,
                },
                '6': {
                    'offset': 0.0,
                },
                '7': {
                    'offset': 0.0,
                },
                '8': {
                    'offset': 0.0,
                },
                '9': {
                    'offset': 0.0,
                },
                '10': {
                    'offset': 0.0,
                },
            },
            'digital_outputs': {
                '1': {},
                '2': {},
                '3': {},
                '4': {},
                '5': {},
            },
            'analog_inputs': {
                '1': {
                    'offset': 0,
                },
                '2': {
                    'offset': 0,
                },
            },
        },
    },
    'elements': {
        'resonator': {
            'mixInputs': {
                'I': ('con1', 1),
                'Q': ('con1', 2),
                'lo_frequency': 4200000000.0,
                'mixer': 'octave_octave1_1',
            },
            'intermediate_frequency': 100000000.0,
            'operations': {
                'cw': 'const',
                'fake_readout': 'zero_pulse',
            },
            'digitalInputs': {
                'switch': {
                    'port': ('con1', 1),
                    'delay': 0,
                    'buffer': 0,
                },
            },
            'outputs': {
                'out1': ('con1', 1),
                'out2': ('con1', 2),
            },
            'time_of_flight': 24,
            'smearing': 0,
        },
        'fluxline': {
            'mixInputs': {
                'I': ('con1', 3),
                'Q': ('con1', 4),
                'lo_frequency': 8600000000.0,
                'mixer': 'octave_octave1_2',
            },
            'intermediate_frequency': 99500000.0,
            'hold_offset': {
                'duration': 5000,
            },
            'operations': {
                'pumping': 'twoPhoton',
            },
            'digitalInputs': {
                'switch': {
                    'port': ('con1', 3),
                    'delay': 0,
                    'buffer': 0,
                },
            },
        },
    },
    'pulses': {
        'const': {
            'operation': 'measurement',
            'length': 2000,
            'waveforms': {
                'I': 'const_wf',
                'Q': 'zero_wf',
            },
            'integration_weights': {
                'cos': 'cosine_weights',
                'sin': 'sine_weights',
                'minus_sin': 'minus_sine_weights',
            },
            'digital_marker': 'ON',
        },
        'zero_pulse': {
            'operation': 'measurement',
            'length': 2000,
            'waveforms': {
                'I': 'zero_wf',
                'Q': 'zero_wf',
            },
            'integration_weights': {
                'cos': 'cosine_weights',
                'sin': 'sine_weights',
                'minus_sin': 'minus_sine_weights',
            },
            'digital_marker': 'ON',
        },
        'twoPhoton': {
            'operation': 'measurement',
            'length': 10000,
            'waveforms': {
                'I': 'twoPhoton_wf',
                'Q': 'zero_wf',
            },
            'integration_weights': {
                'cos': 'cosine_weights',
                'sin': 'sine_weights',
                'minus_sin': 'minus_sine_weights',
            },
            'digital_marker': 'ON',
        },
    },
    'waveforms': {
        'zero_wf': {
            'type': 'constant',
            'sample': 0.0,
        },
        'const_wf': {
            'type': 'constant',
            'sample': 0.125,
        },
        'twoPhoton_wf': {
            'type': 'constant',
            'sample': 0.185,
        },
        'readout_wf': {
            'type': 'constant',
            'sample': 0.125,
        },
    },
    'digital_waveforms': {
        'ON': {
            'samples': [(1, 0)],
        },
        'OFF': {
            'samples': [(0, 0)],
        },
    },
    'integration_weights': {
        'cosine_weights': {
            'cosine': [(1.0, 2000)],
            'sine': [(0.0, 2000)],
        },
        'sine_weights': {
            'cosine': [(0.0, 2000)],
            'sine': [(1.0, 2000)],
        },
        'minus_sine_weights': {
            'cosine': [(0.0, 2000)],
            'sine': [(-1.0, 2000)],
        },
    },
    'mixers': {
        'octave_octave1_1': [{'intermediate_frequency': 100000000, 'lo_frequency': 4200000000, 'correction': [0.9954495579004288, 0.09542691707611084, 0.09213101863861084, 1.0310608074069023]}],
        'octave_octave1_2': [{'intermediate_frequency': 99500000, 'lo_frequency': 8600000000, 'correction': [1.0096100196242332, -0.11023616790771484, -0.10852718353271484, 1.0255084112286568]}],
    },
}

loaded_config = {
    'version': 1,
    'controllers': {
        'con1': {
            'type': 'opx1',
            'analog_outputs': {
                '2': {
                    'offset': 0.0526123046875,
                    'delay': 0,
                    'shareable': False,
                    'filter': {
                        'feedforward': [],
                        'feedback': [],
                    },
                },
                '1': {
                    'offset': -0.0030517578125,
                    'delay': 0,
                    'shareable': False,
                    'filter': {
                        'feedforward': [],
                        'feedback': [],
                    },
                },
                '7': {
                    'offset': 0.0,
                    'delay': 0,
                    'shareable': False,
                    'filter': {
                        'feedforward': [],
                        'feedback': [],
                    },
                },
                '10': {
                    'offset': 0.0,
                    'delay': 0,
                    'shareable': False,
                    'filter': {
                        'feedforward': [],
                        'feedback': [],
                    },
                },
                '6': {
                    'offset': 0.0,
                    'delay': 0,
                    'shareable': False,
                    'filter': {
                        'feedforward': [],
                        'feedback': [],
                    },
                },
                '4': {
                    'offset': 0.0357666015625,
                    'delay': 0,
                    'shareable': False,
                    'filter': {
                        'feedforward': [],
                        'feedback': [],
                    },
                },
                '8': {
                    'offset': 0.0,
                    'delay': 0,
                    'shareable': False,
                    'filter': {
                        'feedforward': [],
                        'feedback': [],
                    },
                },
                '9': {
                    'offset': 0.0,
                    'delay': 0,
                    'shareable': False,
                    'filter': {
                        'feedforward': [],
                        'feedback': [],
                    },
                },
                '3': {
                    'offset': -0.2633056640625,
                    'delay': 0,
                    'shareable': False,
                    'filter': {
                        'feedforward': [],
                        'feedback': [],
                    },
                },
                '5': {
                    'offset': 0.0,
                    'delay': 0,
                    'shareable': False,
                    'filter': {
                        'feedforward': [],
                        'feedback': [],
                    },
                },
            },
            'analog_inputs': {
                '1': {
                    'offset': 0.0,
                    'gain_db': 0,
                    'shareable': False,
                },
                '2': {
                    'offset': 0.0,
                    'gain_db': 0,
                    'shareable': False,
                },
            },
            'digital_outputs': {
                '5': {
                    'shareable': False,
                },
                '4': {
                    'shareable': False,
                },
                '1': {
                    'shareable': False,
                },
                '3': {
                    'shareable': False,
                },
                '2': {
                    'shareable': False,
                },
            },
        },
    },
    'oscillators': {},
    'elements': {
        'fluxline': {
            'digitalInputs': {
                'switch': {
                    'delay': 0,
                    'buffer': 0,
                    'port': ('con1', 3),
                },
            },
            'digitalOutputs': {},
            'intermediate_frequency': 99500000,
            'operations': {
                'pumping': 'twoPhoton',
            },
            'mixInputs': {
                'I': ('con1', 3),
                'Q': ('con1', 4),
                'mixer': 'octave_octave1_2',
                'lo_frequency': 8600000000,
            },
            'hold_offset': {
                'duration': 5000,
            },
        },
        'resonator': {
            'digitalInputs': {
                'switch': {
                    'delay': 0,
                    'buffer': 0,
                    'port': ('con1', 1),
                },
            },
            'digitalOutputs': {},
            'outputs': {
                'out1': ('con1', 1),
                'out2': ('con1', 2),
            },
            'time_of_flight': 24,
            'smearing': 0,
            'intermediate_frequency': 100000000,
            'operations': {
                'cw': 'const',
                'fake_readout': 'zero_pulse',
            },
            'mixInputs': {
                'I': ('con1', 1),
                'Q': ('con1', 2),
                'mixer': 'octave_octave1_1',
                'lo_frequency': 4200000000,
            },
        },
    },
    'pulses': {
        'zero_pulse': {
            'length': 2000,
            'waveforms': {
                'I': 'zero_wf',
                'Q': 'zero_wf',
            },
            'digital_marker': 'ON',
            'integration_weights': {
                'sin': 'sine_weights',
                'cos': 'cosine_weights',
                'minus_sin': 'minus_sine_weights',
            },
            'operation': 'measurement',
        },
        'twoPhoton': {
            'length': 10000,
            'waveforms': {
                'Q': 'zero_wf',
                'I': 'twoPhoton_wf',
            },
            'digital_marker': 'ON',
            'integration_weights': {
                'minus_sin': 'minus_sine_weights',
                'sin': 'sine_weights',
                'cos': 'cosine_weights',
            },
            'operation': 'measurement',
        },
        'const': {
            'length': 2000,
            'waveforms': {
                'Q': 'zero_wf',
                'I': 'const_wf',
            },
            'digital_marker': 'ON',
            'integration_weights': {
                'minus_sin': 'minus_sine_weights',
                'sin': 'sine_weights',
                'cos': 'cosine_weights',
            },
            'operation': 'measurement',
        },
    },
    'waveforms': {
        'readout_wf': {
            'sample': 0.125,
            'type': 'constant',
        },
        'zero_wf': {
            'sample': 0.0,
            'type': 'constant',
        },
        'twoPhoton_wf': {
            'sample': 0.185,
            'type': 'constant',
        },
        'const_wf': {
            'sample': 0.125,
            'type': 'constant',
        },
    },
    'digital_waveforms': {
        'OFF': {
            'samples': [(0, 0)],
        },
        'ON': {
            'samples': [(1, 0)],
        },
    },
    'integration_weights': {
        'sine_weights': {
            'cosine': [(0.0, 2000)],
            'sine': [(1.0, 2000)],
        },
        'minus_sine_weights': {
            'cosine': [(0.0, 2000)],
            'sine': [(-1.0, 2000)],
        },
        'cosine_weights': {
            'cosine': [(1.0, 2000)],
            'sine': [(0.0, 2000)],
        },
    },
    'mixers': {
        'octave_octave1_2': [{'intermediate_frequency': 99500000.0, 'lo_frequency': 8600000000.0, 'correction': [1.0096100196242332, -0.11023616790771484, -0.10852718353271484, 1.0255084112286568]}],
        'octave_octave1_1': [{'intermediate_frequency': 100000000.0, 'lo_frequency': 4200000000.0, 'correction': [0.9954495579004288, 0.09542691707611084, 0.09213101863861084, 1.0310608074069023]}],
    },
}


