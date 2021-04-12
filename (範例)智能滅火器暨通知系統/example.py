# source from https://pynq.readthedocs.io/en/v2.6.1/pynq_libraries/audio.html
from pynq.overlays.base import BaseOverlay

base = BaseOverlay("base.bit")
pAudio = base.audio
pAudio.set_volume(20)
pAudio.load("/home/xilinx/jupyter_notebooks/base/audio/data/recording_0.wav")
pAudio.play()