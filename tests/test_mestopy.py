#!/usr/bin/env python

"""Tests for `mestopy` package."""

from mestopy import Device, MeasurementChain

from pyfar.testing.stub_utils import signal_stub
from pyfar import Signal

import numpy.testing as npt


def test_Device_init():
    """Test to init Device without optinal parameters."""
    dev = Device('dev1')
    assert isinstance(dev, Device)


def test_Device_default_parameter():
    """Test the default attributes after
    init Device without optinal parameters."""
    dev = Device('dev1')
    assert dev.name == 'dev1'
    assert dev.data is None
    assert dev.sens == 1
    assert dev.unit is None


def test_Device_name():
    """Test name setter and getter of Device class."""
    dev = Device('dev1')
    assert dev.name == 'dev1'
    dev.name = 'dev2'
    assert dev.name == 'dev2'


def test_Device_data():
    """Test data setter and getter of Device class
    with signal_stub."""
    dev = Device('dev1')
    assert dev.data is None
    time = [1, 0, 0, 0, 0, 0, 0, 0]
    freq = [1, 1, 1, 1]
    sampling_rate = 44100
    fft_norm = 'none'
    signal = signal_stub(time, freq, sampling_rate, fft_norm)
    dev.data = signal
    assert isinstance(dev.data, Signal)
    assert dev.data == signal


def test_Device_sens():
    """Test sens setter and getter of Device class."""
    dev = Device('dev1')
    assert dev.sens == 1
    dev.sens = 0.3
    assert dev.sens == 0.3


def test_Device_unit():
    """Test unit setter and getter of Device class."""
    dev = Device('dev1')
    assert dev.unit is None
    dev.unit = 'mV/Pa'
    assert dev.unit == 'mV/Pa'


def test_Device_freq():
    """Test freq getter of Device init with and without a Signal."""
    dev = Device('dev1')
    assert dev.freq == 1
    time = [1, 0, 0, 0, 0, 0, 0, 0]
    freq = [1, 1, 1, 1]
    sampling_rate = 44100
    fft_norm = 'none'
    signal = signal_stub(time, freq, sampling_rate, fft_norm)
    dev = Device('dev1', signal)
    assert isinstance(dev.freq, type(signal * 1.0))
    assert dev.freq == dev.data * dev.sens


def test_MeasurementChain_init():
    """Test to init MeasurementChain without optinal parameters."""
    chain = MeasurementChain(44100)
    assert isinstance(chain, MeasurementChain)


def test_MeasurementChain_default_paramerter():
    """Test the default attributes after init
    MeasurementChain without optinal parameters."""
    chain = MeasurementChain(44100)
    assert chain.devices == []
    assert chain.freq == 1.0
    assert chain.sampling_rate == 44100
    assert chain.sound_device is None
    assert chain.comment is None


def test_MeasurementChain_add_device():
    """Test add_device method of MeasurementChain class."""
    chain = MeasurementChain(44100)
    assert len(chain.devices) == 0
    chain.add_device('dev1')
    assert len(chain.devices) == 1
    chain.add_device('dev2')
    assert len(chain.devices) == 2


def test_MeasurementChain__find_device_index():
    """Test private _find_device_index method of
    MeasurementChain class."""
    chain = MeasurementChain(44100)
    chain.add_device('dev1')
    chain.add_device('dev2')
    chain.add_device('dev3')
    assert chain._find_device_index('dev2') == 1


def test_MeasurementChain__freq():
    """Test private _freq method of MeasurementChain class."""
    chain = MeasurementChain(44100)
    assert chain._resp == 1.0
    chain.add_device('dev1', sens=2.0)
    assert isinstance(chain._resp, Signal)
    assert chain._resp.n_samples == 1
    assert chain._resp.time[0] == 2.0


def test_MeasurementChain_list_devices():
    """Test list_devices method of MeasurementChain class."""
    chain = MeasurementChain(44100)
    assert chain.list_devices() == []
    chain.add_device('dev1')
    chain.add_device('dev2')
    chain.add_device('dev3')
    assert chain.list_devices() == ['dev1', 'dev2', 'dev3']


def test_MeasurementChain_remove_device():
    """Test remove_device method of MeasurementChain class.
    Test with nuber and name as argument."""
    chain = MeasurementChain(44100)
    chain.add_device('dev1')
    chain.add_device('dev2')
    chain.add_device('dev3')
    # by number
    chain.remove_device(0)
    assert chain.list_devices() == ['dev2', 'dev3']
    # by name
    chain.remove_device('dev3')
    assert chain.list_devices() == ['dev2']


def test_MeasurementChain_reset_devices():
    """Test reset_devices method of MeasurementChain class."""
    chain = MeasurementChain(44100)
    chain.add_device('dev1')
    chain.add_device('dev2')
    chain.add_device('dev3')
    chain.reset_devices()
    assert chain.list_devices() == []


def test_MeasurementChain_device_freq():
    """Test device_freq method of MeasurementChain class with
    devices init with only sens, but no freq-data.
    Test with nuber and name as argument."""
    chain = MeasurementChain(44100)
    chain.add_device('dev1', sens=1.0)
    chain.add_device('dev2', sens=2.0)
    chain.add_device('dev3', sens=3.0)
    # by number
    assert chain.device_freq(1) == 2.0
    # by name
    assert chain.device_freq('dev3') == 3.0


def test_MeasurementChain_freq():
    """Test freq getter of MeasurementChain class with pyfar.Signal."""
    freq = [1, 1, 1, 1]
    sampling_rate = 44100
    signal = Signal(freq, sampling_rate, domain='freq')
    chain = MeasurementChain(sampling_rate)
    sens1 = 2
    sens2 = 3
    chain.add_device('dev1', sens=sens1)
    chain.add_device('dev2', data=signal, sens=sens2)
    assert chain.freq.n_bins == 4
    npt.assert_equal(chain.freq.freq, signal.freq*sens1*sens2)
