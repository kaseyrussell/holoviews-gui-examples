# holoviews-gui-examples

Are you doing hardware automation? Let's say you need to quickly read out some temperature data from a 
[LabJack](https://labjack.com) or control a stepper motor. Building libraries to communicate with instruments 
is often trivial in Python, but making a GUI interface (especially with a plot) can be cumbersome using
standard GUI toolkits like Tk, Qt, or wxPython. 

The data science field has recently been building some amazing tools for interacting with data.
Compared to the standard GUI toolkits, these data science GUI toolkits are much more along the lines of what 
I typically need as a scientist and engineer.

This repo has a few example GUIs built using [Holoviews](http://holoviews.org) and 
[Bokeh](https://bokeh.org). These aren't drastically different than the examples in the guide to 
[Working with Streaming Data](http://holoviews.org/user_guide/Streaming_Data.html) in the Holoviews documentation,
but if you're not very familiar with Holoviews and DynamicMaps in particular, there are some meaningful
differences. Plotting multiple lines took me much longer than it should have, for example.

There's no actual hardware interaction here, but you could easily swap out the [fake_instrument.py](fake_instrument.py)
module and replace it with a module for communicating with a real piece of hardware. 

## Examples
1. [timeseries_plot_single_variable.py](timeseries_plot_single_variable.py)
![timeseries_plot_single_variable.py](screenshots/timeseries_plot_single_variable.gif)

## Setup
I'm assuming you're using Anaconda Python.

1. Clone this repo onto your computer
2. Open an Anaconda prompt and navigate to the folder that contains this README.md file.
3. To create a new environment with all the necessary packages, type this command at the Anaconda prompt:
`> conda env create -f environment.yml`
4. Activate the environment you just created by typing this command at the prompt:
`> conda activate holoviews-gui-examples'
5. Try out one of the examples. Running this command should open a new browser tab with the GUI in it:
`> bokeh serve --show timeseries_plot_single_variable.py`

