# --------------------------------------------
# Imports
# --------------------------------------------
from shiny import reactive, render,req
from shiny.express import input, ui, render
import random
from datetime import datetime
from collections import deque
import pandas as pd
import plotly.express as px
from shinywidgets import render_plotly, render_widget, output_widget
from scipy import stats
from faicons import icon_svg
import faicons as fa

# --------------------------------------------
# Constants
# --------------------------------------------
UPDATE_INTERVAL_SECS: int = 3
DEQUE_SIZE: int = 5
reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))

# --------------------------------------------
# Reactive Calculation
# --------------------------------------------
@reactive.calc()
def reactive_calc_combined():
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)
    temp = round(random.uniform(-18, -16), 1)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_entry = {"temp": temp, "timestamp": timestamp}
    reactive_value_wrapper.get().append(new_entry)
    deque_snapshot = reactive_value_wrapper.get()
    df = pd.DataFrame(deque_snapshot)
    return deque_snapshot, df, new_entry

# --------------------------------------------
# UI Layout
# --------------------------------------------
ui.page_opts(title="PyShiny Express: Live Data Example", fillable=True)

# Sidebar
with ui.sidebar(open="open"):
    ui.h2("Antarctic Explorer", class_="text-center")
    ui.p("Real-time temperature readings in Antarctica.", class_="text-center")
    ui.hr()
    ui.h6("Links:")
    ui.a("GitHub Source", href="https://github.com/denisecase/cintel-05-cintel", target="_blank")
    ui.a("GitHub App", href="https://denisecase.github.io/cintel-05-cintel/", target="_blank")
    ui.a("PyShiny", href="https://shiny.posit.co/py/", target="_blank")
    ui.a("PyShiny Express", href="https://shiny.posit.co/blog/posts/shiny-express/", target="_blank")

# Main Panel
with ui.layout_columns():
    with ui.value_box(showcase=icon_svg("sun"), theme="bg-gradient-blue-purple"):
        "Current Temperature"
        @render.text
        def display_temp():
            _, _, latest_entry = reactive_calc_combined()
            return f"{latest_entry['temp']} C"
        "warmer than usual"

    with ui.card(full_screen=True):
        ui.card_header("Current Date and Time")
        @render.text
        def display_time():
            _, _, latest_entry = reactive_calc_combined()
            return f"{latest_entry['timestamp']}"

with ui.card(full_screen=True):
    ui.card_header("Most Recent Readings")
    @render.data_frame
    def display_df():
        _, df, _ = reactive_calc_combined()
        pd.set_option('display.width', None)
        return render.DataGrid(df, width="100%")

with ui.card():
    ui.card_header("Chart with Current Trend")
    @render_plotly
    def display_plot():
        _, df, _ = reactive_calc_combined()
        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            fig = px.scatter(df, x="timestamp", y="temp", title="Temperature Readings with Regression Line",
                             labels={"temp": "Temperature (°C)", "timestamp": "Time"}, color_discrete_sequence=["blue"])
            x_vals = range(len(df))
            y_vals = df["temp"]
            slope, intercept, _, _, _ = stats.linregress(x_vals, y_vals)
            df['best_fit_line'] = [slope * x + intercept for x in x_vals]
            fig.add_scatter(x=df["timestamp"], y=df['best_fit_line'], mode='lines', name='Regression Line')
            fig.update_layout(xaxis_title="Time", yaxis_title="Temperature (°C)")
        return fig

