import numpy as np
import pandas as pd

import streamlit as st

def create_team_summary_df(df_tmp, matches_df, teams_df, selected_team_list):
    # 試合数
    n_matches_df = pd.DataFrame(columns=selected_team_list, index=['Number of matches'], data=[[len(matches_df[(matches_df.home_team_name==selected_team)|(matches_df.away_team_name==selected_team)]) for selected_team in selected_team_list]])
    
    # 試合結果、得点/失点
    result_dict = {selected_team:[[0,0,0]] for selected_team in selected_team_list}

    score_df = pd.DataFrame(columns=selected_team_list, index=['Goal', 'Goal Against'], data=np.zeros([2, len(selected_team_list)]))
    
    for selected_team in selected_team_list:
        for home_team_name, away_team_name, home_team_score, away_team_score in matches_df[(matches_df.home_team_name==selected_team)|(matches_df.away_team_name==selected_team)][['home_team_name', 'away_team_name', 'home_team_score', 'away_team_score']].values:
            my_score, against_score = [home_team_score, away_team_score] if home_team_name==selected_team else [away_team_score, home_team_score]
            
            result = 0 if my_score>against_score else 1 if my_score==against_score else 2
            result_dict[selected_team][0][result] += 1

            score_df.at['Goal', selected_team] += int(my_score.split('(')[0])
            score_df.at['Goal Against', selected_team] += int(against_score.split('(')[0])

    result_df = pd.DataFrame(index=['Result(w/d/l)'], data=result_dict)


    # シュート
    shot_s = df_tmp[df_tmp.eventName=='Shot'].groupby('teamId').size()

    penalty_s = df_tmp[df_tmp.subEventName=='Penalty'].groupby('teamId').size()
    for i in penalty_s.index:
        shot_s[i] += penalty_s[i]

    shot_df = shot_s.fillna('0').to_frame().T
    shot_df.index = ['Number of Shots']
    
    # パス本数
    pass_s = df_tmp[df_tmp.eventName=='Pass'].groupby('teamId').size()

    pass_df = pass_s.fillna('0').to_frame().T
    pass_df.index = ['Number of Passes']

    # パス成功率
    r_pass_s = df_tmp[df_tmp.eventName=='Pass'].groupby('teamId').tags.agg(lambda xs: np.sum([[1801 in [tag_dict['id'] for tag_dict in tags]] for tags in xs])) 

    r_pass_df = (r_pass_s.to_frame().T / pass_df.values * 100).astype(int)
    r_pass_df = r_pass_df.applymap(lambda x: f'{x: .2f}%')

    r_pass_df.index = ['Pass Success Rate']
    
    # クリア数
    clear_s = df_tmp[df_tmp.subEventName=='Clearance'].groupby('teamId').size()

    clear_df = clear_s.fillna('0').to_frame().T
    clear_df.index = ['Number of Clears']

    # ファール
    foul_s = df_tmp[df_tmp.subEventName=='Foul'].groupby('teamId').size()

    foul_df = foul_s.fillna('0').to_frame().T
    foul_df.index = ['Number of Fouls']
    
    # デュエル勝率
    r_duel_s = df_tmp[df_tmp.eventName=='Duel'].groupby('teamId').tags.agg(lambda xs:np.sum([np.sum([1801 in [tag_dict['id']] for tag_dict in tags]) for tags in xs])/len(xs))

    r_duel_df = (r_duel_s.to_frame().T * 100)
    r_duel_df = r_duel_df.applymap(lambda x: f'{x: .2f}%')

    r_duel_df.index = ['Duel Win Rate']

    team_summary_df = pd.concat([shot_df, pass_df, r_pass_df, clear_df, foul_df, r_duel_df])
    team_summary_df.columns = [teams_df[teams_df.wyId==teamId].name.values[0] for teamId in team_summary_df.columns.tolist()]

    team_summary_df = pd.concat([n_matches_df, result_df, score_df, team_summary_df])

    return team_summary_df


def create_match_summary_df(df_tmp, teams_df):
    """
        to do : 
            - fix score computing function to using matches_df
    """
    # スコア
    score_s = df_tmp[df_tmp.eventName=='Shot'].groupby('teamId').tags.agg(lambda xs: np.sum([[101 in [tag_dict['id'] for tag_dict in tags]] for tags in xs])) 

    penalty_s = df_tmp[df_tmp.subEventName=='Penalty'].groupby('teamId').tags.agg(lambda xs: np.sum([[101 in [tag_dict['id'] for tag_dict in tags]] for tags in xs])) 
    for i in penalty_s.index:
        score_s[i] += penalty_s[i]

    score_df = score_s.fillna('0').to_frame().T
    score_df.index = ['Score']
    
    # シュート
    shot_s = df_tmp[df_tmp.eventName=='Shot'].groupby('teamId').size()

    penalty_s = df_tmp[df_tmp.subEventName=='Penalty'].groupby('teamId').size()
    for i in penalty_s.index:
        shot_s[i] += penalty_s[i]

    shot_df = shot_s.fillna('0').to_frame().T
    shot_df.index = ['Number of Shots']
    
    # パス本数
    pass_s = df_tmp[df_tmp.eventName=='Pass'].groupby('teamId').size()

    pass_df = pass_s.fillna('0').to_frame().T
    pass_df.index = ['Number of Passes']

    # パス成功率
    r_pass_s = df_tmp[df_tmp.eventName=='Pass'].groupby('teamId').tags.agg(lambda xs: np.sum([[1801 in [tag_dict['id'] for tag_dict in tags]] for tags in xs])) 

    r_pass_df = (r_pass_s.to_frame().T / pass_df.values * 100).astype(int)
    r_pass_df = r_pass_df.applymap(lambda x: f'{x: .2f}%')

    r_pass_df.index = ['Pass Success Rate']
    
    # クリア数
    clear_s = df_tmp[df_tmp.subEventName=='Clearance'].groupby('teamId').size()

    clear_df = clear_s.fillna('0').to_frame().T
    clear_df.index = ['Number of Clears']

    # ファール
    foul_s = df_tmp[df_tmp.subEventName=='Foul'].groupby('teamId').size()

    foul_df = foul_s.fillna('0').to_frame().T
    foul_df.index = ['Number of Fouls']
    
    # デュエル勝率
    r_duel_s = df_tmp[df_tmp.eventName=='Duel'].groupby('teamId').tags.agg(lambda xs:np.sum([np.sum([1801 in [tag_dict['id']] for tag_dict in tags]) for tags in xs])/len(xs))

    r_duel_df = (r_duel_s.to_frame().T * 100)
    r_duel_df = r_duel_df.applymap(lambda x: f'{x: .2f}%')

    r_duel_df.index = ['Duel Win Rate']
    
    match_summary_df = pd.concat([score_df, shot_df, pass_df, r_pass_df, clear_df, foul_df, r_duel_df])
    # match_summary_df = pd.concat([score_df, shot_df, pass_df, clear_df, foul_df])
    
    match_summary_df.columns = [teams_df[teams_df.wyId==teamId].name.values[0] for teamId in match_summary_df.columns.tolist()]
    
    return match_summary_df

def create_detail_events_df(df_tmp, teams_df):
    df_tmp['teamName'] = df_tmp.teamId.apply(lambda x: teams_df[teams_df.wyId==x].name.values[0])
    for eventName in ['Pass', 'Duel']:    
        summary = df_tmp[df_tmp.eventName==eventName].groupby(['teamName', 'subEventName']).size().to_frame()
        summary.columns = ['Number of Actions']

        summary = summary.pivot_table(values=['Number of Actions'], index=['subEventName'], columns=['teamName']).fillna(0)
        # summary.columns = summary.columns.droplevel()

        st.subheader(eventName)
        st.table(
            summary
            .style
            .set_properties(**{'max-width': '80px', 'font-size': '15pt'})
            .bar(vmin=0, vmax=summary.max().max()+10)
            )
        # st.dataframe(summary.style.bar())
        # st.dataframe(summary, width=1000)
        