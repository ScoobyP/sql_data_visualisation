import streamlit as st
from database import DB
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

db = DB()
st.header("IPL Team Record")
st.divider()

all_team_names = db.fetch_all_teams()
t1 = st.selectbox('Select a team', sorted(all_team_names))
b1 = st.button("Show Team Record")

if b1:
    c1,c2, c3 = st.columns([1,2,1])


    with c2:
        st.header(f'{t1}')
        st.table(db.teams_table(t1))

    exp_p2_1 = st.expander(f"Show Match Stats of {t1}", expanded=False)
    t_m_s = db.team_match_by_season(t1)
    with exp_p2_1:
        st.subheader(f"All Matches by {t1}")
        team_pie = db.all_match_piechart_by_team(t1)
        st.plotly_chart(px.pie(team_pie, names=team_pie['Against'], values=team_pie['No. of Matches']))

        st.subheader(f"Total Matches of {t1} per Season")
        total_matches_by_season = go.Figure()
        total_matches_by_season.add_trace(
            go.Scatter(x=t_m_s['season'], y=t_m_s['num'], name='Total Played', mode='lines+markers')).update_traces(
            marker=dict(symbol='circle-open', size=20)).update_layout(
            xaxis=dict(type='category', categoryorder='category ascending', title='Season'),
            yaxis=dict(title='Total Played'))
        st.plotly_chart(total_matches_by_season)

        df_m = db.team_match_by_city(t1)
        st.subheader(f"{t1} in City by Season")
        st.plotly_chart(
            px.bar(df_m, x=df_m['season'], y=df_m['No. of Matches in City'], color=df_m['city']).update_layout(
                xaxis=dict(type='category', categoryorder='category ascending'), xaxis_title="Season",
                yaxis_title='No. of Matches', legend_title="Cities Played in"))

        a_t_b_s = db.against_team_by_season(t1)
        st.subheader(f"{t1} Against Other Teams by Season")
        st.plotly_chart(
            px.bar(a_t_b_s, x=a_t_b_s['season'], y=a_t_b_s['matches'], color=a_t_b_s['against']).update_layout(
                xaxis=dict(type='category', categoryorder='category ascending'), xaxis_title="Season",
                yaxis_title='No. of Matches', legend_title="Teams Played Against"))
###############################################################################
    exp_p2_2 = st.expander(f"Show Win Loss Stats of {t1}", expanded=False)
    with exp_p2_2:
        st.subheader('Comparison by Batting First and Fielding First')
        match_fig = go.Figure()
        team_wonloss = db.matches_won_lost(t1)
        match_fig.add_trace(go.Bar(x = team_wonloss['toss_decision'], y = team_wonloss['_won'], name= 'Won'))
        match_fig.add_trace(go.Bar(x=team_wonloss['toss_decision'], y=team_wonloss['_lost'], name = 'Lost'))
        st.plotly_chart(match_fig)

        st.subheader("Comparison Against Other Teams")
        won_ag_team = db.won_against(t1)
        wonloss_fig = go.Figure()
        wonloss_fig.add_trace(go.Bar(x=won_ag_team['won_against'], y= won_ag_team['Won'], name = 'Won', marker = dict(color='#33cc33')))
        lost_ag_team = db.loss_against(t1)
        wonloss_fig.add_trace(go.Bar(x=lost_ag_team['lost_against'], y=lost_ag_team['Lost'], name='Lost', marker = dict(color='#ffff66')))
        wonloss_fig.update_layout(xaxis=dict(type='category'), barmode = 'stack')
        st.plotly_chart(wonloss_fig)

        st.subheader("Comparison by Season")
        match_fig2 = go.Figure()
        t_wl_s = db.match_wonloss_by_season(t1)

        match_fig2.add_trace(go.Scatter(x=t_m_s['season'], y= t_m_s['num'], name = 'Total', mode='lines+markers')).update_traces(marker=dict(symbol='square', size=15))
        match_fig2.add_trace(go.Bar(x=t_wl_s['season'], y=t_wl_s['won'], name= 'Won'))
        match_fig2.add_trace(go.Bar(x=t_wl_s['season'], y=t_wl_s['lost'], name = 'Lost'))

        match_fig2.update_layout(xaxis=dict(type = 'category'), barmode='stack')
        st.plotly_chart(match_fig2)


        st.subheader(f"Comparison Against Teams by Season of \n{t1}")
        teams_wb_s = db.grouped_stacked_won(t1)
        fig_won = px.bar(teams_wb_s, x = teams_wb_s['season'], y=teams_wb_s['all_won'], color=teams_wb_s['against'], barmode = 'stack', title = 'Won Against', labels={'season':'Season', 'all_won':'Matches Won', 'against': 'Against'}).update_layout(xaxis=dict(type = 'category', categoryorder= 'category ascending', title = 'Season'), yaxis = dict(title='Matches Won'), legend_title='Against')

        won_go = go.Scatter(x=t_wl_s['season'], y= t_wl_s['won'], name = 'Total Won', mode = 'lines+markers')
        fig_won.add_trace(won_go)

        teams_lb_s = db.grouped_stacked_lost(t1)
        fig_lost = px.bar(x = teams_lb_s['season'],y=teams_lb_s['all_lost'], color=teams_lb_s['against'], barmode = 'stack', title = 'Lost Against', labels={'x':'Season', 'y':'Matches Lost', 'color': 'Against'}).update_layout(xaxis=dict(type = 'category', categoryorder= 'category ascending', title='Season'), yaxis=dict(title='Matches Lost'), legend=dict(title='Against'))

        loss_go = go.Scatter(x=t_wl_s['season'], y=t_wl_s['lost'], name='Total Lost', mode='lines+markers')
        fig_lost.add_trace(loss_go)


        st.plotly_chart(fig_won)
        st.plotly_chart(fig_lost)