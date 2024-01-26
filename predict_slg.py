import pandas as pd
import statsapi

def search_gamePk_by_year(year):
    yearlst = []
    search = statsapi.get('season', {'sportId': 1, 'seasonId': year})['seasons'][0]  # '2023'
    start_game_date = search['seasonStartDate']
    end_game_date = search['seasonEndDate']

    for year in statsapi.schedule(start_date=start_game_date, end_date=end_game_date):
        yearlst.append(year['game_id'])

    return yearlst

def make_frame(yearlst):
    cols = ['angle', 'velo', 'pitch_speed_start', 'pitch_speed_end', 'pitch_break_angle', 'pitch_spin_rate',
            'pitch_break_length', 'pitch_breakY', 'pitch_break_vertical', 'pitch_break_vertical_induced',
            'pitch_extension', 'pitch_spin_direction', 'total_distance', 'slg']
    df = pd.DataFrame(columns=cols)

    for gamePk in yearlst:
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
                df = df.append(play_data, ignore_index=True)

            except KeyError:
                pass

    return df



yearlst = search_gamePk_by_year('2023')
df = make_frame(yearlst)