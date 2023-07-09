import numpy as np
import ctypes
import matplotlib.pyplot as plt
from time import sleep




#
# sAConfig level : when this is set the auto, the device will automatically decide the attenuation and gain to get the maximum dynamic range. The choice of this setting will depend on what is set for the reference level. To achieve best results, the reference level needs to be set or slighly above the expected input power. The reference level is in dBm units. 


# The resolution bandwith represent the bandwidth of spectral energy represented in each frequency bin. For an rbw of 10 KHz, the amplitude value for each bin would represent the total energy from 5 kHz below to 5 KHz above the center bin. The maximum rbw is 250 KHZ and the minimum is 0.1 HZ. 

# For spans between 201kHz and 99MHz with a start frequency above 16MHz, the RBW can be set between 30Hz and 250kHz.
# For spans larger than 99MHz or sweeps that start below 16MHz, the RBW can be set between 6.5 kHz
# and 250kHz.

# The vbw is applied after the signal has been converted to the frequency domain as power, voltage or log units. It is implemented as a simple rectangular window , averaging the amplide readings for each frequency bin over several overlapping FFTs. A signal whose amplitude is modulated at a much higher frequency than the vbw will be shown as an average. A signal whose amplitude is modulated at lower frequency will be shown as minimum and maximum value. 




# For “average power” measurements, SA_POWER_UNITS should be selected. For cleaning up an amplitude
# modulated signal, SA_VOLT_UNITS would be a good choice. To emulate a traditional spectrum analyzer,
# select SA_LOG_UNITS. 



class IQPacketData(ctypes.Structure):
    _fields_ = [('iqData',ctypes.POINTER(ctypes.c_float)), #pointer to a 32 bit complex floating point values. This must be a continous block of iqc ount complex pairs
            ('iqCount',ctypes.c_int), #number of I/Q data pairs to return
            ('purge', ctypes.c_int), # Specifies whether to discard any samples acquired by the API since the last time and saGetIQData function was called. Set to SA_TRUE if you wish to discard all previously acquired data, and SA_FALSE if you wish to retrieve the contiguous I/Q values from a previous call to this function. 
            ('dataRemaining', ctypes.c_int),# How many I/Q samples are still left buffered in the API. Set by API. 
            ('sampleLoss', ctypes.c_int), #Returns SA_TRUE or SA_FALSE. Will return SA_TRUE when the API is required to drop data due to internal buffers wrapping. This can be caused by I/Q samples not being polled fast enough, or in instances where the processing is not able to keep up (underpowered systems, or other programs utilizing the CPU) Will return SA_TRUE on the capture in which the sample break occurs. Does not indicate which sample the break occurs on. Will always return SA_FALSE if purge is true. Set by API. 
            ('sec', ctypes.c_int), #Seconds since epoch representing the timestamp of the first sample in the returned array. Set by API. 
            ('milli', ctypes.c_int)] #Milliseconds representing the timestamp of the first sample in the returned array. Set by API. 



class Constants:
    """
    These constants are defined in sa_api.h as part of the the Signal Hound
    SDK
    """
    
    sa_FALSE=0
    sa_TRUE=1

    SA_MAX_DEVICES = 8

    saDeviceTypeNone = 0
    saDeviceTypeSA44 = 1
    saDeviceTypeSA44B = 2
    saDeviceTypeSA124A = 3
    saDeviceTypeSA124B = 4

    sa44_MIN_FREQ = 1.0
    sa124_MIN_FREQ = 100.0e3
    sa44_MAX_FREQ = 4.4e9
    sa124_MAX_FREQ = 13.0e9
    sa_MIN_SPAN = 1.0
    sa_MAX_REF = 20
    sa_MAX_ATTEN = 3
    sa_MAX_GAIN = 2
    sa_MIN_RBW = 0.1
    sa_MAX_RBW = 6.0e6
    sa_MIN_RT_RBW = 100.0
    sa_MAX_RT_RBW = 10000.0
    sa_MIN_IQ_BANDWIDTH = 100.0
    sa_MAX_IQ_DECIMATION = 128

    sa_IQ_SAMPLE_RATE = 486111.111

    sa_IDLE = -1
    sa_SWEEPING = 0x0
    sa_REAL_TIME = 0x1
    sa_IQ = 0x2
    sa_AUDIO = 0x3
    sa_TG_SWEEP = 0x4

    sa_MIN_MAX = 0x0
    sa_AVERAGE = 0x1
    
    sa_LOG_UNITS=0x0
    sa_VOLT_UNITS=0x1
    sa_POWER_UNITS=0x2
    
    sa_REF_EXTERNAL_IN=2
    sa_REF_EXTERNAL_OUT=1

    sa_LOG_SCALE = 0x0
    sa_LIN_SCALE = 0x1
    sa_LOG_FULL_SCALE = 0x2
    sa_LIN_FULL_SCALE = 0x3

    sa_AUTO_ATTEN = -1
    sa_AUTO_GAIN = -1

    sa_LOG_UNITS = 0x0
    sa_VOLT_UNITS = 0x1
    sa_POWER_UNITS = 0x2
    sa_BYPASS = 0x3

    sa_AUDIO_AM = 0x0
    sa_AUDIO_FM = 0x1
    sa_AUDIO_USB = 0x2
    sa_AUDIO_LSB = 0x3
    sa_AUDIO_CW = 0x4

    TG_THRU_0DB = 0x1
    TG_THRU_20DB = 0x2

    sa_REF_UNUSED = 0
    sa_REF_INTERNAL_OUT = 1
    sa_REF_EXTERNAL_IN = 2


class saStatus():
    saUnknownErr = -666
    saFrequencyRangeErr = 99
    saInvalidDetectorErr = -95
    saInvalidScaleErr = -94
    saBandwidthErr = -91
    saExternalReferenceNotFound = -89
    # Device specific errors
    saOvenColdErr = -20
    # Data errors
    saInternetErr = -12
    saUSBCommErr = -11
    # General configuration errors
    saTrackingGeneratorNotFound = -10
    saDeviceNotIdleErr = -9
    saDeviceNotFoundErr = -8
    saInvalidModeErr = -7
    saNotConfiguredErr = -6
    saDeviceNotConfiguredErr = -6  # Added because key error raised
    saTooManyDevicesErr = -5
    saInvalidParameterErr = -4
    saDeviceNotOpenErr = -3
    saInvalidDeviceErr = -2
    saNullPtrErr = -1
    # No error
    saNoError = 0
    # Warnings
    saNoCorrections = 1
    saCompressionWarning = 2
    saParameterClamped = 3
    saBandwidthClamped = 4
    
    
    

class Signalhound(): 
    
    
    def performOpen(self,dll_path):
        """ Opens the signal hound and creates pointers to hold the values for the other question. 
        For now, the signal hound is automatically defined in the average mode with log_scale"""
        
        self.sighound = ctypes.CDLL(dll_path)
        self.hf=Constants #constants
        self.err=saStatus #errors
        
        #variables that contains information returned by function 
        self.handle = ctypes.c_int() #handle 
        self.sweepLen = ctypes.c_int();
        self.startFreq = ctypes.c_double();
        self.binSize = ctypes.c_double();
        self.min = np.empty(1,dtype="float32");
        self.max = np.empty(1,dtype="float32");
        
        
        if(self.sighound.saOpenDevice(ctypes.byref(self.handle))!=0):
            print("Unable to open device SignalHound")
        else:
            self.sighound.saConfigAcquisition(self.handle,ctypes.c_int(self.hf.sa_AVERAGE),ctypes.c_int(self.hf.sa_LOG_SCALE))
            self.sighound.saSetTimebase(self.handle, ctypes.c_int(self.hf.sa_REF_EXTERNAL_IN))
            
    def performClose(self, bError=False, options={}):
        """ Close the signal hound. This must be done after every use"""
        err=self.sighound.saCloseDevice(self.handle)
        self.check_for_error(err, "saCloseDevice")
        
    def setSweepParameters(self,center_freq,span):
        """ Configures the center_freq and the span of the measurement"""
        
        self.center_freq=center_freq
        self.span=span
        self.start=center_freq-(span/2)
        self.stop=center_freq+(span/2)
        
        err=self.sighound.saConfigCenterSpan(self.handle,ctypes.c_double(self.center_freq),ctypes.c_double(self.span)) #config the center and span 
        self.check_for_error(err, "saConfigCenterSpan")
        
    def setRefLevel(self,ref_level):
        """ Sets the reference level. This should be slighly higher than the expected input from the signal to choose the correct set of gain and attenuation"""
         
        
        self.ref_level=ref_level
        
        err=self.sighound.saConfigLevel(self.handle, ctypes.c_double(ref_level)) 
        self.check_for_error(err, "saConfigLevel")
        
    def setGainAtten(self):
        """ sets the atomatic gain and attenuation based on the expected input power from the reference level"""

        err=self.sighound.saConfigGainAtten(self.handle,ctypes.c_int(self.hf.sa_AUTO_ATTEN), ctypes.c_int(self.hf.sa_AUTO_GAIN)) # for now, only automatic is supported so reference level needs to chossen accordingly 
        self.check_for_error(err, "saConfigGainAtten")
        
    def setSweepCoupling(self,rbw, vbw):
        """ sets the rbw and the vbw following the different restrictions given in the manual """
     
        
        self.rbw=rbw
        self.vbw=vbw
        
        err=self.sighound.saConfigSweepCoupling(self.handle, ctypes.c_double(self.rbw), ctypes.c_double(self.vbw), ctypes.c_int(0))  # image rejection set to falst 
        self.check_for_error(err, "saConfigGainAtten")
        
    def setProcUnit(self,units):
    
        self.units=units
        
        
        if self.units=="dbm":
            err=self.sighound.saConfigProcUnits(self.handle, ctypes.c_int(self.hf.sa_LOG_UNITS)) 
            self.check_for_error(err, "saConfigProcUnits")
        elif self.units=="mV":
            err=self.sighound.saConfigProcUnits(self.handle, ctypes.c_int(self.hf.sa_VOLT_UNITS)) 
            self.check_for_error(err, "saConfigProcUnits")
        elif self.units=="mW":
            err=self.sighound.saConfigProcUnits(self.handle, ctypes.c_int(self.hf.sa_POWER_UNITS))
            self.check_for_error(err, "saConfigProcUnits")
        else :
            print("Select allowed units: either dbm, mV or mW")
            
        
        
        
    def setSweepMode(self,mode):
        """ defines the acquisition mode. Only two modes are currently supported : the sweeping and IQ mode"""
     
        self.mode=mode
        
        if self.mode=="sweeping":
            err=self.sighound.saInitiate(self.handle,ctypes.c_int(self.hf.sa_SWEEPING),ctypes.c_int(0))
            
            err=self.sighound.saQuerySweepInfo(self.handle,ctypes.byref(self.sweepLen),ctypes.byref(self.startFreq),ctypes.byref(self.binSize))
            self.check_for_error(err, "saQuerySweepInfo")

            end_freq = self.startFreq.value + self.binSize.value * (self.sweepLen.value - 1)
            self.freq = np.linspace(self.startFreq.value, end_freq, self.sweepLen.value)
            
        elif self.mode=="IQ":
            err=self.sighound.saInitiate(self.handle,ctypes.c_int(self.hf.sa_IQ),ctypes.c_int(0))
            self.check_for_error(err, "saQuerySweepInfo")
        else : 
            print("Select allowed mode: either sweeping or IQ")
            
        self.check_for_error(err, "saInitiate")
        
       
    def SingleSweep(self):
        """ Performs a single sweep based on the parameters defined above"""
     
        
        #Upon returning successfully, this function returns the minimum and maximum arrays of one full sweep.
        #If the detector provided in saConfigAcquisition() is SA_AVERAGE, the arrays will be populated with
        #the same values. Element zero of each array corresponds to the startFreq returned fro
        
        self.min = np.zeros(self.sweepLen.value,dtype="float32"); # required to get the sweep 
        self.max = np.zeros(self.sweepLen.value,dtype="float32"); # required to get the sweep 
        
        minarr= self.min.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        maxarr= self.max.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        
        err=self.sighound.saGetSweep_32f(self.handle, minarr, maxarr);  # the sweep value is pointed into minarr and maxarr. If it is set to average, it will 
        self.check_for_error(err, "Getsweep")
        
        self.trace=self.min
        
        
    def AvSweep(self,navg):
        """ Averages navg sweep and returns the value un self.av_trace """
       
        self.navg=navg
        
        data=np.zeros(self.sweepLen.value)
        
        for i in range(navg):
            
            self.min = np.zeros(self.sweepLen.value,dtype="float32"); # required to get the sweep 
            self.max = np.zeros(self.sweepLen.value,dtype="float32"); # required to get the sweep 
            
            self.trace=self.min # last trace 
            
           
            
            minarr= self.min.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
            maxarr= self.max.ctypes.data_as(ctypes.POINTER(ctypes.c_float))

            sleep(0.01)
            err=self.sighound.saGetSweep_32f(self.handle, minarr, maxarr);  # the sweep value is pointed into minarr and maxarr. If it is set to average, it will 
            self.check_for_error(err, "Getsweep")

            
            data+= self.min
            
        self.av_trace=data/navg
            
            
    def setIQ(self, decimation,bandwidth):
        
        self.bandwidth=bandwidth
        self.decimation=decimation
        
        err=self.sighound.saConfigIQ(self.handle, ctypes.c_int(decimation), ctypes.c_double(bandwidth))
        self.check_for_error(err, "saConfigIQ")

    def IQ(self, length):
        
        self.iqPurge = ctypes.c_int(0) # we discard all previous data
        self.iqDataRemaining = ctypes.c_int(0) # we leave 0 data remaining
        self.iqSampleLoss = ctypes.c_int(0)
        self.secondsRemaining = ctypes.c_int(0)
        self.millisecondsRemaining = ctypes.c_int(0)
                
        self.iqarraySize = ctypes.c_int(length) #size of the array 
        self.iqArr = np.zeros(2*length,dtype="float32") #iq array 
                
        self.saIQPacketData = IQPacketData(self.iqArr.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                                   self.iqarraySize,
                                   self.iqPurge,
                                   self.iqDataRemaining,
                                   self.iqSampleLoss,
                                   self.secondsRemaining,
                                   self.millisecondsRemaining)
                
                
        
                
                
                
        err=self.sighound.saGetIQData(self.handle,ctypes.pointer(self.saIQPacketData))
                
                
    def IQ_second(self,length_IQ):
        
        
     
        self.iqData = np.zeros(length_IQ,dtype="float32") #iq array
        self.iqCount=ctypes.c_int(length_IQ)
        self.purge=ctypes.c_int(self.hf.sa_TRUE)
        
        self.dataRemaining=ctypes.c_int()
        self.sampleLoss=ctypes.c_int()
        self.sec=ctypes.c_int()
        self.milli=ctypes.c_int()
    
        
        IQ_array=self.iqData.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        self.min.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        
        err=self.sighound.saGetIQDataUnpacked(self.handle, 
                                              IQ_array,
                                              self.iqCount,
                                              self.purge, 
                                              ctypes.byref(self.dataRemaining), 
                                              ctypes.byref(self.sampleLoss),
                                              ctypes.byref(self.sec),
                                              ctypes.byref(self.milli))
        self.check_for_error(err, "saGetIQDataUnpacked")
        
    def check_for_error(self,err,source):
        # check if there is an error 
        if err != self.err.saNoError:
            print("During {}, the error {} was raised".format(source,err))
            
   