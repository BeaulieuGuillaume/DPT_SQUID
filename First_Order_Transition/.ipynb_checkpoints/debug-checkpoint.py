
# Single QUA script generated at 2023-04-02 22:11:52.328101
# QUA library version: 1.0.1

from qm.qua import *

with program() as prog:
    v1 = declare(int, )
    v2 = declare(int, )
    a1 = declare(fixed, size=5000)
    a2 = declare(fixed, size=5000)
    a3 = declare(fixed, size=5000)
    a4 = declare(fixed, size=5000)
    a5 = declare(fixed, size=5000)
    a6 = declare(fixed, size=5000)
    measure("fake_readout", "resonator", None, demod.sliced("cos", a1, 5, "out1"), demod.sliced("sin", a3, 5, "out2"), demod.sliced("minus_sin", a2, 5, "out1"), demod.sliced("cos", a4, 5, "out2"))
    with for_(v2,0,(v2<5000),(v2+1)):
        assign(a5[v2], (a1[v2]+a3[v2]))
        assign(a6[v2], (a2[v2]+a4[v2]))
        r1 = declare_stream()
        save(a5[v2], r1)
        r2 = declare_stream()
        save(a6[v2], r2)
    with stream_processing():
        r1.save_all("I")
        r2.save_all("Q")


config = {
    'version': 1,
    'controllers': {
        'con1': {
            'analog_outputs': {
                '1': {
                    'offset': 0.0,
                },
                '2': {
                    'offset': 0.0,
                },
                '3': {
                    'offset': -0.107421875,
                },
                '4': {
                    'offset': -0.0186767578125,
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
                    'offset': 0.0,
                },
                '2': {
                    'offset': 0.0,
                },
            },
        },
    },
    'elements': {
        'resonator': {
            'mixInputs': {
                'I': ('con1', 1),
                'Q': ('con1', 2),
                'lo_frequency': 4000000000.0,
                'mixer': 'octave_octave1_1',
            },
            'intermediate_frequency': 318000000.0,
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
                'lo_frequency': 8400000000.0,
                'mixer': 'octave_octave1_2',
            },
            'intermediate_frequency': 236000000.0,
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
            'length': 10000,
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
            'length': 100000,
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
            'length': 2000,
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
            'sample': 0.125,
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
            'cosine': [(1.0, 100000)],
            'sine': [(0.0, 100000)],
        },
        'sine_weights': {
            'cosine': [(0.0, 100000)],
            'sine': [(1.0, 100000)],
        },
        'minus_sine_weights': {
            'cosine': [(0.0, 100000)],
            'sine': [(-1.0, 100000)],
        },
    },
    'mixers': {
        'octave_octave1_1': [
            {'intermediate_frequency': 242990000, 'lo_frequency': 8400000000, 'correction': [1.0320636592805386, -0.16502943634986877, -0.16310682892799377, 1.04422901943326]},
            {'intermediate_frequency': 262000000, 'lo_frequency': 8400000000, 'correction': [1.0, 0.0, 0.0, 1.0]},
            {'intermediate_frequency': 318000000.0, 'lo_frequency': 4000000000.0, 'correction': (1, 0, 0, 1)},
        ],
        'octave_octave1_2': [
            {'intermediate_frequency': 262000000, 'lo_frequency': 8400000000, 'correction': [1.0125585980713367, -0.15338531136512756, -0.14751067757606506, 1.0528838895261288]},
            {'intermediate_frequency': 235500000, 'lo_frequency': 8400000000, 'correction': [1.0102465897798538, -0.14740926027297974, -0.14176350831985474, 1.0504798032343388]},
            {'intermediate_frequency': 236000000, 'lo_frequency': 8400000000, 'correction': [1.0102465897798538, -0.14740926027297974, -0.14176350831985474, 1.0504798032343388]},
        ],
    },
}

loaded_config = {
    'version': 1,
    'controllers': {
        'con1': {
            'type': 'opx1',
            'analog_outputs': {
                '6': {
                    'offset': 0.0,
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
                '10': {
                    'offset': 0.0,
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
                '9': {
                    'offset': 0.0,
                    'delay': 0,
                    'shareable': False,
                    'filter': {
                        'feedforward': [],
                        'feedback': [],
                    },
                },
                '1': {
                    'offset': 0.0,
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
                '2': {
                    'offset': 0.0,
                    'delay': 0,
                    'shareable': False,
                    'filter': {
                        'feedforward': [],
                        'feedback': [],
                    },
                },
                '4': {
                    'offset': -0.0186767578125,
                    'delay': 0,
                    'shareable': False,
                    'filter': {
                        'feedforward': [],
                        'feedback': [],
                    },
                },
                '3': {
                    'offset': -0.107421875,
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
                '2': {
                    'shareable': False,
                },
                '3': {
                    'shareable': False,
                },
                '1': {
                    'shareable': False,
                },
                '4': {
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
            'intermediate_frequency': 236000000,
            'operations': {
                'pumping': 'twoPhoton',
            },
            'mixInputs': {
                'I': ('con1', 3),
                'Q': ('con1', 4),
                'mixer': 'octave_octave1_2',
                'lo_frequency': 8400000000,
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
            'intermediate_frequency': 318000000,
            'operations': {
                'fake_readout': 'zero_pulse',
                'cw': 'const',
            },
            'mixInputs': {
                'I': ('con1', 1),
                'Q': ('con1', 2),
                'mixer': 'octave_octave1_1',
                'lo_frequency': 4000000000,
            },
        },
    },
    'pulses': {
        'twoPhoton': {
            'length': 2000,
            'waveforms': {
                'I': 'twoPhoton_wf',
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
        'const': {
            'length': 10000,
            'waveforms': {
                'I': 'const_wf',
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
        'zero_pulse': {
            'length': 100000,
            'waveforms': {
                'I': 'zero_wf',
                'Q': 'zero_wf',
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
        'const_wf': {
            'sample': 0.125,
            'type': 'constant',
        },
        'twoPhoton_wf': {
            'sample': 0.125,
            'type': 'constant',
        },
        'zero_wf': {
            'sample': 0.0,
            'type': 'constant',
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
        'sine_weights': {
            'cosine': [(0.0, 100000)],
            'sine': [(1.0, 100000)],
        },
        'cosine_weights': {
            'cosine': [(1.0, 100000)],
            'sine': [(0.0, 100000)],
        },
        'minus_sine_weights': {
            'cosine': [(0.0, 100000)],
            'sine': [(-1.0, 100000)],
        },
    },
    'mixers': {
        'octave_octave1_2': [
            {'intermediate_frequency': 262000000.0, 'lo_frequency': 8400000000.0, 'correction': [1.0125585980713367, -0.15338531136512756, -0.14751067757606506, 1.0528838895261288]},
            {'intermediate_frequency': 235500000.0, 'lo_frequency': 8400000000.0, 'correction': [1.0102465897798538, -0.14740926027297974, -0.14176350831985474, 1.0504798032343388]},
            {'intermediate_frequency': 236000000.0, 'lo_frequency': 8400000000.0, 'correction': [1.0102465897798538, -0.14740926027297974, -0.14176350831985474, 1.0504798032343388]},
        ],
        'octave_octave1_1': [
            {'intermediate_frequency': 242990000.0, 'lo_frequency': 8400000000.0, 'correction': [1.0320636592805386, -0.16502943634986877, -0.16310682892799377, 1.04422901943326]},
            {'intermediate_frequency': 262000000.0, 'lo_frequency': 8400000000.0, 'correction': [1.0, 0.0, 0.0, 1.0]},
            {'intermediate_frequency': 318000000.0, 'lo_frequency': 4000000000.0, 'correction': [1.0, 0.0, 0.0, 1.0]},
        ],
    },
}


