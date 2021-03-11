import numpy as np
from pyfar import Signal


# Class to generate ref-Objects, that can bei part of the MeasurementChain
class DeviceObj(object):
    """Class for device in MeasurementChain.

    This class holds methods and properties of a device in the
    'MeasurementChain' class.
    """

    def __init__(self, data, sens=1, name=''):
        """Init DeviceObj with data.

        Attributes
        ----------
        data : Signal
            Signal with the inverted frequency response of the device.
        sens : float
            Sensitivity of the device as a factor.
        name : str
            Name of the device.
        """
        self.sens = sens
        self.name = name
        self.data = data

    @property
    def freq(self):
        """Return the frequency responses of the device, multiplied by
        the sensitivity.
        """
        return self.data * self.sens

    @property
    def device_name(self):
        """Return the name of the device as string."""
        return self.name

    @device_name.setter
    def device_name(self, new_name):
        """Set the name of the device."""
        self.name = new_name

    def __repr__(self):
        """String representation of DeviceObj class."""
        repr_string = (
            f"{self.name} defined by {self.data.n_bins} freq-bins, "
            f"sensitivity={self.sens}\n")
        return repr_string


# Class for MeasurementChain as frame for RefObjs and calibration
class MeasurementChain(object):
    """Class for complete measurement chain.

    This class that holds methods and properties of all devices in the
    measurement chain. It can include a single or multiple devices from
    'DeviceObj' class.
    """

    def __init__(self,
                 sampling_rate,
                 sound_device=None,
                 devices=[],
                 comment=None):
        """Init measurement chain with rampling rate.

        Attributes
        ----------
        sampling_rate : double
            Sampling rate in Hertz.
        sound_device : int
            Number to identify the sound device used. The default is None.
        devices : list
            A list of instances from 'DeviceObj' class. The default is an
            empty list.
        comment : str
            A comment related to the measurement chain. The default is None.
        """
        self.sampling_rate = sampling_rate
        self.sound_device = sound_device
        self.devices = devices
        self.comment = comment

    def add_device(self,
                   device_data=None,
                   sens=1,
                   device_name=''):
        """Adds a new device to the measurement chain.

        Attributes
        ----------
        device_data : Signal, optional
            Signal data that reprensets the inverted frequency response of the
            device to add. The default is None, in this case a perfect flat
            frequency response is assumed and only sensitivity as
            a factor is applied.
            Caution: Make sure to use frequency responses without artefacts,
            as they will influence the quality of compensations calculated with
            the measurement chain. Most ideal this should be regularized
            inverted frequency responses. Data can be in domain 'freq' or
            'time' and will be transformed if necessary.
        sens : float, optional
            Sensitivity of the device as a factor. If neither device_data nor
            sens is given, add_device generates a device that has no effect to
            the measurement chain as it has no frequency response and a
            sesitivity (factor) of 1.
        device_name : str, optional
            The name of the new device to add to the masurement chain.
            The default is an empty string.
        """
        if device_data is None:
            device_data = Signal(np.full(int(self.sampling_rate/2), 1.0),
                                 self.sampling_rate,
                                 domain='freq')
        # check if ref_signal is a pyfar.Signal, if not raise Error
        if not isinstance(device_data, Signal):
            raise TypeError('Input data must be of type: Signal.')
        # check if there are no devices in measurement chain
        if self.devices == []:
            # add ref-measurement to chain
            device_data.domain = 'freq'
            new_device = DeviceObj(device_data,
                                   sens,
                                   device_name)
            self.devices.append(new_device)
        else:
            # check if n_bins of all devices is the same
            if not self.devices[0].data.n_bins == device_data.n_bins:
                raise ValueError("ref_signal has wrong n_bins")
            # check if sampling_rate of new device and MeasurementChain
            # is the same
            if not self.sampling_rate == device_data.sampling_rate:
                raise ValueError("ref_signal has wrong samping_rate")
            # add device to chain
            new_device = DeviceObj(device_data,
                                   sens,
                                   device_name)
            self.devices.append(new_device)

    def list_devices(self):
        """Returns a list of names of all devices in the measurement chain.
        """
        # list all ref-objects in chain
        device_names = []
        for dev in self.devices:
            name = dev.device_name
            device_names.append(name)
        return device_names

    def remove_device(self, num):
        """Removes a single device from the measurement chain,
         by name or number.

        Attributes
        ----------
        num : int or str
        Identifier for device to remove. Device can be found by name as string
        or by number in device list as int.
        """
        # remove ref-object in chain position num
        if isinstance(num, int):
            front = self.devices[:num]
            back = self.devices[num+1:]
            for i in back:
                front.append(i)
            self.devices = front
        # remove ref-object in chain by name
        elif isinstance(num, str):
            i = 0
            for dev in self.devices:
                if dev.name == num:
                    self.remove_device(i)
                    return
                i = i + 1
            raise ValueError(f"device {num} not found")
        else:
            raise TypeError("device to remove must be int or str")

    # reset complete ref-object-list
    def reset_devices(self):
        """Resets the list of devices in the measurement chain.
        Other global parameters such as sampling rate or sound device of the
        measurement chain remain unchanged.
        """
        self.devices = []

    # get the freq-response of specific device in measurement chain
    def device_freq(self, num):
        """Returns the frequency response of a single device from the
        measurement chain, by name or number.

        Attributes
        ----------
        num : int or str
        Identifier for device, can be name as string or by number
        in device list as int.
        """
        if isinstance(num, int):
            dev = self.devices[num].data * self.devices[num].sens
            dev.domain = 'freq'
            return dev
        elif isinstance(num, str):
            i = 0
            for dev in self.devices:
                if dev.name == num:
                    return self.device_freq(i)
                i = i + 1
            raise ValueError(f"device {num} not found")
        else:
            raise TypeError("device to remove must be int or str")

    # get the freq-response of whole measurement chain as pyfar.Signal
    def freq(self):
        """Returns the frequency response of the complete measurement chain.
        All devices (frequency response and sensitivity) are considered.
        """
        if self.devices != []:
            resp = Signal(np.ones(int(self.devices[0].data.n_bins)),
                          self.sampling_rate,
                          domain='freq',
                          fft_norm=self.devices[0].data.fft_norm,
                          dtype=self.devices[0].data.dtype)
            for dev in self.devices:
                resp = resp * dev.data * dev.sens
        else:
            resp = Signal(np.ones(self.sampling_rate), self.sampling_rate)
        return resp

    def __repr__(self):
        """String representation of MeasurementChain class.
        """
        repr_string = (
            f"measurement chain with {len(self.devices)} devices "
            f"@ {self.sampling_rate} Hz sampling rate.\n")
        i = 1
        for dev in self.devices:
            repr_string = f"{repr_string}# {i}: {dev}"
            i += 1
        return repr_string
