from scipy.signal import oaconvolve
from pyfar import Signal


# Class to generate ref-Objects, that can bei part of the MeasurementChain
class Device(object):
    """Class for device in MeasurementChain.

    This class holds methods and properties of a device in the
    'MeasurementChain' class. A device can be e.g., a sound card or a
    pre-amplifier, described by a frequency response and/or sensitivity.
    """

    def __init__(self, name, data=None, sens=1, unit=None):
        """Init Device with data.

        Attributes
        ----------
        name : str
            Name of the device.
        data : Signal, None, optional
            Signal data that reprensets the inversed frequency response of
            the device. The default is None, in this case a perfect flat
            frequency response is assumed and only sensitivity as a factor
            is applied.
            Caution: Avoid large gains in the frequency responses because
            they will boost measurement noise and might cause numerical
            instabilities. One possibility to avoid this is to use
            regularized inversion.
        sens : float, optional
            Sensitivity of the device as a factor. If neither device_data nor
            sens is given, add_device generates a device that has no effect to
            the measurement chain as it has no frequency response and a
            sesitivity (factor) default of 1.
        unit : str, optional
            The phyiscal unit of the device, e.g., mV/Pa.
        """
        self.name = name
        self.data = data
        self.sens = sens
        self.unit = unit

    @property
    def name(self):
        """The name of the device"""
        return self._name

    @name.setter
    def name(self, name):
        if not isinstance(name, str):
            raise ValueError('Device name must be string.')
        else:
            self._name = name

    @property
    def data(self):
        """The freqeuncy dependent data, representing the device."""
        return self._data

    @data.setter
    def data(self, data):
        if not isinstance(data, (Signal, type(None))):
            raise TypeError('Input data must be type Signal or None.')
        else:
            self._data = data

    @property
    def sens(self):
        """The sensitivity of the device."""
        return self._sens

    @sens.setter
    def sens(self, sens):
        if not isinstance(sens, (int, float)):
            raise ValueError('Sensitivity must be a number (int or float).')
        else:
            self._sens = sens

    @property
    def unit(self):
        """The unit of the sensitivity."""
        return self._unit

    @unit.setter
    def unit(self, unit):
        if not (isinstance(unit, str) or unit is None):
            raise ValueError('Unit of sensitivity must be string or None.')
        else:
            self._unit = unit

    @property
    def freq(self):
        """Return the inverted frequency multiplied by the sensitivity as a signal,
            or the sensitivity as scalar, when the device has no frequency
            response.
        """
        if self.data is not None:
            return self.data * self.sens
        else:
            return self.sens

    def __repr__(self):
        """String representation of Device class."""
        if self.data is None:
            repr_string = (
                f"{self.name} defined by "
                f"sensitivity={self.sens} unit={self.unit}\n")
        else:
            repr_string = (
                f"{self.name} defined by {self.data.n_bins} freq-bins, "
                f"sensitivity={self.sens} unit={self.unit}\n")
        return repr_string


# Class for MeasurementChain as frame for Devices
class MeasurementChain(object):
    """Class for complete measurement chain.

    This class holds methods and properties of all devices in the
    measurement chain. It can include a single or multiple objects of
    the Device class.
    """

    def __init__(self,
                 sampling_rate,
                 sound_device=None,
                 devices=None,
                 comment=None):
        """Init measurement chain with sampling rate.

        Attributes
        ----------
        sampling_rate : double
            Sampling rate in Hertz.
        sound_device : int
            Number to identify the sound device used. The default is None.
        devices : list
            A list of Device objects. The default is an empty list.
        comment : str
            A comment related to the measurement chain. The default is None.
        """
        self.sampling_rate = sampling_rate
        self.sound_device = sound_device
        self.comment = comment
        if isinstance(devices, type(None)):
            self.devices = []
        else:
            for dev in devices:
                if not isinstance(dev, Device):
                    raise TypeError('Input data must be type Device.')
                if dev.data is None:
                    continue
                if not dev.data.sampling_rate == self.sampling_rate:
                    raise ValueError("Sampling rate of device does not agree "
                                     "with the measurement chain.")
            self.devices = devices
        self._freq()

    def _find_device_index(self, name):
        """Private method to find the index of a given device name."""
        for i, dev in enumerate(self.devices):
            if dev.name == name:
                return i
        raise ValueError(f"device {name} not found")

    def _freq(self):
        """Private method to calculate the frequency response of the complete
        measurement chain and save it to the private attribute _resp."""
        if self.devices == []:
            resp = 1.0
        else:
            resp = [[1.0]]
            for dev in self.devices:
                if isinstance(dev.freq, Signal):
                    resp = oaconvolve(resp, dev.freq.time)
                else:
                    resp = oaconvolve(resp, [[dev.freq]])
            resp = Signal(resp, self.sampling_rate, domain='time')
            resp.domain = 'freq'
        self._resp = resp

    def add_device(self,
                   name,
                   data=None,
                   sens=1,
                   unit=None
                   ):
        """Adds a new device to the measurement chain.

        Refer to the documentation of Device class.

        Attributes
        ----------
        name : str
        data : pyfar.Signal, optional
        sens : float, optional
        unit : str, optional
        """
        # check if device_data is type Signal or None
        if not isinstance(data, (Signal, type(None))):
            raise TypeError('Input data must be type Signal or None.')
        # check if there are no devices in measurement chain
        if not self.devices == []:
            # check if sampling_rate of new device and MeasurementChain
            # is the same
            if data is not None:
                if not self.sampling_rate == data.sampling_rate:
                    raise ValueError("Sampling rate of the new device does"
                                     "not agree with the measurement chain.")
        # add device to chain
        new_device = Device(name, data=data,
                            sens=sens, unit=unit)
        self.devices.append(new_device)
        self._freq()

    def list_devices(self):
        """Returns a list of names of all devices in the measurement chain.
        """
        # list all ref-objects in chain
        device_names = []
        for dev in self.devices:
            name = dev.name
            device_names.append(name)
        return device_names

    def remove_device(self, num):
        """Removes a single device from the measurement chain,
         by name or number.

        Attributes
        ----------
        num : int or str
            Identifier for device to remove. Device can be found by name as
            string or by number in device list as int.
        """
        # remove ref-object in chain position num
        if isinstance(num, int):
            self.devices.pop(num)
        # remove ref-object in chain by name
        elif isinstance(num, str):
            self.remove_device(self._find_device_index(num))
        else:
            raise TypeError("device to remove must be int or str")
        self._freq()

    # reset complete ref-object-list
    def reset_devices(self):
        """Resets the list of devices in the measurement chain.
        Other global parameters such as sampling rate or sound device of the
        measurement chain remain unchanged.
        """
        self.devices = []
        self._freq()

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
            return self.devices[num].freq
        elif isinstance(num, str):
            return self.device_freq(self._find_device_index(num))
        else:
            raise TypeError("Device must be called by int or str.")

    # get the freq-response of whole measurement chain as pyfar.Signal
    @property
    def freq(self):
        """Returns the frequency response of the complete measurement chain.
        All devices (frequency response and sensitivity) are considered.
        """
        return self._resp

    def __repr__(self):
        """String representation of MeasurementChain class.
        """
        repr_string = (
            f"measurement chain with {len(self.devices)} devices "
            f"@ {self.sampling_rate} Hz sampling rate.\n")
        for i, dev in enumerate(self.devices):
            repr_string = f"{repr_string}# {i:{2}}: {dev}"
        return repr_string
