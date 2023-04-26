# %% 
from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.octave import (
    QmOctaveConfig, OctaveManager, ClockType, CalibrationDB )

from qm.octave.enums import ClockInfo
import logging
import os

# %% ------------------------------------------------------------------------------
# 1. Configure the octave(s)

# All the octaves are configured in this single object:
octaves_config = QmOctaveConfig()

# Configure the first (and only) Octave. It shall be called 'octave1', you sho
octave1_ip = "128.178.175.167"
octave1_port = 52
octaves_config.add_device_info(
    "octave1", octave1_ip, octave1_port,
    ClockInfo(ClockType.External, 10e6))



octaves_config.set_opx_octave_mapping([("con1", "octave1")])

# The last command is uquivalent to 

# octaves_config.add_opx_octave_port_mapping({
#     ('con1',  1) : ('octave1', 'I3'),
#     ('con1',  2) : ('octave1', 'Q3'),
#     ('con1',  3) : ('octave1', 'I5'),
#     ('con1',  4) : ('octave1', 'Q5'),
# })

# Now open octave manager object (at this point, the octaves are treated as
# standalone devices). Each of the Octaves will start using its specified clock.
octave_manager = OctaveManager(octaves_config)

# %% ------------------------------------------------------------------------------
# 2. Choose the calibration database to be used.

calibration_db = CalibrationDB(os.getcwd())

# %% ------------------------------------------------------------------------------
# 3. Open Quantum Machine Manager 

# Gateway OPX address
opx_ip = "128.178.175.167"
opx_port = 80

# Upon initialization, the QMM connects to all the configured octaves.
qmm = QuantumMachinesManager(
    host=opx_ip,
    port=opx_port,
    octave_manager=octave_manager,
    calibration_db=calibration_db)

# %%
