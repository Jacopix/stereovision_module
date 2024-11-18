import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider, TextBox
import matplotlib.gridspec as gridspec


# Axis options
MAX_X = 20000   # [mm]
MAX_Y = 1500      # [mm]

# ZED 2i stereocamera (model 1)
#
# Error expectations: 
#   < 0.8% @ 2m
#   < 4.0% @ 12m    
# init_p_width    = 2     # um
# init_p_heigth   = 2     # um
# init_s_width    = 2688  # pixels
# init_s_heigth   = 1520  # pixels
# init_hfov       = 110    # degrees
# init_baseline   = 120   # mm
# init_disparity  = 1     # pixels

# ZED 2i stereocamera (model 2)
#
# Error expectations: 
#   < 0.4% @ 2m
#   < 7.0% @ 20m    
init_p_width    = 2     # um
init_p_heigth   = 2     # um
init_s_width    = 2688  # pixels
init_s_heigth   = 1520  # pixels
init_hfov       = 72    # degrees
init_baseline   = 120   # mm
init_disparity  = 1     # pixels

# Gemini 335/336
#
# Error expectations: 
#   < 1% @ 2m considering 81% of RegionOfInteres === 64% of FOV  
# init_p_width    = 2     # um
# init_p_heigth   = 2     # um
# init_s_width    = 1280  # pixels
# init_s_heigth   = 800  # pixels
# init_hfov       = 57.6    # degrees (nominal is 90°, considering 64% -> 57.6°)
# init_baseline   = 50   # mm
# init_disparity  = 1     # pixels

# sensor size (diagonal) function [px]
def get_diag_px(s_width, s_heigth):
    return np.sqrt( pow(s_width,2) + pow(s_heigth,2) )

# sensor size (diagonal) function [mm]
def get_diag_mm(s_width, s_heigth, p_width, p_heigth):
    return np.sqrt( pow(s_width * p_width * pow(10,-6) , 2) + pow(s_heigth * p_heigth * pow(10,-6) , 2))
    
# focal length function [px]
def get_focal_length_px(s_width, s_heigth, hfov):
    diag = get_diag_px(s_width, s_heigth)
    return diag / ( 2 * np.tan( ( hfov * np.pi / 180 ) / 2 ) )

# focal length function [mm]
def get_focal_length_mm(s_width, s_heigth, p_width, p_heigth, hfov):
    diag = get_diag_mm(s_width, s_heigth, p_width, p_heigth)
    return diag / ( 2* np.tan( ( hfov * np.pi / 180 ) / 2 ) ) * pow(10 , 3)

# Error estimation function
def d_z(z, disparity_step, baseline, focal_length):
    return (pow(z,2) * disparity_step) / (baseline * focal_length + z * disparity_step)


# Set up the graph
z = np.linspace(0, MAX_X, 100)
fig, ax = plt.subplots(figsize=(12,8))
line, = ax.plot(z, d_z(z, init_disparity, init_baseline, get_focal_length_px(init_s_width, init_s_heigth, init_hfov)), lw=2)
plt.xlim(0,MAX_X)
plt.ylim(0,MAX_Y)
ax.set_xlabel('Depth [mm]')
ax.set_ylabel('Error [mm]')


# Set up space for other widgets 
fig.subplots_adjust(bottom=0.4)
gs_boxes = gridspec.GridSpec(8,1, wspace=2)
gs_sliders = gridspec.GridSpec(1,1, wspace=2)
gs_boxes.update(left=0.2, right=0.5, bottom=0.01, top=0.3, hspace=1,)
gs_sliders.update(left=0.7, right=0.9, bottom=0.01, top=0.1, hspace=1,)

# create textboxes
p_width         = TextBox(fig.add_subplot(gs_boxes[0,0]), 'pixel width [um]', hovercolor='0.975', label_pad=0.1)
p_heigth        = TextBox(fig.add_subplot(gs_boxes[1,0]), 'pixel heigth [um]', hovercolor='0.975', label_pad=0.1)
s_width         = TextBox(fig.add_subplot(gs_boxes[2,0]), 'sensor width [px]', hovercolor='0.975', label_pad=0.1)
s_heigth        = TextBox(fig.add_subplot(gs_boxes[3,0]), 'sensor heigth [px]', hovercolor='0.975', label_pad=0.1)
hfov            = TextBox(fig.add_subplot(gs_boxes[4,0]), 'hfov [deg]', hovercolor='0.975', label_pad=0.1)
disparity       = TextBox(fig.add_subplot(gs_boxes[5,0]), 'disparity step [px]', hovercolor='0.975', label_pad=0.1)
focal_length_mm = TextBox(fig.add_subplot(gs_boxes[6,0]), 'focal length [mm]', hovercolor='0.975', label_pad=0.1)
focal_length_px = TextBox(fig.add_subplot(gs_boxes[7,0]), 'focal length [px]', hovercolor='0.975', label_pad=0.1)

textboxes = [p_width, p_heigth, s_width, s_heigth, hfov, disparity, focal_length_mm, focal_length_px]


# create slider
baseline = Slider(
    ax=fig.add_subplot(gs_sliders[0,0]),
    label='Baseline [mm]',
    valmin=0,
    valstep=1,
    valmax=300,
    valinit=init_baseline,
)


# The function to be called anytime a value changes in textboxes or slider
def update(val):
    # Get data
    val_p_width    = float(p_width.text)
    val_p_heigth   = float(p_heigth.text)
    val_s_width    = float(s_width.text)
    val_s_heigth   = float(s_heigth.text)
    val_hfov       = float(hfov.text)
    val_disparity  = float(disparity.text)

    # Calculate and set focal length [px]
    val_fl_px = get_focal_length_px(val_s_width, val_s_heigth, val_hfov)
    focal_length_px.set_val(str(val_fl_px))

    # Calculate and set focal length [mm]
    val_fl_mm = get_focal_length_mm(val_s_width, val_s_heigth, val_p_width, val_p_heigth, val_hfov)
    focal_length_mm.set_val(str(val_fl_mm))

    # Draw graph
    line.set_ydata(d_z(z, val_disparity, baseline.val, val_fl_px))
    fig.canvas.draw_idle()

# Register the update function with each slider or text box
baseline.on_changed(update)
for textbox in textboxes:
    textbox.on_text_change(update)

# Fill with initial values
p_width.set_val( init_p_width )
p_heigth.set_val( init_p_heigth )
s_width.set_val( init_s_width )
s_heigth.set_val( init_s_heigth )
hfov.set_val( init_hfov )
disparity.set_val( init_disparity )
update("")


# Get info with mouse
def format_coord(x, y):
    val_s_width    = float(s_width.text)
    val_s_heigth   = float(s_heigth.text)
    val_hfov       = float(hfov.text)
    val_disparity  = float(disparity.text)
    
    # Calculate Focal Length [px]
    z_error = round(d_z(x, val_disparity, baseline.val, get_focal_length_px(val_s_width, val_s_heigth, val_hfov)), 2)
    z_error_perc = round(100*(z_error/x), 2)

    return "Depth: %dmm | Error [mm]: %.3fmm | Error [%%]: %.3f"%(x,z_error,z_error_perc)
ax.format_coord = format_coord

# Show everything
plt.show()