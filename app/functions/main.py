# date density, time density,

import json
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import requests
import json
import math
import bar_chart_race

#data = json.load(open('data/StreamingHistory0.json')) + json.load(open('data/StreamingHistory1.json')) + json.load(open('data/StreamingHistory2.json'))
data = []

for i in range(4):
    data += json.load(open('/Users/yshen4/Desktop/MyData/endsong_' + str(i) + '.json'))

print (len(data))

def time(unformatted, scope):
    year = int(unformatted[0:4])
    month = int(unformatted[5:7])
    day = int(unformatted[8:10])
    hour = (int(unformatted[11:13]) - 8)
    if hour < 0:
        hour += 24
    minute = int(unformatted[14:16])

    if scope == "year":
        return year + month / 12 + day / 365 + hour / (365 * 24) + minute / (365 * 24 * 60)
    elif scope == "month":
        return month + day / 30.5 + hour / (30.5 * 24) + minute / (30.5 * 24 * 60)
    elif scope == "day":
        return day + hour / 24 + minute / (24 * 60)
    elif scope == "hour":
        return hour + minute / 60


def week_time(unformatted):
    year = int(unformatted[0:4])
    month = int(unformatted[5:7])
    day = int(unformatted[8:10])

    return datetime.datetime(year, month, day).weekday() + time(unformatted, 'hour') / 24


def hours_plot(tracks):
    hours = {'year':[], 'hour':[]}

    for track in tracks:
        if track['ms_played'] > 10000:
            year = math.trunc(time(track['ts'], 'year'))
            hour = time(track['ts'], 'hour')

            hours['year'].append(year)
            hours['hour'].append(hour)

    years = list(set(hours['year']))


    plots = sns.displot(data=hours, x='hour', row='year', kind='kde', bw_adjust=0.35, fill=True, height=len(years)/2, aspect = 3)

    sns.set(font='Helvetica')
    sns.despine(left=True)
    plots.set(ylabel=None)
    plots.set(yticks=[])
    plots.set_titles("{row_name}", y=0.5, x=0)
    plots.set(xticks=[0, 4, 8, 12, 16, 20, 24])
    plots.set_axis_labels('Hours of the Day')
    plots.fig.suptitle('Song Streaming End Time (24-hour) Density from Spotify Streaming History')

    for ax in plots.axes.flatten():
        ax.tick_params(labelbottom=True)


    plt.savefig('hours.png')
    plt.close()


def weekday_plot(tracks):
    week_times = []

    for track in tracks:
        if track['msPlayed'] > 10000:
            week_times.append(week_time(track['endTime']))

    sns.set_style('dark')
    ax1 = sns.kdeplot(x=week_times, bw_adjust=.2, fill=True)
    ax1.set(ylabel=None)
    ax1.set(yticks=[])
    plt.savefig('weekdays.png')
    plt.close()


def month_plot(tracks):
    months = []

    for track in tracks:
        if track['msPlayed'] > 10000:
            months.append(time(track['endTime'], 'month'))

    sns.set_style('dark')
    ax1 = sns.kdeplot(x=months, bw_adjust=.25, fill=True)
    ax1.set(ylabel=None)
    ax1.set(yticks=[])
    plt.savefig('months.png')
    plt.close()


def years_plot(tracks):
    years = []

    for track in tracks:
        if track['ms_played'] > 10000:
            years.append(time(track['ts'], 'year'))

    sns.set_style('dark')
    ax1 = sns.kdeplot(x=years, bw_adjust=.25, fill=True)
    ax1.set(ylabel=None)
    ax1.set(yticks=[])
    plt.savefig('years.png')
    plt.close()

def bar_race(tracks):
    d = {}

    all_dates = []
    all_artists = []
    for track in tracks:
        if track['ms_played'] > 5000:
            date = track['ts'][0:10]
            if date not in all_dates:
                all_dates.append(date)

            artist = track['master_metadata_album_artist_name']
            if artist not in all_artists:
                all_artists.append(artist)


    for track in tracks:
        if track['ms_played'] > 5000:
            artist = track['master_metadata_album_artist_name']
            date = track['ts'][0:10]

def bar_race_test():
    # d = [
    #     ['date', 'Belgium', 'China', 'France', 'Germany', 'USA'],
    #     ['2020-04-08', 2240, 3337, 10887, 2349, 14704],
    #     ['2020-04-09', 2523, 3339, 12228, 2607, 16553],
    #     ['2020-04-10', 3019, 3340, 13215, 2767, 18595],
    #     ['2020-04-11', 3346, 3343, 13851, 2894, 20471],
    #     ['2020    -04-12', 3600, 3343, 14412, 3022, 22032]
    #      ]

    d = {
        'date': ['2020-04-12', '2020-04-11', '2020-04-10', '2020-04-09', '2020-04-08'],
        'Belgium': [2240, 2524, 3019, 3346, 3600],
        'China': [3337, 3339, 3340, 3343,3343],
        'France': [10887, 12228, 13215, 13851, 14412],
        'Germany': [2349, 2607, 2767, 2894, 3022],
        'USA': [14704, 16553, 18595, 20471, 22032]
    }

    df = pd.DataFrame(d)

    bar_chart_race.bar_chart_race(df=df, filename='vid.mp4')

#hours_plot(data)
#weekday_plot(data)
#month_plot(data)
#years_plot(data)
bar_race_test()