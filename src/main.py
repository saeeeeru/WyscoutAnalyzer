import os, itertools
import requests

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import streamlit as st
from PIL import Image

from viz_func import *
from utils import *

args = parse_args()

if args.env == "local":
    base_dir = os.path.join(".")
elif args.env == "heroku":
    base_dir = os.path.join('https://raw.githubusercontent.com','saeeeeru','WyscoutAnalyzer','develop')
else:
    exit(9)

# get image
image_path = os.path.join(base_dir, "assets", "profile.JPG")
md_path = os.path.join(base_dir, "assets", "PROFILE.md")
if args.env == "local":
    image = Image.open(image_path)
    with open(md_path, "r") as fi:
        profile_md = fi.read()
else:
    profile_md = requests.get(md_path).content.decode(encoding="utf-8")
    image = requests.get(image_path).content

# Use the full page instead of a narrow central column
st.beta_set_page_config(
        page_title="WyScoutAnalyzer",
        page_icon=image,
        layout="wide",
        initial_sidebar_state="expanded"
    )

data_dir = os.path.join(base_dir, 'data', 'raw')

competition_list = ['France', 'Spain', 'Germany', 'European_Championship', 'World_Cup', 'Italy', 'England']

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
def read_dfs(selected_competition):
    players_df = pd.read_json(os.path.join(data_dir, 'players.json'))
    teams_df = pd.read_json(os.path.join(data_dir, 'teams', f'teams_{selected_competition}.json'))

    # encode, decode
    players_df['shortName'] = players_df.shortName.apply(lambda x: x.encode('utf-8').decode('unicode-escape'))
    teams_df['name'] = teams_df.name.apply(lambda x: x.encode('utf-8').decode('unicode-escape'))
    
    return players_df, teams_df

st.sidebar.title('WyScoutAnalyzer via wyscout dataset')
st.sidebar.markdown("")

selected_competition = st.sidebar.selectbox('Which League/Tournament do you select?', competition_list)

players_df, teams_df = read_dfs(selected_competition)

viz_mode = st.sidebar.radio("Which Analytics Summary do you check??", ('Each Match', 'Each Team'))

st.sidebar.markdown("")
st.sidebar.markdown("")
st.sidebar.image(image, caption="@saeeeeru", use_column_width=True)
st.sidebar.info(profile_md)
st.sidebar.markdown("")
st.sidebar.markdown("")

@st.cache(allow_output_mutation=True)
def read_events_df(selected_competition, wyId_list):
    events_df = pd.concat([pd.read_json(os.path.join(data_dir, 'events', selected_competition, f'{wyId}.json')) for wyId in wyId_list])
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

    c_list = ['home_team_name', 'away_team_name', 'home_team_score', 'away_team_score']
    for c in c_list:
        matches_df[c] = np.zeros(len(matches_df))
    matches_df[c_list] = [list(itertools.chain.from_iterable([v.split(' @')[0].split(' - ') for v in name.split(', ')[:2]])) for name in matches_df.name.tolist()]

    return matches_df.sort_values('date_time')

def main():
    matches_df = read_matches_df(selected_competition)
    
    if viz_mode == 'Each Match':
        name_list = matches_df.name.tolist()
        match_expander = st.beta_expander('Expand match select box')
        with match_expander:
            selected_match = st.selectbox('Which Match do you want to see data?', name_list)

        selected_wyId = matches_df[matches_df.name == selected_match].wyId.values[0]
        events_df = read_events_df(selected_competition, [selected_wyId])

        col_list = st.beta_columns(3)
        with col_list[0]:
            st.header('match summary')
            st.table(
            # st.dataframe(
                create_match_summary_df(events_df[events_df.matchId==selected_wyId], teams_df)
                .style
                # .set_table_styles([{'selector': 'td', 'props': [('font-size', '20pt')]}])
                .set_properties(**{'max-width': '80px', 'font-size': '15pt'})
                .apply(highlight_max, axis=1)
                )

        create_detail_events_df(events_df, teams_df, col_list[1:])

        col_list = st.beta_columns(2)
        with col_list[0]:
            matchPeriod_list = st.multiselect('Which Half do you want to see data?', ['1H', '2H'])

        with col_list[1]:
            library = st.selectbox('Which Library do you want to visualize?', ['matplotlib(faster)', 'plotly(slowly, but detail)'])

        try:
            df_tmp = events_df[(events_df.eventName=='Shot')&(events_df.matchPeriod.isin(matchPeriod_list))]
            st.header('shot point')
            vizualize_shot_points(df_tmp, teams_df, players_df, matchPeriod_list, library.split('(')[0])

            st.header('pass map')

            subEventName_list = events_df[events_df.eventName=='Pass'].subEventName.unique().tolist()
            df_tmp = events_df[(events_df.eventName=='Pass')&(events_df.matchPeriod.isin(matchPeriod_list))]
            visualize_pass_lines(df_tmp, teams_df, players_df, subEventName_list, matchPeriod_list, library.split('(')[0])

        except Exception:
            st.error('please select 1H / 2H')

    elif viz_mode == 'Each Team':
        # teams_df
        team_list = teams_df.name.tolist()
        selected_team_list = st.multiselect('Which Team do you want to see data?', team_list)
        teamId_list = teams_df[teams_df.name.isin(selected_team_list)].wyId.tolist()

        if len(selected_team_list) != 0:
            matchId_list = np.unique(list(itertools.chain.from_iterable([matches_df[matches_df.name.str.contains(selected_team)].wyId.tolist() for selected_team in selected_team_list]))).tolist()
            events_df = read_events_df(selected_competition, matchId_list)

            st.header('team summary')
            st.table(
                create_team_summary_df(events_df[events_df.teamId.isin(teamId_list)], matches_df, teams_df, selected_team_list)
                # .style
                # .set_table_styles([{'selector': 'td', 'props': [('font-size', '20pt')]}])
                # .set_properties(**{'max-width': '80px', 'font-size': '15pt'})
                # .apply(highlight_max, axis=1)
                )
            st.header('goal time')
            visualize_score_time_summary(events_df[events_df.teamId.isin(teamId_list)], teams_df)
            st.header("pass sonars")
            visualize_pass_sonars(events_df[events_df.teamId.isin(teamId_list)&(events_df.eventName=='Pass')], teams_df)
            st.header("ball hunt")
            visualize_ball_hunt(events_df[events_df.teamId.isin(teamId_list)], teams_df)
        else:
            st.error('Please select teams you want to analyze !!')


if __name__ == '__main__':
    main()