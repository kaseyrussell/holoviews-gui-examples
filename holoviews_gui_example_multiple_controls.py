# Run with 
# bokeh serve --show <name>
import numpy as np
import pandas as pd
import panel as pn
import holoviews as hv
from holoviews.streams import Buffer
from bokeh.io import curdoc
from bokeh.models import Button, Slider
from datetime import datetime
import asyncio
import streamz.dataframe
import hvplot.streamz

hv.extension('bokeh')
hv.renderer('bokeh').theme = 'caliber'
doc = curdoc()
global stop

button = Button(label="Start")
slider = Slider(title='Value', start=-1.0, end=1.0, value=0.0, step=0.01)

def make_df(time, x):
    x = [x] if type(x) is float else x
    return pd.DataFrame({'Time': time, 'x': x}).set_index('Time')

example_df = make_df(0.0, np.zeros(0))
buffer = Buffer(example_df.loc[:, ['x']], length=1000)
plot = hv.DynamicMap(hv.Curve, streams=[buffer]).opts(padding=0.1, width=600, xlim=(0, None))

#
# fake instrument
# 
def read_from_sensor():
    return np.random.random()

async def acquire_data(start_time):
    global stop
    while True:
        if stop:
            return
        duration = (datetime.now() - start_time).total_seconds()
        value = read_from_sensor()
        value += 10 * slider.value
        b = make_df(duration, value)
        buffer.send(b.loc[:, ['x']])
        await asyncio.sleep(0.1)

def start_stop():
    global stop
    if button.label == 'Start':
        button.label = 'Stop'
        buffer.clear()
        stop = False
        t0 = datetime.now()
        asyncio.get_running_loop().create_task(acquire_data(t0))
    else:
        stop = True
        button.label = 'Start'

button.on_click(start_stop)
pn.Row(pn.panel(plot),
        pn.panel(pn.WidgetBox('# Controls', button, slider))).servable()

