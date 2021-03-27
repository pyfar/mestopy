import pytest
from pyfar.testing.stub_utils import signal_stub


@pytest.fixture
def flat_freq():
    """Flat frequency signal stub.

    Returns
    -------
    signal : Signal
        Stub of flat freq signal
    """
    time = [1, 0, 0, 0, 0, 0, 0, 0]
    freq = [1, 1, 1, 1]
    sampling_rate = 44100
    fft_norm = 'none'
    signal = signal_stub(time, freq, sampling_rate, fft_norm)
    return signal
