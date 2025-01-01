import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from database import DB


db=DB()

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

        st.subheader('IPL Season Titles by Teams')
        titles = db.titles_by_season()
        titles_fig = px.bar(titles, y=titles['Winner'], x=titles['Times Won'], color=titles['Season'], orientation='h', hover_data={'Season': True, 'Times Won':False, 'Winner': True})
        titles_fig.update_layout(yaxis=dict(type='category', categoryorder= 'category ascending'))
        st.plotly_chart(titles_fig)

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
        #runs_fig.update_layout(xaxis=dict(categoryorder= 'category ascending'))
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
        #boundary_fig.update_layout(xaxis=dict(type='category'))
        st.plotly_chart(boundary_fig)


        o_cap = db.orange_cap_by_season()
        st.subheader("Orange Cap Holder  by Season")
        st.write("Orange Cap holder in an IPL tournament is the player with highest runs scored in the entire season")
        st.plotly_chart(px.scatter(o_cap, x=o_cap['Season'], y= o_cap['Runs'], color=o_cap['Name']).update_traces(marker=dict(size=25, symbol='triangle-up')).update_layout(xaxis=dict(type='category',categoryorder= 'category ascending')))

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

        #all_ies.update_layout(xaxis=dict(type='category'))
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

        st.subheader("Maidens and Hat Tricks")
        st.write('''
                    * Maiden over is when the bowler concedes 0 runs for the entire over. 
                    1 Over = 6 deliveries (balls). Three consecutive wickets by the same bowler constitutes a hat-trick.
                    ''' )

        maiden_col1,maiden_col2 = st.columns(2)
        with maiden_col1:
            all_maidens = db.all_maidens()
            st.subheader(f"ALL Maiden Overs: {all_maidens}")

        ht_df = db.all_hattricks()
        with maiden_col2:

            st.subheader(f"ALL Hat Tricks: {sum(ht_df['Hat Tricks'])}")


        df_m = db.maiden_overs_by_season()
        dots_maidens_ht_fig = go.Figure()


        dots_maidens_ht_fig.add_trace(go.Scatter(x = ht_df['Season'].sort_values(ascending=True).unique(), y=ht_df.groupby('Season')['Total'].first(), name='Hat Tricks', mode='markers', marker=dict(size=19)))
        dots_maidens_ht_fig.add_trace(go.Bar(x = ht_df['Season'].sort_values(ascending=True).unique(), y=df_m['maiden_overs']))
        dots_maidens_ht_fig.update_layout(xaxis=dict(title='Season'), yaxis=dict(title='Maidens and Hat Tricks'))
        st.plotly_chart(dots_maidens_ht_fig)


        ht_by_season = px.bar(ht_df, x='Season', y=ht_df['Hat Tricks'], color=ht_df['Bowler'])
        ht_by_season.update_layout(
                xaxis=dict(type='category', categoryorder='category ascending'), xaxis_title="Season",
                yaxis_title='No. of Hat Tricks', legend_title="Bowlers", title='Breakdown of Hat Tricks by Season')
        total_ht = go.Scatter(x=ht_df['Season'].unique(), y=ht_df.groupby('Season')['Total'].first(), name='Total HatTricks', mode='markers', marker=dict(size=19, symbol='diamond'))
        ht_by_season.add_trace(total_ht)
        st.plotly_chart(ht_by_season)
###############################################################################
