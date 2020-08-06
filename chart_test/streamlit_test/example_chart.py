import streamlit as st
import numpy as np
import pandas as pd
import chart_ipynb as cpy
from chart_ipynb import time_series
import urllib
from datetime import time, datetime
from IPython.display import display
import altair as alt
import streamlit.components.v1 as components

@st.cache
def get_data():
    url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv'
    df = pd.read_csv(url)
    return df.set_index("state")

try:
    df = get_data()
except urllib.error.URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
    """
        % e.reason
    )

@st.cache
def get_state_data(data, state, start=None, end=None):
    """
    data: pd.DataFrame
    state: a str of state or a list of states
    """
    if start is None:
        start = data.iloc[0].date
    if end is None:
        end = data.iloc[-1].date
    data = data[(data.date >= start) & (data.date <= end)]
    states = data.reset_index().groupby('state')
    if isinstance(state, str):
        state = [state]
    state_data = dict()
    for s in state:
        idx = states.groups[s]
        state_data[s] = data.iloc[idx].reset_index(drop=True)
    return state_data

def draw_chart(chart_type, states, col, input_datasets):
    chart = time_series.time_series_Chart(chart_type, states, col, date_col = 'date', 
                        data_provide = True, title = 'Covid-19 - %s chart'%chart_type,
                        input_dataset = input_dataset)
    input_config = str(chart.config)
    html_datasets="["
    for i in range(len(states)):
        data_html = ""
        if i != len(states)-1:
            data_html = """
                {label: '%s',
                data: %s,
                backgroundColor: '%s',
                borderColor: '%s',
                fill: false, 
                type: '%s', 
                pointRadius: 0, 
                lineTension: 0, 
                borderWidth: 1},
            """%(states[i],str(chart.datasets[i]['data']),
            chart.datasets[i]['backgroundColor'],chart.datasets[i]['borderColor'],chart_type)
        else:
            data_html = """
                {label: '%s',
                data: %s,
                backgroundColor: '%s',
                borderColor: '%s',
                fill: false, 
                type: '%s', 
                pointRadius: 0, 
                lineTension: 0, 
                borderWidth: 1}
            """%(states[i],str(chart.datasets[i]['data']),chart.datasets[i]['backgroundColor'],chart.datasets[i]['borderColor'],chart_type)
        html_datasets += data_html
    html_datasets += "]"
    html_script = """
    <head>
	<title>Line Chart</title>
	<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.9.3/Chart.min.js"></script>
    </head>

    <body>
        <canvas id="myChart" width="800" height="500"></canvas>
        <script>
            var ctx = document.getElementById('myChart');
            var myChart = new Chart(ctx, {
                type: '%s', 
                data: {
                    datasets: %s,
                    labels: %s
                }, 
                options: {
                    responsive: true, 
                    title: {
                        display: true, 
                        text: '%s'
                        }, 
                    animation: {duration: 0}, 
                    tooltips: {mode: 'index', intersect: false}, 
                    scales: {
                        xAxes: {display: true, 
                                scaleLabel: {display: true, labelString: 'Date'}, 
                                stacked: false, 
                                ticks: {
                                    major: {
                                        enabled: true, fontStyle: 'bold'
                                    }, source: 'data'}
                        }, 
                        yAxes: [{
                            display: true, 
                            scaleLabel: {
                                display: true, 
                                labelString: '%s'
                                }, 
                            stacked: false, 
                            gridLines: {drawBorder: false}
                        }]
                    }
                }
            });
        </script>
    </body>
    """%(chart_type,html_datasets, str(chart.labels),chart.title, col)
    return html_script

states = st.multiselect(
        "Choose countries", list(set(df.index)), ["New York"]
    )
date_time = sorted(list(set(df['date'].values)))
date = st.slider('Select a range of date', value=(datetime.strptime(date_time[0],'%Y-%m-%d'), datetime.strptime(date_time[-1],'%Y-%m-%d')))
start = date[0].strftime("%Y-%m-%d")
end = date[-1].strftime("%Y-%m-%d")
col = st.selectbox('Which statistic you would like to see?', ('cases','deaths'))
if not states:
    st.error("Please select at least one country.")
elif not col:
    st.error("Please select a column.")
else:
    data = get_state_data(df.reset_index(), states, start, end)
    input_dataset = [data[s] for s in states]
    html_script = draw_chart('line', states, col, input_dataset)
    components.html(html_script,width=800, height=600)
    # test_html = """
    # <head>
	# <title>Line Chart</title>
	# <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.9.3/Chart.min.js"></script>
    # </head>

    # <body>
    #     <canvas id="myChart" width="800" height="400"></canvas>
    #     <script>
    #         var ctx = document.getElementById('myChart');
    #         var myChart = new Chart(ctx, {
    #             type: 'line', 
    #             data: {
    #                 datasets:[{
    #                     data: [1, 1, 2, 11, 22, 44, 89, 106, 142, 173, 217, 326, 421, 610, 732, 950, 1375, 2387, 4161, 7113, 10371, 15188, 20899, 25704, 33117, 39058, 44746, 53517, 59783, 67504, 76211, 84364, 93360, 103689, 115963, 124085, 133389, 141703, 151271, 162036, 172830, 182990, 191425, 197973, 205375, 217130, 225761, 233293, 240542, 246741, 251608, 255932, 261591, 267932, 276218, 286901, 292914, 296991, 300276, 304994, 309696, 313575, 318134, 321833, 324357, 326659, 329405, 332931, 335804, 338519, 340657, 342267, 343705, 345828, 348192, 350951, 353136, 355037, 356278, 357757, 359235, 361313, 362991, 364745, 366346, 367625, 368669, 369801, 371559, 373108, 374471, 375575, 376520, 377881, 378924, 379977, 381019, 382102, 382879, 383591, 384281, 384945, 385669, 386490, 387402, 388096, 388719, 389349, 389910, 390536, 391330, 392037, 392702, 393257, 393855, 394430, 395168, 395972, 396669, 397293, 397684, 398142, 398770, 399642, 400561, 401286, 401822, 402338, 402928, 403619, 404207, 404997, 405724, 406403, 406962, 407875, 408709, 409476, 410254, 411006, 411515, 412034, 412889, 413595, 414405, 415163, 415911, 416443, 417056, 417591, 418302, 419081, 419723, 420477, 421008, 421550, 422296], 
    #                     label: 'New York', 
    #                     backgroundColor: 'red', 
    #                     borderColor: 'red', 
    #                     fill: false, 
    #                     type: 'line', 
    #                     pointRadius: 0, 
    #                     lineTension: 0, 
    #                     borderWidth: 1}], 
    #                 labels: ['2020-03-01', '2020-03-02', '2020-03-03', '2020-03-04', '2020-03-05', '2020-03-06', '2020-03-07', '2020-03-08', '2020-03-09', '2020-03-10', '2020-03-11', '2020-03-12', '2020-03-13', '2020-03-14', '2020-03-15', '2020-03-16', '2020-03-17', '2020-03-18', '2020-03-19', '2020-03-20', '2020-03-21', '2020-03-22', '2020-03-23', '2020-03-24', '2020-03-25', '2020-03-26', '2020-03-27', '2020-03-28', '2020-03-29', '2020-03-30', '2020-03-31', '2020-04-01', '2020-04-02', '2020-04-03', '2020-04-04', '2020-04-05', '2020-04-06', '2020-04-07', '2020-04-08', '2020-04-09', '2020-04-10', '2020-04-11', '2020-04-12', '2020-04-13', '2020-04-14', '2020-04-15', '2020-04-16', '2020-04-17', '2020-04-18', '2020-04-19', '2020-04-20', '2020-04-21', '2020-04-22', '2020-04-23', '2020-04-24', '2020-04-25', '2020-04-26', '2020-04-27', '2020-04-28', '2020-04-29', '2020-04-30', '2020-05-01', '2020-05-02', '2020-05-03', '2020-05-04', '2020-05-05', '2020-05-06', '2020-05-07', '2020-05-08', '2020-05-09', '2020-05-10', '2020-05-11', '2020-05-12', '2020-05-13', '2020-05-14', '2020-05-15', '2020-05-16', '2020-05-17', '2020-05-18', '2020-05-19', '2020-05-20', '2020-05-21', '2020-05-22', '2020-05-23', '2020-05-24', '2020-05-25', '2020-05-26', '2020-05-27', '2020-05-28', '2020-05-29', '2020-05-30', '2020-05-31', '2020-06-01', '2020-06-02', '2020-06-03', '2020-06-04', '2020-06-05', '2020-06-06', '2020-06-07', '2020-06-08', '2020-06-09', '2020-06-10', '2020-06-11', '2020-06-12', '2020-06-13', '2020-06-14', '2020-06-15', '2020-06-16', '2020-06-17', '2020-06-18', '2020-06-19', '2020-06-20', '2020-06-21', '2020-06-22', '2020-06-23', '2020-06-24', '2020-06-25', '2020-06-26', '2020-06-27', '2020-06-28', '2020-06-29', '2020-06-30', '2020-07-01', '2020-07-02', '2020-07-03', '2020-07-04', '2020-07-05', '2020-07-06', '2020-07-07', '2020-07-08', '2020-07-09', '2020-07-10', '2020-07-11', '2020-07-12', '2020-07-13', '2020-07-14', '2020-07-15', '2020-07-16', '2020-07-17', '2020-07-18', '2020-07-19', '2020-07-20', '2020-07-21', '2020-07-22', '2020-07-23', '2020-07-24', '2020-07-25', '2020-07-26', '2020-07-27', '2020-07-28', '2020-07-29', '2020-07-30', '2020-07-31', '2020-08-01', '2020-08-02', '2020-08-03', '2020-08-04']}, 
    #             options: {
    #                 responsive: true, 
    #                 title: {
    #                     display: true, 
    #                     text: 'Covid-19 Cases - line chart'
    #                     }, 
    #                 animation: {duration: 0}, 
    #                 tooltips: {mode: 'index', intersect: false}, 
    #                 scales: {
    #                     xAxes: {display: true, 
    #                             scaleLabel: {display: true, labelString: 'Date'}, 
    #                             stacked: false, 
    #                             ticks: {
    #                                 major: {
    #                                     enabled: true, fontStyle: 'bold'
    #                                 }, source: 'data'}
    #                     }, 
    #                     yAxes: [{
    #                         display: true, 
    #                         scaleLabel: {
    #                             display: true, 
    #                             labelString: 'cases'
    #                             }, 
    #                         stacked: false, 
    #                         gridLines: {drawBorder: false}
    #                     }]
    #                 }
    #             }
    #         });
    #     </script>
    # </body>
    # """
    # components.html(test_html, width=800, height=400)


    # data = df.iloc[df.index.isin(states)].reset_index()
    # data = data[(data["date"] >= start)&(data["date"] <= end)]
    # st.write(data)
    # chart = (
    #     alt.Chart(data)
    #     .mark_area(opacity=0.3)
    #     .encode(
    #         x="date:N",
    #         y=alt.Y("cases:Q", stack=None),
    #         color="state:N",
    #     )
    # )
    # st.altair_chart(chart, use_container_width=True)