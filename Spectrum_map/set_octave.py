from qm.octave import *
import os
import numpy as np
from qm import generate_qua_script
from qm.octave import QmOctaveConfig
import re
from configuration import *

def set_octave_config(default_port_mapping=True):
    octave_config = QmOctaveConfig()
    octave_config.set_calibration_db(os.getcwd())
    octave_config.add_device_info('octave1', octave_ip, octave_port)
    if default_port_mapping:
        octave_config.set_opx_octave_mapping([('con1', 'octave1')])
    else:
        portmap = {('con1', 1): ('octave1', 'I1'), ('con1', 2): ('octave1', 'Q1'), ('con1', 3): ('octave1', 'I2'),
                   ('con1', 4): ('octave1', 'Q2'), ('con1', 5): ('octave1', 'I3'), ('con1', 6): ('octave1', 'Q3'),
                   ('con1', 7): ('octave1', 'I4'), ('con1', 8): ('octave1', 'Q4'), ('con1', 9): ('octave1', 'I5'),
                   ('con1', 10): ('octave1', 'Q5')}
        octave_config.add_opx_octave_port_mapping(portmap)

    return octave_config

def get_elements_used_in_octave(qm=None, octave_config=None, prog=None):
    """
    This function extracts the elements used in program that are connected to the octave
    :param qm: Quantum Machine object
    :param octave_config: octave configuration
    :param prog: QUA program object
    :return: a list of elements which are used in the program and are connected to the octave
    """

    if qm is None:
        raise ('Can not find qm object')
    if octave_config is None:
        raise ('Can not find octave configuration')
    if prog is None:
        raise ('Can not find QUA program object')

    # make a list of all the elements in the program
    elements_in_prog = []
    for element in list(qm.get_config()['elements'].keys()):
        if re.search(f'(?<="){element}', generate_qua_script(prog)) is not None and re.search(f'{element}(?=")',
                                                                                              generate_qua_script(
                                                                                                  prog)) is not None:
            elements_in_prog.append(element)

    # get the elements that are connected to the octave
    elements_used_in_octave = []
    for element in elements_in_prog:
        if 'mixInputs' in config['elements'][element].keys() and qm.octave._get_element_opx_output(element)[0] in list(
                QmOctaveConfig.get_opx_octave_port_mapping(octave_config)):
            elements_used_in_octave.append(element)

    return np.array(elements_used_in_octave)


def get_L0_and_IF(config, element):
    LO = config["elements"][element]["mixInputs"]["lo_frequency"]
    IF = config["elements"][element]["intermediate_frequency"]
    return LO, IF



def set_octave(qmm, qm, prog, octave_config, internal_clock = True):
    #####################
    # setting the clock#
    #####################
    if internal_clock:
        qmm.octave_manager.set_clock("octave1", ClockType.Internal, ClockFrequency.MHZ_10)  # internal clock
    else:
        qmm.octave_manager.set_clock("octave1", ClockType.External, ClockFrequency.MHZ_1000) # external clock

    ########################################################
    # extracting octave elements and their lo and if freqs #
    ########################################################
    octave_elements = get_elements_used_in_octave(qm=qm, octave_config=octave_config, prog=prog)
    lo_freq = [config['elements'][octave_elements[i]]['mixInputs']['lo_frequency'] for i in range(len(octave_elements))]
    ##############################
    # setting up-converting block#
    ##############################
    for i in range(len(octave_elements)):
        qm.octave.set_lo_source(octave_elements[i], OctaveLOSource.Internal) # Internal by default
        qm.octave.set_lo_frequency(octave_elements[i], lo_freq[i])
        qm.octave.set_rf_output_gain(octave_elements[i], 0)
        qm.octave.set_rf_output_mode(octave_elements[i], RFOutputMode.on)

    ################################
    # setting down-converting block#
    ################################
    for i in range(len(octave_elements)):
        if config['elements'][octave_elements[i]]['mixInputs']['I'][1] == 1 and 'outputs' in config['elements'][octave_elements[i]].keys():
            qm.octave.set_qua_element_octave_rf_in_port(octave_elements[i], "octave1", 1)
            qm.octave.set_downconversion(octave_elements[i])
            qm.octave.set_downconversion(octave_elements[i], lo_source=RFInputLOSource.Internal)
        if config['elements'][octave_elements[i]]['mixInputs']['I'][1] == 3 and 'outputs' in config['elements'][octave_elements[i]].keys():
            qm.octave.set_qua_element_octave_rf_in_port(octave_elements[i], "octave1", 2)
            qm.octave.set_downconversion(octave_elements[i])
            qm.octave.set_downconversion(octave_elements[i], lo_source=RFInputLOSource.Dmd2LO) # Don't forget to connect external LO to Dmd2LO or Synth2 from back panel


def calibration(qmm, qm, prog, octave_config):
    octave_elements = get_elements_used_in_octave(qm=qm, octave_config=octave_config, prog=prog)
    lo_freq = [config['elements'][octave_elements[i]]['mixInputs']['lo_frequency'] for i in range(len(octave_elements))]
    if_freq = [config['elements'][octave_elements[i]]['intermediate_frequency'] for i in range(len(octave_elements))]

    for i in range(len(octave_elements)):
        qm.octave.calibrate_element(octave_elements[i], [(lo_freq[i], if_freq[i])])
        qm = qmm.open_qm(config)

