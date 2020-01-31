import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import streamlit as st

from viz_func import vizualize_shot_points, visualize_pass_lines
from utils import *

base_dir = os.path.join('..')
data_dir = os.path.join(base_dir, 'data', 'raw')

def highlight_max(data, color='yellow'):
    '''
    highlight the maximum in a Series or DataFrame
    '''
    attr = 'background-color: {}'.format(color)
    if data.ndim == 1:  # Series from .apply(axis=0) or axis=1
        is_max = data == data.max()
        return [attr if v else '' for v in is_max]
    else:  # from .apply(axis=None)
        is_max = data == data.max().max()
        return pd.DataFrame(np.where(is_max, attr, ''),
                            index=data.index, columns=data.columns)

@st.cache
def read_dfs():
    players_df = pd.read_json(os.path.join(data_dir, 'players.json'))
    teams_df = pd.read_json(os.path.join(data_dir, 'teams.json'))

    # encode, decode
    players_df['shortName'] = players_df.shortName.apply(lambda x: x.encode('utf-8').decode('unicode-escape'))
    teams_df['name'] = teams_df.name.apply(lambda x: x.encode('utf-8').decode('unicode-escape'))
    
    return players_df, teams_df

players_df, teams_df = read_dfs()

st.title('WyScoutAnalyzer via wyscout dataset')

competition_list = [infile.replace('matches_','').replace('.json','') for infile in os.listdir(os.path.join(data_dir, 'matches')) if infile.endswith('.json')]
selected_competition = st.sidebar.selectbox('Which League/Tournament do you select?', competition_list)

@st.cache
def read_events_df(selected_competition):
    events_df = pd.read_json(os.path.join(data_dir, 'events', f'events_{selected_competition}.json'))
    return events_df

@st.cache
def read_matches_df(selected_competition):
    matches_df = pd.read_json(os.path.join(data_dir, 'matches', f'matches_{selected_competition}.json'))
    matches_df['date_time'] = pd.to_datetime(matches_df.dateutc)

    # encode, decode
    matches_df['label'] = matches_df.label.apply(lambda x: x.encode('utf-8').decode('unicode-escape'))
    matches_df['venue'] = matches_df.venue.apply(lambda x: x.encode('utf-8').decode('unicode-escape'))

    # concate label, venue, date_time
    matches_df['name'] = matches_df[['label', 'venue', 'date_time']].apply(lambda xs: f'{xs[0]} @{xs[1]}, {xs[2].date()}', axis=1)

    return matches_df.sort_values('date_time')

def main():
    matches_df = read_matches_df(selected_competition)

    name_list = matches_df.name.tolist()
    selected_match = st.selectbox('Which Match do you want to see data?', name_list)

    selected_wyId = matches_df[matches_df.name == selected_match].wyId.values[0]

    events_df = read_events_df(selected_competition)
    # events_df[events_df.matchId == selected_wyId]

    st.header('match summary')
    st.table(create_match_summary_df(events_df[events_df.matchId==selected_wyId], teams_df).style.apply(highlight_max, axis=1))

    st.header('detail event summary')
    create_detail_events_df(events_df[events_df.matchId==selected_wyId], teams_df)

    matchPeriod_list = st.multiselect('Which Half do you want to see data?', ['1H', '2H'])

    library = st.selectbox('Which Library do you want to visualize?', ['matplotlib(faster)', 'plotly(slowly, but detail)'])

    try:
        df_tmp = events_df[(events_df.matchId == selected_wyId)&(events_df.eventName=='Shot')&(events_df.matchPeriod.isin(matchPeriod_list))]
        st.header('shot point')
        vizualize_shot_points(df_tmp, teams_df, players_df, matchPeriod_list, library.split('(')[0])

        st.header('pass map')

        subEventName_list = events_df[events_df.eventName=='Pass'].subEventName.unique().tolist()
        df_tmp = events_df[(events_df.matchId==selected_wyId)&(events_df.eventName=='Pass')&(events_df.matchPeriod.isin(matchPeriod_list))]
        visualize_pass_lines(df_tmp, teams_df, players_df, subEventName_list, matchPeriod_list, library.split('(')[0])

    except Exception:
        st.error('please select 1H / 2H')

if __name__ == '__main__':
    main()