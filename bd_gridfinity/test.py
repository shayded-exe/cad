# %%
# !%load_ext autoreload
# !%autoreload 2

# %%
from ocp_vscode import *

import bd_gridfinity as gf
import bd_utils as bdu
from build123d import *

# %%
bdu.init_show()
# bdu.reset_camera()

# baseplate = gf.Baseplate(4, 2)
# baseplate = gf.BaseplateUnit()
# show_object(baseplate, name='baseplate')

# dovetail = gf.Dovetail()
# show_object(dovetail, name='dovetail')

# base = gf.BinBase(align=None)
# show_object(base, name='base')

bin = gf.Bin(
    x_units=2,
    y_units=1,
    align=None,
)
# bin.expo
show_object(bin, name="bin")

# show_all()
