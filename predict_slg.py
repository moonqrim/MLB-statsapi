import pandas as pd
import statsapi
from tqdm import tqdm
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

def search_gamePk_by_year(year):
    yearlst = []
    search = statsapi.get('season', {'sportId': 1, 'seasonId': year})['seasons'][0]  # '2023'
    start_game_date = search['seasonStartDate']
    end_game_date = search['seasonEndDate']

    for year in tqdm(statsapi.schedule(start_date=start_game_date, end_date=end_game_date)):
        yearlst.append(year['game_id'])

    return yearlst

def make_frame(yearlst):
    cols = ['angle', 'velo', 'pitch_speed_start', 'pitch_speed_end', 'pitch_break_angle', 'pitch_spin_rate',
            'pitch_break_length', 'pitch_breakY', 'pitch_break_vertical', 'pitch_break_vertical_induced',
            'pitch_extension', 'pitch_spin_direction', 'total_distance', 'slg']
    df = pd.DataFrame(columns=cols)
    df_lst = []

    for gamePk in tqdm(yearlst):
        for all_play in statsapi.get('game_playByPlay', {'gamePk': gamePk})['allPlays']:
            try:
                event_type = all_play['result']['event']
                slg_value = {'Single': 1.0, 'Double': 2.0, 'Triple': 3.0, 'Home Run': 4.0}.get(event_type, 0)

                play_data = {
                    'angle': all_play['playEvents'][-1]['hitData']['launchAngle'],
                    'velo': all_play['playEvents'][-1]['hitData']['launchSpeed'],
                    'pitch_speed_start': all_play['playEvents'][-1]['pitchData']['startSpeed'],
                    'pitch_speed_end': all_play['playEvents'][-1]['pitchData']['endSpeed'],
                    'pitch_break_angle': all_play['playEvents'][-1]['pitchData']['breaks']['breakAngle'],
                    'pitch_spin_rate': all_play['playEvents'][-1]['pitchData']['breaks']['spinRate'],
                    'pitch_break_length': all_play['playEvents'][-1]['pitchData']['breaks']['breakLength'],
                    'pitch_breakY': all_play['playEvents'][-1]['pitchData']['breaks']['breakY'],
                    'pitch_break_vertical': all_play['playEvents'][-1]['pitchData']['breaks']['breakVertical'],
                    'pitch_break_vertical_induced': all_play['playEvents'][-1]['pitchData']['breaks'][
                        'breakVerticalInduced'],
                    'pitch_extension': all_play['playEvents'][-1]['pitchData']['extension'],
                    'pitch_spin_direction': all_play['playEvents'][-1]['pitchData']['breaks']['spinDirection'],
                    'total_distance': all_play['playEvents'][-1]['hitData']['totalDistance'],
                    'slg': slg_value
                }
                df_lst.append(pd.DataFrame(play_data, index=[0]))

            except KeyError:
                pass

    df = pd.concat(df_lst, ignore_index=True)

    return df

def predict_slg(data): # ver 1.0 alpha
    df = data
    val = df[['angle', 'velo', 'pitch_speed_start', 'pitch_speed_end',
              'pitch_break_angle', 'pitch_spin_rate', 'pitch_break_length',
              'pitch_break_vertical', 'pitch_break_vertical_induced',
              'pitch_extension', 'pitch_spin_direction']]

    target = df['slg']

    # split
    X_train, X_test, y_train, y_test = \
        train_test_split(val, target, test_size=0.15, random_state=42)

    # model fit
    model = xgb.XGBRegressor()
    model.fit(X_train, y_train)

    # prediction
    pred = model.predict(X_test)

    # estimate
    mse = mean_squared_error(y_test, pred)
    print(f"Mean Squared Error: {mse}")
    xgb.plot_importance(model)

yearlst = search_gamePk_by_year('2023')
df = make_frame(yearlst)
predict_slg(df)
