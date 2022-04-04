import plotly.express as px
# import plotly.io as pio
# pio.renderers.default = 'png'

def simple_flightplan(flightpairs):
    fig = px.timeline(flightpairs, x_start='ETA', x_end='SDT', y='AC_REG')
    fig.update_yaxes(autorange='reversed')
    fig.show()