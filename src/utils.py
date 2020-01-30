import numpy as np
import pandas as pd

import streamlit as st

def create_match_summary_df(df_tmp, teams_df):
    # スコア
    score_s = df_tmp[df_tmp.eventName=='Shot'].groupby('teamId').tags.agg(lambda xs: np.sum([[101 in [tag_dict['id'] for tag_dict in tags]] for tags in xs])) 

    penalty_s = df_tmp[df_tmp.subEventName=='Penalty'].groupby('teamId').tags.agg(lambda xs: np.sum([[101 in [tag_dict['id'] for tag_dict in tags]] for tags in xs])) 
    for i in penalty_s.index:
        score_s[i] += penalty_s[i]

    score_df = score_s.fillna('0').to_frame().T
    score_df.index = ['score']
    
    # シュート
    shot_s = df_tmp[df_tmp.eventName=='Shot'].groupby('teamId').size()

    penalty_s = df_tmp[df_tmp.subEventName=='Penalty'].groupby('teamId').size()
    for i in penalty_s.index:
        shot_s[i] += penalty_s[i]

    shot_df = shot_s.fillna('0').to_frame().T
    shot_df.index = ['number of shots']
    
    # パス本数
    pass_s = df_tmp[df_tmp.eventName=='Pass'].groupby('teamId').size()

    pass_df = pass_s.fillna('0').to_frame().T
    pass_df.index = ['number of passes']

    # パス成功率
    r_pass_s = df_tmp[df_tmp.eventName=='Pass'].groupby('teamId').tags.agg(lambda xs: np.sum([[1801 in [tag_dict['id'] for tag_dict in tags]] for tags in xs])) 

    r_pass_df = (r_pass_s.to_frame().T / pass_df.values * 100).astype(int)
    r_pass_df = r_pass_df.applymap(lambda x: f'{x: .2f}%')

    r_pass_df.index = ['pass success rate']
    
    # クリア数
    clear_s = df_tmp[df_tmp.subEventName=='Clearance'].groupby('teamId').size()

    clear_df = clear_s.fillna('0').to_frame().T
    clear_df.index = ['number of Clear']

    # ファール
    foul_s = df_tmp[df_tmp.subEventName=='Foul'].groupby('teamId').size()

    foul_df = foul_s.fillna('0').to_frame().T
    foul_df.index = ['number of Foul']
    
    # デュエル勝率
    r_duel_s = df_tmp[df_tmp.eventName=='Duel'].groupby('teamId').tags.agg(lambda xs:np.sum([np.sum([1801 in [tag_dict['id']] for tag_dict in tags]) for tags in xs])/len(xs))

    r_duel_df = (r_duel_s.to_frame().T * 100)
    r_duel_df = r_duel_df.applymap(lambda x: f'{x: .2f}%')

    r_duel_df.index = ['duel win rate']
    
    match_summary_df = pd.concat([score_df, shot_df, pass_df, r_pass_df, clear_df, foul_df, r_duel_df])
    
    match_summary_df.columns = [teams_df[teams_df.wyId==teamId].name.values[0] for teamId in match_summary_df.columns.tolist()]
    
    return match_summary_df

def create_detail_events_df(df_tmp, teams_df):
    df_tmp['teamName'] = df_tmp.teamId.apply(lambda x: teams_df[teams_df.wyId==x].name.values[0])
    for eventName in ['Pass', 'Duel']:    
        summary = df_tmp[df_tmp.eventName==eventName].groupby(['teamName', 'subEventName']).size().to_frame()
        summary.columns = ['Number of actions']

        st.echo(eventName)
        st.dataframe(summary.reset_index(0).pivot_table(values=['Number of actions'], index=['subEventName'], columns=['teamName']).style.bar(vmin=summary.min(), vmax=summary.max()))
        