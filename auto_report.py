import statsapi
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

def search_game_id(team, date):
    game = statsapi.schedule(start_date=date, team=team)
    gamePk = game[0]['game_id']
    home = game[0]['home_id']
    away = game[0]['away_id']
    return gamePk

def auto_report(gamePk):
    boxscore = statsapi.boxscore_data(gamePk)

    away_hits = boxscore['away']['teamStats']['batting']['hits']

    away_rbi = boxscore['away']['teamStats']['batting']['rbi']
    away_hrs = boxscore['away']['teamStats']['batting']['homeRuns']
    away_stolen = boxscore['away']['teamStats']['batting']['stolenBases']
    away_so = boxscore['away']['teamStats']['batting']['strikeOuts']
    away_lob = boxscore['away']['teamStats']['batting']['leftOnBase']

    home_hits = boxscore['home']['teamStats']['batting']['hits']
    home_rbi = boxscore['home']['teamStats']['batting']['rbi']
    home_hrs = boxscore['home']['teamStats']['batting']['homeRuns']
    home_stolen = boxscore['home']['teamStats']['batting']['stolenBases']
    home_so = boxscore['home']['teamStats']['batting']['strikeOuts']
    home_lob = boxscore['home']['teamStats']['batting']['leftOnBase']

    cols = ['H', 'RBI', 'HR', 'SB', 'SO', 'LOB']
    away = np.array([away_hits, away_rbi, away_hrs, away_stolen, away_so, away_lob])
    home = np.array([home_hits, home_rbi, home_hrs, home_stolen, home_so, home_lob])

    df = np.arange(away.size)

    fig, ax = plt.subplots(ncols=2, sharey=True)

    ax[0].barh(df, away, align='center', color='lightgrey', zorder=10)
    ax[0].set(title=boxscore['teamInfo']['away']['shortName'])

    ax[1].barh(df, home, align='center', color='crimson', zorder=10)
    ax[1].set(title=boxscore['teamInfo']['home']['shortName'])

    ax[0].set(yticks=df, yticklabels=cols)
    ax[0].yaxis.tick_right()
    ax[0].set_xlim([0,25])
    ax[1].set_xlim([0,25])
    ax[0].invert_xaxis()

    ax[0].spines['top'].set_visible(False)
    ax[0].spines['right'].set_visible(False)
    ax[0].spines['left'].set_visible(False)
    ax[0].spines['bottom'].set_visible(False)

    ax[1].spines['top'].set_visible(False)
    ax[1].spines['right'].set_visible(False)
    ax[1].spines['left'].set_visible(False)
    ax[1].spines['bottom'].set_visible(False)

    fig.set_figheight(2)
    fig.tight_layout()
    fig.subplots_adjust(wspace=0.165)
    fig.show()


def win_proba_per_game(gamePk):
    home_added_prob, color, time = [], [], []

    for proba in statsapi.get('game_winProbability', {'gamePk' : gamePk}):
        home_added_prob.append(proba['homeTeamWinProbability'] - proba['awayTeamWinProbability'])
        time_str = proba['about']['startTime']
        time.append(datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%fZ'))
        point_color = 'crimson' if (proba['homeTeamWinProbability']-proba['awayTeamWinProbability']) > 0 else ('lightgrey' if (proba['homeTeamWinProbability']-proba['awayTeamWinProbability']) < 0 else 'darkgrey')
        color.append(point_color)

    fig = go.Figure()
    for i in range(len(time)):
         fig.add_trace(
             go.Scatter(
                 x=[time[i]], y=[home_added_prob[i]], mode='markers+lines',
                 line=dict(color=color[i]), text=[f'{home_added_prob[i]:.2f}']
                 )
             )

    fig.update_layout(
        yaxis=dict(range=[-105, 105]),
        xaxis=dict(showline=False, showticklabels=False),
        title='Win Probability',
        plot_bgcolor='white',
        showlegend=False
    )
    fig.add_hline(y=0,line_width=1, line_dash="dash",line_color="grey")
    fig.show()


def time_line(gamePk):
    fig, ax = plt.subplots()

    inn_lst = statsapi.get('game', {'gamePk': gamePk})['liveData']['linescore']['innings']
    for i, inn in enumerate(inn_lst):
        away_runs = inn['away']['runs']
        away_lobs = inn['away']['leftOnBase']
        home_runs = inn['home']['runs'] * -1
        home_lobs = inn['home']['leftOnBase'] * -1

        away_total = away_runs + away_lobs
        home_total = home_runs + home_lobs

        ax.bar(
            i, away_runs, width=0.4, label=f'Away - {inn["num"]}',
            color='darkgrey', edgecolor='black'
        )
        ax.bar(
            i, away_total, width=0.4, label=f'Away - {inn["num"]}', bottom=away_runs,
            color='lightgrey', edgecolor='black', alpha=0.3
        )

        ax.bar(
            i, home_runs, width=0.4, label=f'Home - {inn["num"]}',
            color='crimson', edgecolor='black'
        )
        ax.bar(
            i, home_total, width=0.4, label=f'Home - {inn["num"]}', bottom=home_runs,
            color='lightgrey', edgecolor='black', alpha=0.3
        )

        if away_total != 0:
            ax.text(i, away_total + 1, str(away_total), ha='center', va='bottom', color='black')
            if away_runs != 0:
                ax.text(i, away_runs + 1, str(away_runs), ha='center', va='bottom', color='black')
        if home_total != 0:
            ax.text(i, (home_total + 1), str(home_total * -1), ha='center', va='bottom', color='black')
            if home_runs != 0:
                ax.text(i, (home_runs + 1), str(home_runs * -1), ha='center', va='bottom', color='black')

    ax.set_xticks(range(len(inn_lst)))
    ax.set_xticklabels([str(inn['num']) + "'s" for inn in inn_lst])
    ax.set_yticklabels([])

    legend_color_mapping = {
        'Away runs': 'darkgrey',
        'Home runs': 'crimson',
        'left on base': 'lightgrey'
    }

    handles = [plt.Rectangle((0, 0), 1, 1, color=legend_color_mapping[label]) for label in legend_color_mapping.keys()]
    ax.legend(handles, legend_color_mapping.keys(), loc=(1.0, 1.0), fontsize=6)

    plt.show()



gamePk = search_game_id(143, '07/01/2018')
# sample
# 143 : PHI

auto_report(gamePk)
win_proba_per_game(gamePk)
time_line(gamePk)