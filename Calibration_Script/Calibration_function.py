
from qm.qua import *
from qm.QuantumMachinesManager import QuantumMachinesManager
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from qm import SimulationConfig, LoopbackInterface
import Labber


from qm.octave import *
from qm.qua import *
import os
import time
from qualang_tools.units import unit
from set_octave import get_L0_and_IF


from qualang_tools.loops import from_array,get_equivalent_log_array
from qualang_tools.plot import interrupt_on_close
from qualang_tools.results import progress_counter, fetching_tool
from resonator_tools import circuit 


from Signal_hound_driver import Signalhound 
from lmfit.models import LinearModel

from qualang_tools.units import unit
u = unit()



def SingleResonatorSpec(qm,n_avg,calib_pulse_len,cooldown_time, f_min, f_max, df, amp_factor,LO_readout,plot=True): 
    
    freqs = np.arange(f_min, f_max + 0.1, df)
    
    with program() as resonator_spec:

        n = declare(int)
        f = declare(int)
        I = declare(fixed)
        Q = declare(fixed)
        I_st = declare_stream()
        Q_st = declare_stream()
        n_st= declare_stream()

        with for_(n, 0, n < n_avg, n + 1):

            with for_(f, f_min, f <= f_max, f + df):  # Notice it's <= to include f_max (This is only for integers!)

                update_frequency("resonator", f)

                measure(
                    "cw"*amp(amp_factor),
                    "resonator",
                    None,
                    dual_demod.full("cos", "out1", "sin", "out2", I),
                    dual_demod.full("minus_sin", "out1", "cos", "out2", Q),
                )

                wait(cooldown_time, "resonator") #Waiting time between sucessive measure 

                save(I, I_st)
                save(Q, Q_st)

            save(n, n_st)

        with stream_processing():

            I_st.buffer(len(freqs)).average().save("I") #Fills all the buffer frequency and then average the sucessive 
            Q_st.buffer(len(freqs)).average().save("Q")
            n_st.save("iteration")

    simulate = False

    if simulate:

        simulation_config = SimulationConfig(duration=10000)
        job = qmm.simulate(config, resonator_spec, simulation_config)
        job.get_simulated_samples().con1.plot(analog_ports={'1','2'},digital_ports={'1'})

    else:

        job = qm.execute(resonator_spec)

        # Get results from QUA program
        results = fetching_tool(job, data_list=["I", "Q", "iteration"], mode="live")

        # Live plotting
        fig = plt.figure()
    

        while results.is_processing():
            # Fetch results
            I, Q, iteration = results.fetch_all()
            
                # Convert I & Q to Volts
            I = u.demod2volts(I, calib_pulse_len)
            Q = u.demod2volts(Q, calib_pulse_len)
            
            progress_counter(iteration, n_avg, start_time=results.get_start_time())

            # Plot results
            plt.subplot(211)
            plt.cla()
            plt.title("resonator spectroscopy amplitude")
            plt.plot(freqs / u.MHz, 20*np.log10(np.sqrt(I**2 + Q**2)/(amp_factor)), ".")
            plt.xlabel("frequency [MHz]")
            plt.ylabel(r"$\sqrt{I^2 + Q^2}$ [a.u.]")
            plt.subplot(212)
            plt.cla()
            # detrend removes the linear increase of phase
            phase = signal.detrend(np.unwrap(np.angle(I + 1j * Q)))
            plt.title("resonator spectroscopy phase")
            plt.plot(freqs / u.MHz, phase, ".")
            plt.xlabel("frequency [MHz]")
            plt.ylabel("Phase [rad]")
            plt.pause(0.1)
            plt.tight_layout()
            
            
    
    f=freqs+LO_readout 
    
    port=circuit.notch_port()
    port.add_data(f,I+ 1j*Q)
    port.autofit()
    
    if plot==True : 

        fig, axs = plt.subplots( nrows=1, ncols=3, figsize=(26/2.54, 6/2.54),dpi=200)
        figsize=(8/2.54, 6/2.54)
        dpi=300
        fontsize=5

        #fig.suptitle("Output VNA power "+str(y_0[idx]) +" dB", fontsize=8)



        ax=axs[0]
        ax.plot(port.z_data_raw.real, port.z_data_raw.imag,"o", ms=0.5)
        ax.plot(port.z_data_sim.real, port.z_data_sim.imag,"-")
        ax.set_title("S21",fontsize=fontsize)
        ax.set_xlabel("Real value [S21]",fontsize=fontsize)
        ax.set_ylabel("Imag value [S21]",fontsize=fontsize)
        ax.tick_params(axis='x', labelsize=fontsize)
        ax.tick_params(axis='y', labelsize=fontsize)


        ax=axs[1]
        ax.plot(f/1e9, np.abs(port.z_data_raw),"o", ms=0.5)
        ax.plot(f/1e9, np.abs(port.z_data_sim),"-")
        ax.set_title("Amplitude",fontsize=fontsize)
        ax.set_xlabel("Frequency [GHz]",fontsize=fontsize)
        ax.set_ylabel("Amplitude ",fontsize=fontsize)
        ax.tick_params(axis='x', labelsize=fontsize)
        ax.tick_params(axis='y', labelsize=fontsize)



        ax=axs[2]
        ax.plot(f/1e9, np.angle(port.z_data_raw),"o", ms=0.5)
        ax.plot(f/1e9, np.angle(port.z_data_sim),"-")
        ax.set_title("Phase",fontsize=fontsize)
        ax.set_xlabel("Frequency [GHz]",fontsize=fontsize)
        ax.set_ylabel("Phase [rad]",fontsize=fontsize)
        ax.tick_params(axis='x', labelsize=fontsize)
        ax.tick_params(axis='y', labelsize=fontsize)
    resonance_frequency=port.fitresults["fr"]
    error_frequency=port.fitresults['fr_err']


    print("The measured resonance frequency is {} GHz with an error of {} GHz".format(port.fitresults["fr"]/1e9,port.fitresults['fr_err']/1e9))
    
    plt.close()

 
    return freqs,I,Q,resonance_frequency, error_frequency





def Resonator_Power_Monitoring(qm,sgh,amplitude_array, n_points):
    
    Spec_amp=np.zeros(len(amplitude_array))
    pulse_time=2_000_000_000//4
    
    amplitude_array=amplitude_array.tolist()
    
    #defines the program 
    with program() as calib_amp:

        a=declare(fixed)

        with for_each_(a,amplitude_array):

            play("cw"*amp(a), "resonator",duration=pulse_time) #Plays the pump pulse on the flux line 
            pause() # pause to collect the data from the trigger 


    job = qm.execute( calib_amp)  # Execute QUA program  


    for j in range(len(amplitude_array)):
        while not job.is_paused():
            time.sleep(0.001)


        print(j)
        #time.sleep()
        sgh.IQ(n_points)
        time.sleep(0.5)


        b=sgh.iqArr[0:].reshape(int(len(sgh.iqArr[0:])/2),2)
        Spec_amp[j]=np.mean(np.sqrt(b[:,0]**2+b[:,1]**2))*1000

        job.resume()  # Resume to the program
        
   

    return Spec_amp


def Pump_Power_Monitoring(qm,sgh,amplitude_array, n_points):
    
    Spec_amp=np.zeros(len(amplitude_array))
    pulse_time=2_000_000_000//4
    
    #defines the program 
    with program() as calib_amp:

        a=declare(fixed)

        with for_(*from_array(a,amplitude_array)):

            play("pumping"*amp(a), "fluxline",duration=pulse_time) #Plays the pump pulse on the flux line 
            pause() # pause to collect the data from the trigger 
            

    job = qm.execute(calib_amp)  # Execute QUA program  


    for j in range(len(amplitude_array)):
        while not job.is_paused():
            time.sleep(0.001)


        print(j)
        #time.sleep()
        sgh.IQ(n_points)
        time.sleep(0.5)


        b=sgh.iqArr[0:].reshape(int(len(sgh.iqArr[0:])/2),2)
        Spec_amp[j]=np.mean(np.sqrt(b[:,0]**2+b[:,1]**2))*1000

        job.resume()  # Resume to the program
        
   

    return Spec_amp



def full_power_calibration(qm,dll_path,amplitude_array_res, amplitude_array_pump, IF_readout, LO_readout, IF_fluxline, LO_fluxline): 

    
    sgh=Signalhound()
    #open the device
    sgh.performOpen(dll_path)


    center_freq=LO_readout+IF_readout
    span=5e3 #does not change anything 
    ref_level=-30

    decimation=1
    bandwidth=250e3

    sgh.setSweepParameters(center_freq,span)
    sgh.setRefLevel(ref_level)
    sgh.setGainAtten()
    sgh.setIQ(decimation,bandwidth)
    sgh.setProcUnit("mV")
    sgh.setSweepMode("IQ")


    #amplitude factor 
    n_points=4000

    amp_calib_res=Resonator_Power_Monitoring(qm,sgh,amplitude_array_res, n_points)


    model=LinearModel()
    params=model.make_params(slope=1, intercept=0)
    result=model.fit(amp_calib_res,params, x=amplitude_array_res)

    plt.plot(amplitude_array_res,amp_calib_res,".")
    plt.xlabel("Amp factor")
    plt.ylabel("Signal hound")
    plt.plot(amplitude_array_res, result.best_fit)

    slope_res=result.params["slope"].value
    intercept_res=result.params["intercept"].value

    #Initial values 
    init_value=np.array([0.6621, 3.3114, 6.61637])
    init_slope=6.615617
    init_intercept=0.001645


    print("Variation relative to the first calibration {}".format(amp_calib_res/init_value))
    print("Slope relative to the first intercept {}".format(slope_res/init_slope))
    print("Intercept relative to the first intercept {}".format(intercept_res/init_intercept))



    center_freq=LO_fluxline+IF_fluxline
    span=5e3 #does not change anything 
    ref_level=-30

    decimation=1
    bandwidth=250e3

    sgh.setSweepParameters(center_freq,span)
    sgh.setRefLevel(ref_level)
    sgh.setGainAtten()
    sgh.setIQ(decimation,bandwidth)
    sgh.setProcUnit("mV")
    sgh.setSweepMode("IQ")


    n_points=4000

    amp_calib_pump=Pump_Power_Monitoring(qm,sgh,amplitude_array_pump, n_points)


    model=LinearModel()
    params=model.make_params(slope=1, intercept=0)
    result=model.fit(amp_calib_pump,params, x=amplitude_array_pump)

    plt.plot(amplitude_array_pump,amp_calib_pump,".")
    plt.xlabel("Amp factor")
    plt.ylabel("Signal hound")
    plt.plot(amplitude_array_pump, result.best_fit)

    slope_pump=result.params["slope"].value
    intercept_pump=result.params["intercept"].value

    #Initial values 
    init_value=np.array([ 8.27148,  9.24304,  10.21174, 11.188815, 12.14929])
    init_slope=9.700894
    init_intercept=0.0264438


    print("Variation relative to the first calibration {}".format(amp_calib_pump/init_value))
    print("Slope relative to the first intercept {}".format(slope_pump/init_slope))
    print("Intercept relative to the first intercept {}".format(intercept_pump/init_intercept))
    
    
    sgh.performClose()
    
    return amp_calib_pump, amp_calib_res




def Pump_Power_Monitoring_sticky(qm,sgh,amplitude_array, n_points):
    
    Spec_amp=np.zeros(len(amplitude_array))
    pulse_time=2_000_000_000//4
    
    #defines the program 
    with program() as calib_amp:

        a=declare(fixed)

        with for_(*from_array(a,amplitude_array)):

            play("pumping"*amp(a), "fluxline") #Plays the pump pulse on the flux line 
            pause() # pause to collect the data from the trigger 
            
            ramp_to_zero("fluxline")  #ramp the pump to zero

    job = qm.execute(calib_amp)  # Execute QUA program  


    for j in range(len(amplitude_array)):
        while not job.is_paused():
            time.sleep(0.001)


        print(j)
        #time.sleep()
        sgh.IQ(n_points)
        time.sleep(0.5)


        b=sgh.iqArr[0:].reshape(int(len(sgh.iqArr[0:])/2),2)
        Spec_amp[j]=np.mean(np.sqrt(b[:,0]**2+b[:,1]**2))*1000

        job.resume()  # Resume to the program
        
   

    return Spec_amp



def full_power_calibration_sticky(qm,dll_path,amplitude_array_res, amplitude_array_pump, IF_readout, LO_readout, IF_fluxline, LO_fluxline): 

    
    sgh=Signalhound()
    #open the device
    sgh.performOpen(dll_path)


    center_freq=LO_readout+IF_readout
    span=5e3 #does not change anything 
    ref_level=-30

    decimation=1
    bandwidth=250e3

    sgh.setSweepParameters(center_freq,span)
    sgh.setRefLevel(ref_level)
    sgh.setGainAtten()
    sgh.setIQ(decimation,bandwidth)
    sgh.setProcUnit("mV")
    sgh.setSweepMode("IQ")


    #amplitude factor 
    n_points=4000

    amp_calib_res=Resonator_Power_Monitoring(qm,sgh,amplitude_array_res, n_points)


    model=LinearModel()
    params=model.make_params(slope=1, intercept=0)
    result=model.fit(amp_calib_res,params, x=amplitude_array_res)

    plt.plot(amplitude_array_res,amp_calib_res,".")
    plt.xlabel("Amp factor")
    plt.ylabel("Signal hound")
    plt.plot(amplitude_array_res, result.best_fit)

    slope_res=result.params["slope"].value
    intercept_res=result.params["intercept"].value

    #Initial values 
    init_value=np.array([0.6621, 3.3114, 6.61637])
    init_slope=6.615617
    init_intercept=0.001645


    print("Variation relative to the first calibration {}".format(amp_calib_res/init_value))
    print("Slope relative to the first intercept {}".format(slope_res/init_slope))
    print("Intercept relative to the first intercept {}".format(intercept_res/init_intercept))



    center_freq=LO_fluxline+IF_fluxline
    span=5e3 #does not change anything 
    ref_level=-30

    decimation=1
    bandwidth=250e3

    sgh.setSweepParameters(center_freq,span)
    sgh.setRefLevel(ref_level)
    sgh.setGainAtten()
    sgh.setIQ(decimation,bandwidth)
    sgh.setProcUnit("mV")
    sgh.setSweepMode("IQ")


    n_points=4000

    amp_calib_pump=Pump_Power_Monitoring_sticky(qm,sgh,amplitude_array_pump, n_points)


    model=LinearModel()
    params=model.make_params(slope=1, intercept=0)
    result=model.fit(amp_calib_pump,params, x=amplitude_array_pump)

    plt.plot(amplitude_array_pump,amp_calib_pump,".")
    plt.xlabel("Amp factor")
    plt.ylabel("Signal hound")
    plt.plot(amplitude_array_pump, result.best_fit)

    slope_pump=result.params["slope"].value
    intercept_pump=result.params["intercept"].value

    #Initial values 
    init_value=np.array([ 8.27148,  9.24304,  10.21174, 11.188815, 12.14929])
    init_slope=9.700894
    init_intercept=0.0264438


    print("Variation relative to the first calibration {}".format(amp_calib_pump/init_value))
    print("Slope relative to the first intercept {}".format(slope_pump/init_slope))
    print("Intercept relative to the first intercept {}".format(intercept_pump/init_intercept))
    
    
    sgh.performClose()
    
    return amp_calib_pump, amp_calib_res