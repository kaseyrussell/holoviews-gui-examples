# Run with 
# bokeh serve --show timeseries_plot_single_variable.py
import pandas as pd
import panel as pn
import holoviews as hv
from holoviews.streams import Buffer
from bokeh.models import Button, Slider, Spinner
import time
import asyncio
from fake_instrument import FakeInstrument  # replace this with whatever you're trying to communicate with

#
# Initialize your temperature monitor
#
instrument = FakeInstrument()

#
# Make a dataframe to hold the buffered data. You could get by without making a Pandas Dataframe, but it does a good
# job of writing to a csv file.
#
def make_df(time_sec=0.0, temperature_degC=0.0):
    return pd.DataFrame({'Time (s)': time_sec, 'Temperature (°C)': temperature_degC}, index=[0])

#
# Initialize the buffer and the plot.
# Holoviews handles all of the plotting and makes some guesses about what columns to plot.
#
example_df = pd.DataFrame(columns=make_df().columns)
buffer = Buffer(example_df, length=1000, index=False)
plot = hv.DynamicMap(hv.Curve, streams=[buffer]).opts(padding=0.1, width=600, xlim=(0, None))

#
# Define any other GUI components
#
LABEL_START = 'Start'
LABEL_STOP = 'Stop'
LABEL_CSV_START = "Save to csv"
LABEL_CSV_STOP = "Stop save"
CSV_FILENAME = 'tmp.csv'

button_startstop = Button(label=LABEL_START)
button_csv = Button(label=LABEL_CSV_START)
offset = Slider(title='Offset', start=-10.0, end=10.0, value=0.0, step=0.1)
interval = Spinner(title="Interval (sec)", value=0.1, step=0.01)


#
# Define behavior
#
acquisition_task = None
save_to_csv = False


#
# Here we're using a coroutine to handle getting the data from the instrument and plotting it without blocking
# the GUI. In my experience, this works fine if you are only trying to get data from your instrument once every
# ~50 ms or so. The buffering and plotting take on the order of 10-20 ms. If you need to communicate with your
# instrument on millisecond timescales, then you'll want a separate thread and maybe even separate hardware. And you
# won't want to update the plot with every single data point.
#
async def acquire_data(interval_sec=0.1):
    global save_to_csv
    t0 = time.time()
    while True:
        instrument.set_offset(offset.value)
        time_elapsed = time.time() - t0
        value = instrument.read_data()
        b = make_df(time_elapsed, value)
        buffer.send(b)

        if save_to_csv:
            b.to_csv(CSV_FILENAME, header=False, index=False, mode='a')

        time_spent_buffering = time.time() - t0 - time_elapsed
        if interval_sec > time_spent_buffering:
            await asyncio.sleep(interval_sec - time_spent_buffering)


def toggle_csv():
    global save_to_csv
    if button_csv.label == LABEL_CSV_START:
        button_csv.label = LABEL_CSV_STOP
        example_df.to_csv(CSV_FILENAME, index=False)  # example_df is empty, so this just writes the header
        save_to_csv = True
    else:
        save_to_csv = False
        button_csv.label = LABEL_CSV_START


def start_stop():
    global acquisition_task, save_to_csv
    if button_startstop.label == LABEL_START:
        button_startstop.label = LABEL_STOP
        buffer.clear()
        acquisition_task = asyncio.get_running_loop().create_task(acquire_data(interval_sec=interval.value))
    else:
        acquisition_task.cancel()
        button_startstop.label = LABEL_START
        if save_to_csv:
            toggle_csv()


button_startstop.on_click(start_stop)
button_csv.on_click(toggle_csv)

hv.extension('bokeh')
hv.renderer('bokeh').theme = 'caliber'
controls = pn.WidgetBox('# Controls',
                        interval,
                        button_startstop,
                        button_csv,
                        offset)

pn.Row(plot, controls).servable()

