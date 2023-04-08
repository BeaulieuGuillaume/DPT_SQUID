#Defines the functions 
from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.octave import *
from qm.qua import *

import matplotlib.pyplot as plt
from qualang_tools.units import unit
from set_octave import get_L0_and_IF
from configuration_multiple_jumps import *
from qm import SimulationConfig, LoopbackInterface
from qualang_tools.units import unit
from qualang_tools.loops import from_array
u = unit()
from qualang_tools.plot import interrupt_on_close
from qualang_tools.results import progress_counter, fetching_tool
from qualang_tools.addons.variables import assign_variables_to_element


#Function for a single IQ trace 
def single_IQ_trace(IF_pump,IF_resonator,Offset_IF,amp_factor,n_runs,Readout_Delay,Readout_Len,qm):
    
    """ gets the IQ values for a given pump frequency and amplitude 
    IF_Pump : If frequency of the pump 
    IF_resonator : IF frequency of the resonator (should be calculated before such that it gives half of the pump total frequency (LO_fluxline+IF_pump)/2-LO_readout
    Offset_IF : in case the down converted frequency is not perfectly centered around 0. This is typically kept to zero
    amp_facot amplitude factor of the pump
    n_runs : number of points 
    Readout_delay : waiting time before the first readout in clock cycle
    Readout_Len : time in ns of each readout 
    qm : quantum manager 
    
    returns :
    
    I: vector n_runs components of the frist quadrature
    Q : vector of n_runs compontents of the second quadrature
    time : vector of the time """
    

    with program() as IQ_blobs:

        n = declare(int)
        i = declare(int)
        I = declare(fixed)
        Q = declare(fixed)
        assign_variables_to_element("resonator", I,Q) #This line forces the OPX to assign I and Q to the resonator element such that the loops can happen in parallel as intented
        I_st = declare_stream()
        Q_st = declare_stream()
        f = declare(int)

        # Change the of the pump and resonator to demodulate better
        update_frequency("resonator",IF_resonator+Offset_IF) 
        update_frequency("fluxline",IF_pump)

        #Play a continuous loop sending a pulse through the fluxline 
         # Starts playing on the fluxline 
        # with infinite_loop_():
        #     play("pumping"*amp(amp_factor), 'fluxline') #Play the pulse on the fluxline  

        with for_(i, 0, i < np.round((n_runs*(Readout_Len+300)+Readout_Delay*4)/twoPhoton_len)+1, i + 1): # the 300 is added because there is a time delay associated to saving the data in the steam. The *4 is necessary because the waiting time is in clockcycle 
            play("pumping" * amp(amp_factor), 'fluxline')  # Play the pulse on the fluxline


        #Delay time before the first readout 
        wait(Readout_Delay,"resonator")

        with for_(n, 0, n < n_runs, n + 1):

            #Demodulate for the length 
            measure(
                "fake_readout",
                "resonator",
                None,
                dual_demod.full("cos", "out1", "sin", "out2", I),
                dual_demod.full("minus_sin", "out1", "cos", "out2", Q),
            )

            save(I, I_st)
            save(Q, Q_st)


        with stream_processing():
            I_st.with_timestamps().save_all("I")
            Q_st.with_timestamps().save_all("Q")
        
    job = qm.execute(IQ_blobs)
    results = fetching_tool(job, data_list=["I", "Q"], mode="live")
    
    fig = plt.figure()
    interrupt_on_close(fig, job)
    while results.is_processing():
       
        I, Q = results.fetch_all()
        
        dt=(I["timestamp"][1]-I["timestamp"][0])*1e-9 #time between sucessive points
        I = u.demod2volts(I["value"], Readout_Len) #diviser par la duree du pulse 
        Q = u.demod2volts(Q["value"], Readout_Len)

        #plt.subplot(211)
        plt.title("IQ blobs")
        plt.subplot(211)
        plt.cla()
        plt.plot(I[:min(len(I), len(Q))], Q[:min(len(I), len(Q))], ".", markersize=2)
        plt.xlabel("I")
        plt.ylabel("Q")
        plt.axis("equal")
        plt.subplot(212)
        plt.cla()
        tau=np.linspace(1,min(len(I), len(Q)),min(len(I), len(Q)))
        plt.plot(tau,np.angle(I[:min(len(I), len(Q))]+1j*Q[:min(len(I), len(Q))]), ".", markersize=2)
        plt.xlabel("nb_points")
        plt.ylabel("phase")
        plt.pause(0.1)
       
    I, Q = results.fetch_all()
    dt=(I["timestamp"][1]-I["timestamp"][0])*1e-9 #time between sucessive points
    I = u.demod2volts(I["value"], Readout_Len) #diviser par la duree du pulse 
    Q = u.demod2volts(Q["value"], Readout_Len)
    time=np.linspace(1,len(I), len(I),len(I))*dt # time in micro seconds
    
    return I,Q,time 


def Update_single_IQ_trace(config,IF_pump,IF_resonator,Offset_IF,amp_factor,qm,nb_desired_jumps,nb_points_between_jumps,nb_angle=100,n_avg=10,init_Readout_Len=50_000,init_nruns=100000,threshold=1e-5 ):
    
    #Initialisation
    counter=0
    jumps=[] 
    stop=False
    vaccum=False
    
    Readout_Len= init_Readout_Len    # Sets the readout to the initial wanted value 
    config,qm=update_readout_lenght(Readout_Len,config,qmm)
    
    
    n_runs=init_nruns # set the number_runsto the initial wanted number of runs 
    
    #First estimate of the total time 
    Total_time=n_runs*Readout_Len*1e-9

    counter+=1
    
    print("########### Iteration number : {} ##########".format(counter))
    print("The program is initalized with :")
    print("A readout length of {}".format(Readout_Len))
    print("The Number of points  {}".format(n_runs))   
    print("Time for iteration  {} min".format(Total_time/60)) 


    # Begins the loop that is stopped under the following conditions : we have more then 90 % of the number of desired jumps but less than twice (otherwise, we might not have the optimal readout length)
    # stop is set to true 
    
    while stop==False:


        #Run the program for a single IQ trace once 
        time_package.sleep(1)
        I,Q,time=single_IQ_trace(IF_pump,IF_resonator,Offset_IF,amp_factor,n_runs,Readout_Delay,Readout_Len,qm)
        
        print("Out_of_qm")
        plt.close()

        #rotate data and average 
        I_2d=np.reshape(I, (1, I.shape[0])) 
        Q_2d=np.reshape(Q, (1, Q.shape[0]))
        rot_I,rot_Q=an.rotate_data(I_2d,Q_2d,nb_angle)
        average_I,average_Q,time_average=an.average_data(rot_I,rot_Q,time,n_avg)
        av = np.mean(abs(average_I))
        print(av)
        
        # We look if the average value is above our threshold. Being blow this threshold tells use that we should measure with the minimum readout len anyway so we can stop 
        if av>threshold:
            
            #renormalize the data and find jumps 
            length_array=average_I.shape[1] 
            jumps=an.find_jumps(average_I[0]/av,length_array,Nw=10)
            print("Jumps found {}".format(len(jumps)))
            
            #Check if we have succed. If yes, the program is stoped
            if nb_desired_jumps*0.9<len(jumps)<2*nb_desired_jumps:
                stop=True 
                print("Success")
            # if not, we start a new iteration
            else:
                counter+=1
                print("########### Iteration number : {} ##########".format(counter))
        
        #If we are below threshold, we stop 
        else: 
            vaccum=True
            print("vaccum state")
            stop=True 
            

        # If the program is not stopped, we continue 
        if stop==False: 
            
            #If we have found zero jump, we increase the parameters  
            if (len(jumps)==0):
                
                print("no jumps found found")

                #If the length was already between 1.5 and 2 ms
                if 1_500_000<Readout_Len<=2_000_000:

                    print("We update the number of runs")
                    Readout_Len=2_000_000 #we set the readout_len
                    config,qm=update_readout_lenght(Readout_Len, config,qmm)
                    n_runs=2*n_runs #double the number of runs

                else:

                    print("We update the readout length")
                    Readout_Len=2*Readout_Len 
                    config,qm=update_readout_lenght(Readout_Len, config,qmm)

                    #If the readout_len is larger than 2 ms, we set 2 ms  
                    if Readout_Len>2_000_000:
                        Readout_Len=2_000_000

                Total_time=n_runs*Readout_Len*1e-9
                print("New readout length of {}".format(Readout_Len))
                print("New number of points  {}".format(n_runs))   
                print("Time for iteration  {} min".format(Total_time/60)) 

                if Total_time>10*60: #If the total time is larger than 10 minutes 
                    stop=True 

            # In the case we find some jumps 
            else:

                time_per_jump=time_average[length_array-1]/len(jumps) #average time per jump 
                Total_time= time_per_jump*nb_desired_jumps #total time I should measure to get the number of desired jumps 

                Readout_Len=4*round(round(time_per_jump*1e9/nb_points_between_jumps)/4) # expected readout length given that I would like x number of points between jumps 

                if Readout_Len>2_000_000:
                    Readout_Len=2_000_000

                if Readout_Len<50_000:
                    Readout_Len=50_000

                n_runs=round(Total_time*1e9/Readout_Len)

                #Update the readout length based on the single test  
                config,qm=update_readout_lenght(Readout_Len, config,qmm)

                print("New readout length of {}".format(Readout_Len))
                print("New number of points {}".format(n_runs))
                print("Time for iteration  {} min".format(Total_time/60))

                if Total_time>10*60: #If the total propsed time is larger than 10 minutes 
                    stop=True 
            
    
    return I,Q,rot_I,rot_Q,time,counter,Readout_Len,n_runs,jumps,vaccum