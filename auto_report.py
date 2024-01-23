import statsapi
import matplotlib.pyplot as plt
import numpy as np

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

    ax[0].barh(df, away, align='center', color='crimson', zorder=10)
    ax[0].set(title=boxscore['teamInfo']['away']['shortName'])

    ax[1].barh(df, home, align='center', color='lightgrey', zorder=10)
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

gamePk = search_game_id(143, '07/01/2018')
# sample
# 143 : PHI

auto_report(gamePk)