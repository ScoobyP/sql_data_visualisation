import streamlit as st
from database import DB
import plotly.express as px
import plotly.graph_objects as go


db = DB()
st.sidebar.image('https://i1.wp.com/bl-i.thgim.com/public/incoming/1ogk5e/article25940328.ece/alternates/FREE_1200/IPL-400x400jpg?strip=all', width = 200)

st.sidebar.title('Info')
option_button = st.sidebar.radio('Select a category', options = ['General Info','Team name', 'Batsman record', 'Bowler record'])

if option_button == 'General Info':
    st.header('Indian Premier League Analytics')
    all_matches = db.total_matches()
    st.subheader(f'Total matches played: {all_matches}')
    teams, matches = db.matches_by_all_teams()
    p_df_teams = db.fetch_current_and_defunct_teams()

    st.plotly_chart(px.pie(db.matches_by_all_teams(), names= p_df_teams, values=matches))
    st.text('+ indicates defunct teams')

    st.subheader('Number of Matches by Season')
    matches = go.Figure()
    matches.add_trace(go.Scatter(x=db.fetch_matches_by_season()[0], y=db.fetch_matches_by_season()[1], mode='lines+markers', name='Total Matches')).update_layout(xaxis=dict(type='category', categoryorder= 'category ascending'))
    st.plotly_chart(matches)

    st.subheader('Matches in Cities by Season')
    matches_in_cities = db.fetch_cities_played_in()
    matches_in_cities = px.bar(matches_in_cities, x= matches_in_cities['Season'], y= matches_in_cities['Matches'], color=matches_in_cities['City'], labels={'x': "Seasons", 'Matches': "IPL Matches", 'City':"Cities"})
    matches_in_cities.update_layout(xaxis=dict(type='category', categoryorder= 'category ascending'), barmode='stack')

    st.plotly_chart(matches_in_cities)

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
    boundary_fig.update_layout(xaxis=dict(type='category'))
    st.plotly_chart(boundary_fig)



    st.subheader('All Wickets by Season')
    all_wic = db.total_wickets()
    st.subheader(f'Wickets taken till date: {all_wic}')

    season_wic, category, tot_wic = db.total_wickets_by_category_by_season()

    wic_fig = px.scatter(db.total_wickets_by_category_by_season(), x = season_wic, y = tot_wic,color=category ,labels = {'color': 'Category', 'x': 'Season', 'y': 'Total Wickets'})
    wic_fig.update_traces(marker=dict(size=15))
    wic_fig.update_layout(xaxis=dict(type='category', categoryorder= 'category ascending'))
    st.plotly_chart(wic_fig)
    st.subheader('ALL EXTRAS GIVEN')

    ex_col1, ex_col2,ex_col3,ex_col4, ex_col5 = st.columns(5)
    with ex_col1:
        all_wides = db.total_wides()
        st.subheader(f'Wides: {all_wides}')
    with ex_col2:
        all_noballs = db.total_noballs()
        st.subheader(f'No Balls: {all_noballs}')
    with ex_col3:
        all_extras = db.total_extras()
        st.subheader(f'Extras: {all_extras}')
    with ex_col4:
        all_byes = db.total_byes()
        st.subheader(f'All Byes : {all_byes}')
    with ex_col5:
        all_legbyes = db.total_legbyes()
        st.subheader(f'Leg Byes: {all_legbyes}')

    season_extras, wides, noball, extras, byes, legbyes = db.all_extras_by_category_season()
    extras_fig = go.Figure()
    extras_fig.add_trace(go.Scatter(x=season_extras, y = wides, name = 'Wides' ))
    extras_fig.add_trace(go.Scatter(x=season_extras, y=noball,  name='No Balls'))
    extras_fig.add_trace(go.Scatter(x=season_extras, y=extras,  name='Extras'))
    extras_fig.add_trace(go.Scatter(x=season_extras, y=byes,  name='Byes'))
    extras_fig.add_trace(go.Scatter(x=season_extras, y=legbyes,  name='Leg byes'))

    extras_fig.update_layout(xaxis=dict(type='category'))
    st.plotly_chart(extras_fig)


elif option_button == 'Team name':
    all_team_names = db.fetch_all_teams()
    st.sidebar.selectbox('Select a team', sorted(all_team_names))
    st.header('Work in Progress....')

elif option_button == 'Batsman record':
    batsman_names = db.all_batsman_names()
    st.sidebar.selectbox('Select a batsman', sorted(batsman_names))
    st.header('Work in Progress....')

elif option_button == 'Bowler record':
    bowler_names = db.all_bowler_names()
    st.sidebar.selectbox('Select a bowler', sorted(bowler_names))
    st.header('Work in Progress....')

else:
    team_matches = db.matches_by_all_teams()
    # st.sidebar.selectbox('Season')