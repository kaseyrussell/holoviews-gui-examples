# Run with 
# bokeh serve --show <name>
import pandas as pd
import panel as pn
import holoviews as hv
from holoviews.streams import Buffer
from bokeh.models import Button, Slider, Spinner
import time
import asyncio
from fake_instrument import FakeInstrument  # replace this with whatever you're trying to communicate with

#
# Initialize your instrument
#
instrument = FakeInstrument()

#
# Make a buffer to hold the instrument data. You could get by without making a Pandas Dataframe, but it does a good
# job of handling things like writing to a csv file.
#
def make_df(time_sec=0.0, temperature_degC=0.0):
    return pd.DataFrame({'Time (s)': time_sec, 'Temperature (°C)': temperature_degC}, index=[0])

#
# Initialize the plot. Holoviews handles all of the plotting and makes some guesses about what columns to plot.
#
example_df = make_df()
buffer = Buffer(example_df, length=1000, index=False)
plot = hv.DynamicMap(hv.Curve, streams=[buffer]).opts(padding=0.1, width=600, xlim=(0, None))

#
# Define any other GUI components
#
button = Button(label="Start")
offset = Slider(title='Offset', start=-10.0, end=10.0, value=0.0, step=0.1)
interval = Spinner(title="Interval (sec)", value=0.1, step=0.01)

acquisition_task = None

async def acquire_data(interval_sec=0.1):
    t0 = time.time()
    while True:
        instrument.set_offset(offset.value)
        time_elapsed = time.time() - t0
        value = instrument.read_data()
        b = make_df(time_elapsed, value)
        buffer.send(b)
        time_spent_buffering = time.time() - t0 - time_elapsed
        if interval_sec > time_spent_buffering:
            await asyncio.sleep(interval_sec - time_spent_buffering)

def start_stop():
    global acquisition_task
    if button.label == 'Start':
        button.label = 'Stop'
        buffer.clear()
        acquisition_task = asyncio.get_running_loop().create_task(acquire_data(interval_sec=interval.value))
    else:
        button.label = 'Start'
        acquisition_task.cancel()

button.on_click(start_stop)
hv.extension('bokeh')
hv.renderer('bokeh').theme = 'caliber'
controls = pn.WidgetBox('# Controls',
                        interval,
                        button,
                        offset)
pn.Row(plot, controls).servable()

