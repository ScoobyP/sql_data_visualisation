import streamlit as st
from database import DB
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


db=DB()
st.set_page_config(layout="wide")
st.sidebar.image('https://i1.wp.com/bl-i.thgim.com/public/incoming/1ogk5e/article25940328.ece/alternates/FREE_1200/IPL-400x400jpg?strip=all', width = 200)

st.sidebar.title('Info')
option_button = st.sidebar.radio('Select a category', options = ['General Info','Team Record', 'Batsman Record', 'Bowler Record'])

if option_button == 'General Info':
    st.header("Indian Premier League")

    st.divider()
    col1, col2 = st.columns([2,1])
    with col1:
        st.subheader("Welcome to My Mini IPL Analysis Project!")

        st.write('''
        Hello! Thank you for visiting my page. I'm excited to share with you my
        Mini IPL Analysis Project, where I dive into the world of the Indian Premier 
        League (IPL) using data from Kaggle.

        A Simple Introduction to IPL
        
        The IPL, or Indian Premier League, is a professional Twenty20 cricket league in
        India. It started in 2008 and has become one of the most popular cricket 
        tournaments in the world. Teams representing different cities compete against 
        each other in a fast-paced, thrilling format that keeps fans on the edge of 
        their seats.
        
        What is My Project About?
        
        In this project, I use data to explore various aspects of the IPL. By analyzing
        match results, player performances, and team statistics, I aim to uncover 
        interesting patterns and insights. Whether you're a cricket fan or just curious
        about data analysis, I hope you'll find something fascinating here.
        
        A Glimpse Into the Technical Side
        
        I used Python along with libraries like pandas for data handling and Plotly
        for creating the visualizations. SQL queries helped me fetch and process the 
        data efficiently from my cloud database and lastly I deployed it using 
        Streamlit.
        ''')

    with col2:
        st.image("https://www.thestatesman.com/wp-content/uploads/2023/02/Untitled-design-2023-02-17T184545.299.jpg")
        st.table(db.front_index_table())

    st.divider()

    exp1_button = st.checkbox("Show IPL Matches' Stats")

    if exp1_button:

        with st.expander("IPL Matches' Stats", expanded=False):

            all_matches = db.total_matches()
            st.subheader(f'Total matches played: {all_matches}')

            teams, matches = db.matches_by_all_teams()
            p_df_teams = db.fetch_current_and_defunct_teams()

            st.plotly_chart(px.pie(db.matches_by_all_teams(), names= p_df_teams, values=matches))
            st.text('*+* indicates defunct teams')

            st.subheader('Number of Matches by Season')
            matches = go.Figure()

            matches.add_trace(go.Scatter(x=db.fetch_matches_by_season()[0], y=db.fetch_matches_by_season()[1], mode='lines+markers', name='Total Matches')).update_layout(xaxis=dict(type='category', categoryorder= 'category ascending'))
            st.plotly_chart(matches)

            st.subheader('Matches in Cities by Season')

            matches_in_cities = db.fetch_cities_played_in()
            matches_in_cities = px.bar(matches_in_cities, x= matches_in_cities['Season'], y= matches_in_cities['Matches'], color=matches_in_cities['City'], labels={'x': "Seasons", 'Matches': "IPL Matches", 'City':"Cities"})
            matches_in_cities.update_layout(xaxis=dict(type='category', categoryorder= 'category ascending'), barmode='stack')

            st.plotly_chart(matches_in_cities)


    st.divider()

    exp2_button = st.checkbox("Show IPL Batting Stats")
    if exp2_button:
        with st.expander("IPL Batting Stats", expanded=False):

            st.subheader(f'Total IPL Runs: {db.total_ipl_runs()}')
            runs_df = db.total_runs()
            runs_fig = go.Figure()
            runs_fig.add_trace(go.Scatter(x=runs_df['Season'], y=runs_df['Total Runs'], name = 'Total Runs', mode='markers'))
            runs_fig.add_trace(go.Scatter(x=runs_df['Season'],y=runs_df['Runs Scored'], name = 'Scored', mode='markers'))
            runs_fig.add_trace(go.Scatter(x=runs_df['Season'], y=runs_df['Extras'],name = 'Extras', mode='markers'))
            runs_fig.update_traces(marker=dict(size=20, symbol='diamond-tall-dot'))
            runs_fig.update_layout(xaxis=dict(type='category', categoryorder= 'category ascending'))
            st.plotly_chart(runs_fig)


            col1, col2 = st.columns(2)
            with col1:
                sixes = db.total_six()
                st.subheader(f'Total sixes: {sixes}')

            with col2:
                fours = db.total_fours()
                st.subheader(f'Total fours: {fours}')

            st.subheader('Boundaries by season')
            season_boundaries, tot_six, tot_four = db.total_boundaries_by_season()

            boundary_fig = go.Figure()
            boundary_fig.add_trace(go.Scatter(x = season_boundaries, y = tot_six, name = 'Sixes', mode = 'lines+markers'))
            boundary_fig.add_trace(go.Scatter(x=season_boundaries, y=tot_four, name = 'Fours', mode = 'lines+markers'))
            boundary_fig.update_traces(marker=dict(size=15))
            boundary_fig.update_layout(xaxis=dict(type='category'))
            st.plotly_chart(boundary_fig)


            o_cap = db.orange_cap_by_season()
            st.subheader("Orange Cap Holder  by Season")
            st.write("Orange Cap holder in an IPL tournament is the player with highest runs scored in the entire season")
            st.plotly_chart(px.scatter(o_cap, x=o_cap['Season'], y= o_cap['Runs'], color=o_cap['Name']).update_traces(marker=dict(size=25, symbol='triangle-up')).update_layout(xaxis=dict(type='category',categoryorder= 'category ascending') ))

            st.subheader("Fifties and Centuries by Season")

            cen = db.num_centuries_by_season()
            fif = db.num_fifties_by_season()
            tot = db.total_fifties_centuries()

            c1,c2 = st.columns(2)
            with c1:
                st.subheader(f"Total Fifties: {sum(fif['Fifties'])}")
            with c2:
                st.subheader(f"Total Centuries: {sum(cen['Centuries'])}")
            all_ies = go.Figure()
            all_ies.add_trace(go.Scatter(x=cen['Season'], y=cen['Centuries'].astype(int), name='Centuries', mode='markers'))
            all_ies.add_trace(go.Scatter(x=fif['Season'], y=fif['Fifties'].astype(int), name='Fifties', mode='lines+markers')).update_traces(marker=dict(size = 15, symbol='diamond'))
            all_ies.add_trace(go.Bar(x = tot['Season'], y= tot['Total'], name='Total'))

            all_ies.update_layout(xaxis=dict(type='category'))
            st.plotly_chart(all_ies)

    st.divider()

    exp3_button = st.checkbox("Show IPL Bowling Stats")
    if exp3_button:

        with st.expander("IPL Bowling Stats", expanded=False):

            st.subheader('All Wickets by Season')
            all_wic = db.total_wickets()
            st.subheader(f'Wickets taken till date: {all_wic}')

            wickets_df = db.total_wickets_by_category_by_season()

            wic_fig = px.scatter(wickets_df, x = wickets_df['Season'], y = wickets_df['Total Wickets'],color=wickets_df['Category'] ,labels = {'color': 'Category', 'x': 'Season', 'y': 'Total Wickets'})
            wic_fig.update_traces(marker=dict(size=15))
            wic_fig.update_layout(xaxis=dict(type='category', categoryorder= 'category ascending'))
            st.plotly_chart(wic_fig)

            st.divider()

            st.subheader(f'ALL EXTRAS GIVEN: {db.total_extras()}')

            ex_col1, ex_col2,ex_col3,ex_col4, ex_col5 = st.columns(5)
            with ex_col1:
                all_wides = db.total_wides()
                st.subheader(f'Wides: {all_wides}')
            with ex_col2:
                all_noballs = db.total_noballs()
                st.subheader(f'No Balls: {all_noballs}')
            with ex_col3:
                st.subheader(f'Penalties: {db.total_penalty()}')
            with ex_col4:
                all_byes = db.total_byes()
                st.subheader(f'Byes : {all_byes}')
            with ex_col5:
                all_legbyes = db.total_legbyes()
                st.subheader(f'Leg Byes: {all_legbyes}')

            extras_df = db.all_extras_by_category_season()
            extras_fig = go.Figure()
            extras_fig.add_trace(go.Scatter(x=extras_df['Season'], y = extras_df['Wides'], name = 'Wides', mode='lines+markers' ))
            extras_fig.add_trace(go.Scatter(x=extras_df['Season'], y= extras_df['No Balls'],  name='No Balls', mode='lines+markers'))
            extras_fig.add_trace(go.Scatter(x=extras_df['Season'], y=extras_df['Byes'],  name='Byes', mode='lines+markers'))
            extras_fig.add_trace(go.Scatter(x=extras_df['Season'], y=extras_df['Leg Byes'],  name='Leg Byes', mode='lines+markers'))
            extras_fig.add_trace(go.Scatter(x=extras_df['Season'], y=extras_df['Penalty'], name='Penalties', mode='lines+markers'))

            extras_fig.update_layout(xaxis=dict(type='category'))
            st.plotly_chart(extras_fig)

            st.subheader("Purple Cap Holder by Season")
            st.write("Purple Cap holder in an IPL tournament is the player with the most wickets in the entire season")

            p_cap = db.purple_cap_by_season()
            st.plotly_chart(px.scatter(p_cap, x=p_cap['Season'], y=p_cap['Wickets'], color=p_cap['Name'], size=p_cap['Wickets'].astype(int), size_max=25).update_layout(xaxis=dict(type='category', categoryorder= 'category ascending')))

elif option_button == 'Team Record':
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


            st.subheader("Comparison Against Teams by Season")
            teams_wb_s = db.grouped_stacked_won(t1)
            fig_won = px.bar(teams_wb_s, x = teams_wb_s['season'], y=teams_wb_s['all_won'], color=teams_wb_s['against'], barmode = 'stack', title = 'Won Against').update_layout(xaxis=dict(type = 'category', categoryorder= 'category ascending', title = 'Season'), yaxis = dict(title='Matches Won'), legend_title='Against')

            won_go = go.Scatter(x=t_wl_s['season'], y= t_wl_s['won'], name = 'Total Won', mode = 'lines+markers')
            fig_won.add_trace(won_go)

            teams_lb_s = db.grouped_stacked_lost(t1)
            fig_lost = px.bar(x = teams_lb_s['season'],y=teams_lb_s['all_lost'], color=teams_lb_s['against'], barmode = 'stack', title = 'Lost Against').update_layout(xaxis=dict(type = 'category', categoryorder= 'category ascending', title='Season'), yaxis=dict(title='Matches Lost'), legend=dict(title='Against'))

            loss_go = go.Scatter(x=t_wl_s['season'], y=t_wl_s['lost'], name='Total Lost', mode='lines+markers')
            fig_lost.add_trace(loss_go)


            st.plotly_chart(fig_won)
            st.plotly_chart(fig_lost)

###############################################################################


elif option_button == 'Batsman Record':
    st.header("IPL Batsman Record")
    st.divider()

    batsman_names = db.all_batsman_names()
    st.selectbox('Select a batsman', sorted(batsman_names))
    st.subheader('Work in Progress....')

elif option_button == 'Bowler Record':
    st.subheader("IPL Bowler Record")
    st.divider()

    bowler_names = db.all_bowler_names()
    st.selectbox('Select a bowler', sorted(bowler_names))
    st.header('Work in Progress....')

else:
    team_matches = db.matches_by_all_teams()
    # st.sidebar.selectbox('Season')