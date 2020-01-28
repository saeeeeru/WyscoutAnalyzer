import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import streamlit as st

from matplotlib.lines import Line2D

from utils import *

cmap = plt.get_cmap('tab10')

XMAX, XMIN = 120, 0
YMAX, YMIN = 80, 0

base_dir = os.path.join('..')
data_dir = os.path.join(base_dir, 'data', 'raw')

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

matches_df = read_matches_df(selected_competition)

name_list = matches_df.name.tolist()
selected_match = st.selectbox('Which Match do you want to see data?', name_list)

selected_wyId = matches_df[matches_df.name == selected_match].wyId.values[0]

events_df = read_events_df(selected_competition)
# events_df[events_df.matchId == selected_wyId]

matchPeriod_list = st.multiselect('Which Half do you want to see data?', ['1H', '2H'])

library = st.selectbox('Which Library do you want to visualize?', ['matplotlib', 'plotly'])

try:
    df_tmp = events_df[(events_df.matchId == selected_wyId)&(events_df.eventName=='Shot')&(events_df.matchPeriod.isin(matchPeriod_list))]
    st.header('shot point')

    if library == 'matplotlib':
        fig, axes = draw_pitches_matplotlib(nrows=len(matchPeriod_list), ncols=2)
        for i, (matchPeriod, teamId) in enumerate(df_tmp[['matchPeriod', 'teamId']].drop_duplicates().sort_values(by=['teamId', 'matchPeriod']).values.tolist()):
            ax = axes.reshape([-1, 2])[int(i/2), i%2]
            team_name = teams_df[teams_df.wyId==teamId].name.values[0]
            ax.set_title(f'{matchPeriod} {team_name}', color='white')
            
            for (positions, tags) in df_tmp[(df_tmp.matchPeriod==matchPeriod)&(df_tmp.teamId==teamId)][['positions', 'tags']].values.tolist():
                id_list = [tag_dict['id'] for tag_dict in tags]
            
                st_x, st_y = XMAX * positions[0]['x'] / 100, YMAX * (1 - positions[0]['y'] / 100)
                
                ax.scatter(x=st_x, y=st_y, c = cmap(1) if 101 in id_list else cmap(0), label='success' if 101 in id_list else 'fail')

            if i == len(matchPeriod_list)*2-1:
                ax.legend([Line2D([0], [0], color=cmap(j)) for j in range(2)], ['success', 'failure'], loc='lower right')

        st.pyplot(fig, facecolor=fig.get_facecolor(), bbox_inches = 'tight')

    else:
        title_list = [f'{matchPeriod} {teams_df[teams_df.wyId==teamId].name.values[0]}' for [matchPeriod, teamId] in df_tmp[['matchPeriod', 'teamId']].drop_duplicates().sort_values(by=['teamId', 'matchPeriod']).values.tolist()]
        fig = draw_pitches_plotly(len(matchPeriod_list), 2, title_list)

        df_tmp['x'] = None
        df_tmp['y'] = None
        df_tmp[['x', 'y']] = df_tmp.apply(lambda xs: [XMAX*xs['positions'][0]['x']/100, YMAX*(1-xs['positions'][0]['y']/100)], result_type='expand', axis=1)

        df_tmp['result'] = df_tmp.apply(lambda xs: 'success' if 101 in [tag['id'] for tag in xs['tags']] else 'failure', axis=1)

        df_tmp['name'] = df_tmp.apply(lambda xs: 'player= '+players_df[players_df.wyId==xs['playerId']].shortName.tolist()[0]+'\n time= '+str(int(xs['eventSec']/60))+'m'+str(int(xs['eventSec']%60))+'s\n result= '+xs['result'], axis=1)

        legend_dict = {'success':0, 'failure':0}
        for i, (matchPeriod, teamId) in enumerate(df_tmp[['matchPeriod', 'teamId']].drop_duplicates().sort_values(by=['teamId', 'matchPeriod']).values.tolist()):
            i, j = int(i/2)+1, i%2+1
            for result in df_tmp[(df_tmp.matchPeriod==matchPeriod)&(df_tmp.teamId==teamId)].result.unique().tolist():
                fig.add_trace(
                    go.Scatter(
                        x=df_tmp[(df_tmp.matchPeriod==matchPeriod)&(df_tmp.teamId==teamId)&(df_tmp.result==result)].x.tolist()
                        , y=df_tmp[(df_tmp.matchPeriod==matchPeriod)&(df_tmp.teamId==teamId)&(df_tmp.result==result)].y.tolist()
                        , name=result
                        , mode='markers'
                        , marker=dict(color='orange' if result=='success' else 'skyblue')
                        , hovertext=df_tmp[(df_tmp.matchPeriod==matchPeriod)&(df_tmp.teamId==teamId)&(df_tmp.result==result)].name.tolist()
                        , showlegend= legend_dict[result] == 0
                    )
                    , row=i, col=j)
                legend_dict[result] += 1

        st.plotly_chart(fig)

    st.header('pass map')

    subEventName_list = events_df[events_df.eventName=='Pass'].subEventName.unique().tolist()
    df_tmp = events_df[(events_df.matchId==selected_wyId)&(events_df.eventName=='Pass')&(events_df.matchPeriod.isin(matchPeriod_list))]

    if library == 'matplotlib':
        fig, axes = draw_pitches_matplotlib(nrows=len(matchPeriod_list), ncols=2)
        for i, (matchPeriod, teamId) in enumerate(df_tmp[['matchPeriod', 'teamId']].drop_duplicates().sort_values(by=['teamId', 'matchPeriod']).values.tolist()):
            ax = axes.reshape([-1, 2])[int(i/2), i%2]
            team_name = teams_df[teams_df.wyId==teamId].name.values[0]
            ax.set_title(f'{matchPeriod} {team_name}', color='white')

            for (positions, subEventName, tags) in df_tmp[(df_tmp.eventName=='Pass')&(df_tmp.matchPeriod==matchPeriod)&(df_tmp.teamId==teamId)][['positions', 'subEventName', 'tags']].values.tolist():
                ed_x, ed_y = XMAX * positions[1]['x'] / 100, YMAX * (1 - positions[1]['y'] / 100)
                st_x, st_y = XMAX * positions[0]['x'] / 100, YMAX * (1 - positions[0]['y'] / 100)
                id_list = [tag_dict['id'] for tag_dict in tags]

                ax.annotate('', xy=[ed_x, ed_y], xytext=[st_x, st_y],
                        arrowprops=dict(shrink=0, width=0.5, headwidth=4, alpha=0.8,
                                        headlength=5, connectionstyle='arc3',
                                        facecolor=cmap(subEventName_list.index(subEventName)), edgecolor=cmap(subEventName_list.index(subEventName))
                                        , linestyle= 'solid' if 1801 in id_list else 'dashed'
                                       )

                       )

            for positions in df_tmp[(df_tmp.eventName=='Interruption')&(df_tmp.matchPeriod==matchPeriod)&(df_tmp.teamId==teamId)]['positions'].values.tolist():
                st_x, st_y = XMAX * positions[0]['x'] / 100, YMAX * (1 - positions[0]['y'] / 100)
                ax.scatter(x=st_x, y=st_y, c='white', s=100, marker='x')


            if i == len(matchPeriod_list)*2-1:
                ax.legend([Line2D([0], [0], color=cmap(j)) for j in range(len(subEventName_list))], subEventName_list, loc='lower right')

        st.pyplot(fig, facecolor=fig.get_facecolor(), bbox_inches = 'tight')

    else:
        df_tmp['st_x'] = None
        df_tmp['st_y'] = None
        df_tmp['ed_x'] = None
        df_tmp['ed_y'] = None

        df_tmp[['st_x', 'st_y', 'ed_x', 'ed_y']] = df_tmp.apply(lambda xs: [XMAX*xs['positions'][0]['x']/100, YMAX*(1-xs['positions'][0]['y']/100), XMAX*xs['positions'][1]['x']/100, YMAX*(1-xs['positions'][1]['y']/100)], result_type='expand', axis=1)

        df_tmp['result'] = df_tmp.apply(lambda xs: 'success' if 1801 in [tag['id'] for tag in xs['tags']] else 'failure', axis=1)
        df_tmp['name'] = df_tmp.apply(lambda xs: 'player= '+players_df[players_df.wyId==xs['playerId']].shortName.tolist()[0]+'\n time= '+str(int(xs['eventSec']/60))+'m'+str(int(xs['eventSec']%60))+'s\n subEventName= '+xs['subEventName']+'\n result= '+xs['result'], axis=1)
        
        legend_dict = dict(zip(subEventName_list, [0]*len(subEventName_list)))
        color_list = ['#1f77b4',
         '#ff7f0e',
         '#2ca02c',
         '#d62728',
         '#9467bd',
         '#8c564b',
         '#e377c2',
         '#7f7f7f',
         '#bcbd22',
         '#17becf']
        color_dict = dict(zip(subEventName_list, color_list[:len(subEventName_list)]))

        fig = draw_pitches_plotly(len(matchPeriod_list), 2, title_list)
        N = len(df_tmp)
        cnt = 0
        with st.spinner('Wait for it ...'):
            my_bar = st.progress(cnt) 
            for i, (matchPeriod, teamId) in enumerate(df_tmp[['matchPeriod', 'teamId']].drop_duplicates().sort_values(by=['teamId', 'matchPeriod']).values.tolist()):
                i += 1
                
                for (st_x, st_y, ed_x, ed_y, subEventName, result, name) in df_tmp[(df_tmp.matchPeriod==matchPeriod)&(df_tmp.teamId==teamId)][['st_x', 'st_y', 'ed_x', 'ed_y', 'subEventName', 'result', 'name']].values.tolist():
                    my_bar.progress(int((cnt+1)/N*100))
                    
                    fig.add_annotation(go.layout.Annotation(
                        captureevents=True,
                        hovertext=name,
                        x=ed_x,
                        y=ed_y,
                        xref=f'x{i}',
                        yref=f'y{i}',
                        axref=f'x{i}',
                        ayref=f'y{i}',
                        ax=st_x,
                        ay=st_y,
                        arrowhead=4,
                        arrowsize=2,
                        arrowcolor=color_dict[subEventName],
                        showarrow=True,
            #             showlegend=legend_dict[subEventName] == 0
                    ))
                    
                    legend_dict[subEventName] += 1
                    cnt += 1
        st.success("Done!!")
        st.plotly_chart(fig)
except Exception:
    st.error('please select 1H / 2H')
