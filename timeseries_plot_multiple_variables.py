# Run with 
# bokeh serve --show timeseries_plot_multiple_variables.py
import pandas as pd
import panel as pn
import holoviews as hv
from holoviews.streams import Buffer
from bokeh.models import Button, Slider, Spinner, Paragraph, TextInput
import time
import asyncio
from fake_instrument import FakeInstrument  # replace this with whatever you're trying to communicate with
from pathlib import Path

#
# Initialize your instruments
#
temperature1 = FakeInstrument()
temperature2 = FakeInstrument()

#
# Make a buffer to hold the temperature1 data. You could get by without making a Pandas Dataframe, but it does a good
# job of writing to a csv file.
#
def make_df(time_sec=0.0, temperature1_degC=0.0, temperature2_degC=0.0):
    return pd.DataFrame({'Time (s)': time_sec,
                         'Temperature #1 (°C)': temperature1_degC,
                         'Temperature #2 (°C)': temperature2_degC}, index=[0])

#
# Initialize the plot. Holoviews handles all of the plotting and makes some guesses about what columns to plot. Since
# we want to plot more than just col2 vs col1, we need to be explicit.
#
def build_plot(data):
    p1 = hv.Curve(data, 'Time (s)', 'Temperature #1 (°C)', label="Sensor #1")
    p2 = hv.Curve(data, 'Time (s)', 'Temperature #2 (°C)', label="Sensor #2")
    return (p1 * p2).opts(ylabel='Temperature (°C)')

example_df = pd.DataFrame(columns=make_df().columns)
buffer = Buffer(example_df, length=1000, index=False)
plot = hv.DynamicMap(build_plot, streams=[buffer]).opts(padding=0.1, width=600, xlim=(0, None))

#
# Define any other GUI components
#
LABEL_START = 'Start'
LABEL_STOP = 'Stop'
LABEL_CSV_START = "Save to csv"
LABEL_CSV_STOP = "Stop save"

button_startstop = Button(label=LABEL_START)
button_csv = Button(label=LABEL_CSV_START)
offset = Slider(title='Offset', start=-10.0, end=10.0, value=0.0, step=0.1)
interval = Spinner(title="Interval (sec)", value=0.1, step=0.01)
csv_filename_input = TextInput(title="CSV file name:", value="")
status = Paragraph()


#
# Define behavior
#
acquisition_task = None
csv_filename = None


#
# Here we're using a coroutine to handle getting the data from the temperature1 and plotting it without blocking
# the GUI. In my experience, this works fine if you are only trying to get data from your temperature1 once every
# ~50 ms or so. The buffering and plotting take on the order of 10-20 ms. If you need to communicate with your
# temperature1 on millisecond timescales, then you'll want a separate thread and maybe even separate hardware. And you
# won't want to update the plot with every single data point.
#
async def acquire_data(interval_sec=0.1):
    global csv_filename
    t0 = time.time()
    while True:
        temperature1.set_offset(offset.value)
        time_stamp = time.time()
        elapsed = time_stamp - t0
        b = make_df(elapsed, temperature1.read_data(), temperature2.read_data())
        buffer.send(b)

        if csv_filename is not None:
            b.to_csv(csv_filename, header=False, index=False, mode='a')

        time_spent_buffering = time.time() - time_stamp
        if interval_sec > time_spent_buffering:
            await asyncio.sleep(interval_sec - time_spent_buffering)


def validate_csv(attr, old, new):
    if Path(new).exists() and new != '':
        status.text = "File already exists!"
    else:
        status.text = ""


def toggle_csv():
    global csv_filename
    if button_csv.label == LABEL_CSV_START:
        if csv_filename_input.value is "":
            status.text = "No csv filename entered!"
            return
        if Path(csv_filename_input.value).exists():
            status.text = "File already exists!"
            return
        button_csv.label = LABEL_CSV_STOP
        csv_filename = csv_filename_input.value
        example_df.to_csv(csv_filename, index=False)  # example_df is empty, so this just writes the header
    else:
        csv_filename = None
        button_csv.label = LABEL_CSV_START


def start_stop():
    global acquisition_task, csv_filename
    if button_startstop.label == LABEL_START:
        button_startstop.label = LABEL_STOP
        buffer.clear()
        acquisition_task = asyncio.get_running_loop().create_task(acquire_data(interval_sec=interval.value))
    else:
        acquisition_task.cancel()
        button_startstop.label = LABEL_START
        if csv_filename is not None:
            toggle_csv()


button_startstop.on_click(start_stop)
button_csv.on_click(toggle_csv)
csv_filename_input.on_change('value_input', validate_csv)

hv.extension('bokeh')
hv.renderer('bokeh').theme = 'caliber'
controls = pn.WidgetBox('# Controls',
                        interval,
                        button_startstop,
                        csv_filename_input,
                        button_csv,
                        status)

pn.Row(plot, controls).servable()

