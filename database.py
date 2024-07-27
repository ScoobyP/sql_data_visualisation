import mysql.connector
import streamlit as st
from dotenv import load_dotenv
import pandas as pd
import os


class DB:

    def __init__(self):

        try:
            load_dotenv()
            #self.mydb = mysql.connector.connect(
                #host='',
                #user='',
                #password='',
                #port='',
                #database=''
            #)
            self.mydb = mysql.connector.connect(
             host=os.getenv("aiven_url1"),
             user=os.getenv("aiven_user_name"),
             password=os.getenv("aiven_user_pass"),
             port=os.getenv("aiven_port"),
             database=os.getenv("aiven_db2")

             )
            self.my_cursor = self.mydb.cursor()
            print('Connection Established')
        except Exception as e:
            print(f'Connection Error: {e}')

    # Clean table - team names and season
    def clean_table(self):
        self.my_cursor.execute('''
        CALL update_OLAP_all_matches() 
        ''')

    # Front Table START

    @st.cache_data
    def total_matches(_self):
        _self.my_cursor.execute('''
        SELECT COUNT(DISTINCT match_id) AS 'all_matches' FROM ipl_OLAP.all_deliveries
        ''')
        data = _self.my_cursor.fetchone()
        return data[0]

    def first_edition(self):
        self.my_cursor.execute('''
        SELECT season FROM ipl_OLAP.all_deliveries
        GROUP BY  season
        ORDER BY season LIMIT 1
        ''')
        data = self.my_cursor.fetchone()
        return str(data[0])

    def latest_edition(self):
        self.my_cursor.execute('''
        SELECT season FROM ipl_OLAP.all_deliveries
        GROUP BY  season
        ORDER BY season DESC LIMIT 1
        ''')
        data = self.my_cursor.fetchone()
        return str(data[0])

    def next_edition(self):
        self.my_cursor.execute('''
        SELECT season + 1 AS 'next_season'
        FROM (SELECT season FROM all_deliveries
        GROUP BY  season
        ORDER BY season DESC LIMIT 1) t1
        ''')
        data = self.my_cursor.fetchone()
        return str(int(data[0]))

    def num_of_current_teams(self):

        self.my_cursor.execute('''
                SELECT COUNT(DISTINCT all_deliveries.batting_team) AS 'num_teams'
                FROM all_deliveries
                WHERE season = (SELECT MAX(season) FROM all_deliveries);
                ''')
        data = self.my_cursor.fetchone()
        return str(data[0])

    def current_champion(self):

        self.my_cursor.execute('''
                SELECT winner FROM all_matches
                WHERE season = (SELECT MAX(season) FROM all_matches) AND
                                match_type = 'Final';
                ''')
        data = self.my_cursor.fetchone()
        return data[0]

    def most_titles(self):
        teams = []
        times = []
        self.my_cursor.execute('''
                WITH table1 AS (SELECT winner, COUNT(*) as 'times_won' FROM ipl_OLAP.all_matches
                WHERE match_type = 'Final'
                GROUP BY winner)
                SElECT winner, times_won FROM table1
                WHERE times_won = (SELECT MAX(times_won) FROM table1);
                ''')
        data = self.my_cursor.fetchall()
        for i in data:
            teams.append(str(i[0]))
            times.append(f' ({str(i[1])})')

        return pd.DataFrame({'Team': teams, 'Titles Won': times})

    def most_runs(self):
        name = []
        runs = []
        self.my_cursor.execute('''
        SELECT striker,
        SUM(runs_off_bat) AS 'total_runs'
        FROM all_deliveries
        WHERE innings < 3 
        GROUP BY striker
        ORDER BY total_runs DESC LIMIT 1
        ''')
        data = self.my_cursor.fetchall()
        for i in data:
            name.append(str(i[0]))
            runs.append(f' ({str(round((i[1])))})')
        return pd.DataFrame({'Name': name, 'Runs': runs})

    @st.cache_data
    def most_wickets(_self):
        name = []
        wicks = []
        _self.my_cursor.execute('''
        SELECT bowler,
        SUM(CASE WHEN wicket_type IS NOT NULL THEN 1 ELSE 0 END) AS 'total_wickets'
        FROM (SELECT * FROM all_deliveries
                       WHERE innings < 3 AND wicket_type
                                 IN ('bowled', 'caught','caught and bowled','hit wicket','lbw','stumped')) a1
        GROUP BY bowler
        ORDER BY total_wickets DESC LIMIT 1
        ''')
        data = _self.my_cursor.fetchall()
        for i in data:
            name.append(str(i[0]))
            wicks.append(f' ({str(i[1])})')
        return pd.DataFrame({'Name': name, 'Wickets': wicks})

    @st.cache_data
    def front_index_table(_self):

        df = pd.DataFrame(
            {'Format: ': '20 Overs', 'First Season: ': _self.first_edition(), 'Latest Season: ': _self.latest_edition(),
             'Next Season: ': _self.next_edition(), 'Number of Teams: ': _self.num_of_current_teams(),
             'Current Champion: ': _self.current_champion(),
             'Most Titles: ': _self.most_titles().to_string(index=False, header=False),
             'Most Runs': _self.most_runs().to_string(index=False, header=False),
             'Most Wickets': _self.most_wickets().to_string(index=False, header=False)}, index=['Values'])
        return df.transpose()

    # Front Table END

    def fetch_all_player_names(self):
        # Extracting all player names

        all_names = []
        self.my_cursor.execute('''
        SELECT non_striker FROM ipl_OLAP.all_deliveries
        UNION
        SELECT striker FROM ipl_OLAP.all_deliveries
        UNION
        SELECT bowler FROM ipl_OLAP.all_deliveries
        ''')
        # self.mydb.commit()
        all_player_names = self.my_cursor.fetchall()

        for name in all_player_names:
            all_names.append(name[0])

        return all_names

    def fetch_all_teams(self):
        ipl_teams = []
        # Extracting all team names

        self.my_cursor.execute('''
        SELECT batting_team FROM ipl_OLAP.all_deliveries
        UNION 
        SELECT bowling_team FROM ipl_OLAP.all_deliveries
        ''')

        team_names = self.my_cursor.fetchall()
        for team in team_names:
            ipl_teams.append(team[0])

        return ipl_teams

    # IPL Matches' Stats START

    def fetch_current_teams(self):
        current_teams = []
        self.my_cursor.execute('''
        SELECT DISTINCT all_deliveries.batting_team FROM ipl_OLAP.all_deliveries
        WHERE season = (SELECT MAX(season) FROM ipl_OLAP.all_deliveries)
        UNION
        SELECT DISTINCT all_deliveries.bowling_team FROM ipl_OLAP.all_deliveries
        WHERE season = (SELECT MAX(season) FROM ipl_OLAP.all_deliveries)
        ''')
        curr_team = self.my_cursor.fetchall()
        for team in curr_team:
            current_teams.append(team[0])

        return current_teams

    @st.cache_data
    def fetch_current_and_defunct_teams(_self):
        current_teams = _self.fetch_current_teams()
        all_teams_pnp = []
        for team in _self.matches_by_all_teams()[0]:
            if team not in current_teams:
                all_teams_pnp.append(team + ' *+*')
            else:
                all_teams_pnp.append(team)

        return sorted(all_teams_pnp)

    @st.cache_data
    def matches_by_all_teams(_self):
        teams = []
        matches = []
        _self.my_cursor.execute('''
        WITH big_table AS (SELECT A1.batting_team, matches_played, matches FROM (SELECT batting_team, COUNT(DISTINCT match_id) AS 'matches_played' FROM ipl_OLAP.all_deliveries
        GROUP BY batting_team) A1
        JOIN 
        (SELECT DISTINCT bowling_team, COUNT(DISTINCT match_id) AS 'matches' FROM ipl_OLAP.all_deliveries
        GROUP BY bowling_team) A2
        ON A1.batting_team = A2.bowling_team)
        
        SELECT batting_team, GREATEST(matches_played, matches) AS 'total_played' FROM big_table
        ''')
        no_of_matches = _self.my_cursor.fetchall()
        for item in no_of_matches:
            teams.append(item[0])
            matches.append(item[1])

        return sorted(teams), matches

    @st.cache_data
    def fetch_cities_played_in(_self):
        season = []
        city = []
        num_mat = []

        _self.my_cursor.execute('''
        SELECT season, 
        city,
        COUNT(city) AS 'num_matches'
        FROM ipl_OLAP.all_matches
        GROUP BY season, city
        ''')
        data = _self.my_cursor.fetchall()
        for i in data:
            season.append(i[0])
            city.append(i[1])
            num_mat.append(i[2])

        df_original = pd.DataFrame({'Season': season, 'City': city, 'Matches': num_mat})

        return df_original.sort_values('Season', ascending=True)

    @st.cache_data
    def fetch_matches_by_season(_self):
        num_matches = []
        season = []
        _self.my_cursor.execute('''
        SELECT season, COUNT(*) AS 'num_matches' FROM ipl_OLAP.all_matches
        GROUP BY season
        ''')
        data = _self.my_cursor.fetchall()
        for i in data:
            season.append(i[0])
            num_matches.append(i[1])

        return sorted(season), num_matches

    def titles_by_season(self):
        self.my_cursor.execute('''
        SELECT season, winner, COUNT(winner) AS times_won FROM all_matches
        WHERE match_type = 'Final'
        GROUP BY season, winner
        ORDER BY season
        ''')
        data = self.my_cursor.fetchall()
        s=[]
        winner=[]
        times=[]
        for i in data:
            s.append(i[0])
            winner.append(i[1])
            times.append(i[2])
        df = pd.DataFrame({'Season': s, 'Winner': winner, 'Times Won': times})
        return df

    # IPL Matches' Stats END

    # IPL Batting Stats START
    @st.cache_data
    def total_ipl_runs(_self):

        _self.my_cursor.execute('''
        SELECT SUM(runs_off_bat)+SUM(extras) FROM ipl_OLAP.all_deliveries
        WHERE innings < 3
        ''')
        runs = _self.my_cursor.fetchone()
        return int(runs[0])  #

    @st.cache_data
    def total_runs(_self):
        s = []
        run_scored = []
        run_extras = []
        all_runs = []
        _self.my_cursor.execute('''
        SELECT season,SUM(runs_off_bat),SUM(extras), SUM(runs_off_bat)+SUM(extras) FROM ipl_OLAP.all_deliveries 
        WHERE innings < 3
        GROUP BY season
        ORDER BY season ASC
        ''')
        data = _self.my_cursor.fetchall()
        for i in data:
            s.append(i[0])
            run_scored.append(i[1])
            run_extras.append(i[2])
            all_runs.append(i[3])
        df = pd.DataFrame({'Season': s, 'Runs Scored': run_scored, 'Extras': run_extras, 'Total Runs': all_runs})
        return df

    @st.cache_data
    def orange_cap_by_season(_self):
        s = []
        n = []
        r = []
        _self.my_cursor.execute('''
                SELECT season, striker, runs FROM (SELECT season,
                striker,
                SUM(runs_off_bat) AS 'runs',
                ROW_NUMBER() over (PARTITION BY season ORDER BY SUM(runs_off_bat) DESC) AS 'row_num'
                FROM all_deliveries
                WHERE innings < 3
                GROUP BY season,striker
                ORDER BY season ASC,runs DESC) a1
                WHERE row_num = 1
                
                ''')
        data = _self.my_cursor.fetchall()
        for item in data:
            s.append(item[0])
            n.append(item[1])
            r.append(item[2])
        df = pd.DataFrame({'Season': s, 'Name': n, 'Runs': r})
        return df

    @st.cache_data
    def total_six(_self):
        sixes = []
        _self.my_cursor.execute('''
        SELECT COUNT(*) FROM ipl_OLAP.all_deliveries
        WHERE runs_off_bat = 6 AND innings < 3
        ''')
        data = _self.my_cursor.fetchall()
        for item in data:
            sixes.append(item)

        return sixes[0][0]

    @st.cache_data
    def total_fours(_self):
        fours = []
        _self.my_cursor.execute('''
        SELECT COUNT(*) FROM ipl_OLAP.all_deliveries
        WHERE runs_off_bat = 4 AND innings < 3
                ''')
        data = _self.my_cursor.fetchall()
        for item in data:
            fours.append(item)

        return fours[0][0]

    @st.cache_data
    def total_boundaries_by_season(_self):
        season = []
        sixes = []
        fours = []
        _self.my_cursor.execute('''
        SELECT t1.season, total_sixes, total_fours FROM (SELECT season, COUNT(runs_off_bat) AS 'total_sixes' FROM ipl_OLAP.all_deliveries
        WHERE runs_off_bat = 6 AND innings < 3
        GROUP BY season) t1
        JOIN (SELECT season, COUNT(runs_off_bat) AS 'total_fours' FROM ipl_OLAP.all_deliveries
        WHERE runs_off_bat = 4 AND innings < 3
        GROUP BY season) t2
        ON t1.season = t2.season
        ORDER BY t1.season ASC
        ''')
        data = _self.my_cursor.fetchall()
        for item in data:
            season.append(item[0])
            sixes.append(item[1])
            fours.append(item[2])

        return season, sixes, fours

    @st.cache_data
    def num_centuries_by_season(_self):
        s = []
        cen = []
        _self.my_cursor.execute('''
        SELECT season, COUNT(striker) AS 'num_100' FROM (SELECT season, striker, SUM(runs_off_bat) AS 'total_runs' FROM all_deliveries
        GROUP BY season, match_id, striker
        HAVING total_runs > 99) a1
        GROUP BY season
        ORDER BY season ASC
         ''')
        data = _self.my_cursor.fetchall()
        for item in data:
            s.append(item[0])
            cen.append(item[1])
        df = pd.DataFrame({'Season': s, 'Centuries': cen})
        return df

    @st.cache_data
    def num_fifties_by_season(_self):
        s = []
        fif = []
        _self.my_cursor.execute('''
        SELECT season, COUNT(striker) AS 'num_100' FROM (SELECT season, striker, SUM(runs_off_bat) AS 'total_runs' FROM all_deliveries
        GROUP BY season, match_id, striker
        HAVING total_runs BETWEEN 49 AND 99) a1
        GROUP BY season
        ORDER BY season ASC
         ''')
        data = _self.my_cursor.fetchall()
        for item in data:
            s.append(item[0])
            fif.append(item[1])
        df = pd.DataFrame({'Season': s, 'Fifties': fif})
        return df

    @st.cache_data
    def total_fifties_centuries(_self):
        df = pd.DataFrame({'Season': _self.num_fifties_by_season()['Season'],
                           'Total': _self.num_fifties_by_season()['Fifties'] + _self.num_centuries_by_season()[
                               'Centuries']})
        return df

    # IPL Batting Stats END

    # IPL Bowling Stats START
    def total_balls_thrown(self):
        balls_thrown = []
        self.my_cursor.execute('''
        SELECT COUNT(ball) FROM ipl_OLAP.all_deliveries
        WHERE innings < 3
                ''')
        data = self.my_cursor.fetchall()
        for item in data:
            balls_thrown.append(item[0])

        return balls_thrown

    @st.cache_data
    def total_penalty(_self):
        pen = []
        _self.my_cursor.execute('''
        SELECT SUM(penalty) AS 'total_penalty' FROM ipl_OLAP.all_deliveries
        WHERE innings < 3
        ''')
        data = _self.my_cursor.fetchone()
        for i in data:
            pen.append(int(i))
        return pen[0]

    @st.cache_data
    def total_wickets_by_category_by_season(_self):
        season = []
        wickets_category = []
        total_wickets = []
        _self.my_cursor.execute('''
        SELECT season, wicket_type, COUNT(wicket_type) AS 'total_wickets' FROM ipl_OLAP.all_deliveries
        WHERE wicket_type != '' AND innings < 3
        GROUP BY season , wicket_type
        ORDER BY season ASC''')
        data = _self.my_cursor.fetchall()
        for item in data:
            season.append(item[0])
            wickets_category.append(item[1])
            total_wickets.append(item[2])

        df = pd.DataFrame({'Season': season, 'Category': wickets_category, 'Total Wickets': total_wickets})
        df1 = df.sort_values(by='Season')
        return df1

    @st.cache_data
    def all_extras_by_category_season(_self):
        season = []
        wides = []
        noballs = []
        penalty = []
        byes = []
        legbyes = []
        _self.my_cursor.execute('''
        SELECT season, SUM(wides), SUM(noballs), SUM(byes), SUM(legbyes), SUM(penalty)
        FROM ipl_OLAP.all_deliveries
        WHERE innings < 3
        GROUP BY season
        ORDER BY season ASC
        ''')
        data = _self.my_cursor.fetchall()
        for item in data:
            season.append(item[0])
            wides.append(item[1])
            noballs.append(item[2])
            byes.append(item[3])
            legbyes.append(item[4])
            penalty.append(item[5])

        df = pd.DataFrame({'Season': season, 'Wides': wides, 'No Balls': noballs, 'Penalty': penalty, 'Byes': byes,
                           'Leg Byes': legbyes})
        df1 = df.sort_values(by='Season')
        return df1

    @st.cache_data
    def purple_cap_by_season(_self):
        s = []
        n = []
        w = []
        _self.my_cursor.execute('''
                SELECT season, bowler, total_wickets 
                FROM  (SELECT season,bowler,
                       SUM(CASE WHEN wicket_type IS NOT NULL THEN 1 ELSE 0 END) AS 'total_wickets',
                       ROW_NUMBER() over (PARTITION BY season ORDER BY SUM(CASE WHEN wicket_type IS NOT NULL THEN 1 ELSE 0 END) DESC ) AS 'row_num'
                FROM (SELECT * FROM all_deliveries
                               WHERE innings < 3 AND
                                     wicket_type
                                         IN ('bowled', 'caught','caught and bowled','hit wicket','lbw','stumped')) a1
                GROUP BY season, bowler
                ORDER BY season ASC, total_wickets DESC) k1
                WHERE row_num = 1
                ORDER BY season ASC
                ''')
        data = _self.my_cursor.fetchall()
        for item in data:
            s.append(item[0])
            n.append(item[1])
            w.append(item[2])
        df = pd.DataFrame({'Season': s, 'Name': n, 'Wickets': w})
        return df

    @st.cache_data
    def total_wides(_self):
        all_wides = []
        _self.my_cursor.execute('''
        SELECT SUM(wides) AS 'wides' FROM ipl_OLAP.all_deliveries
        WHERE innings < 3
        ''')
        data = _self.my_cursor.fetchone()
        for item in data:
            all_wides.append(int(item))

        return all_wides[0]

    @st.cache_data
    def total_noballs(_self):
        all_noballs = []
        _self.my_cursor.execute('''
        SELECT SUM(noballs) AS 'no_balls' FROM ipl_OLAP.all_deliveries
        WHERE innings < 3
        ''')
        data = _self.my_cursor.fetchone()
        for item in data:
            all_noballs.append(int(item))

        return all_noballs[0]

    @st.cache_data
    def total_extras(_self):
        all_extras = []
        _self.my_cursor.execute('''
        SELECT SUM(extras) AS 'extras' FROM ipl_OLAP.all_deliveries
        WHERE innings < 3
        ''')
        data = _self.my_cursor.fetchone()
        for item in data:
            all_extras.append(int(item))

        return all_extras[0]

    @st.cache_data
    def total_byes(_self):
        all_byes = []
        _self.my_cursor.execute('''
        SELECT SUM(byes) AS 'byes' FROM ipl_OLAP.all_deliveries
        WHERE innings < 3
        ''')
        data = _self.my_cursor.fetchone()
        for item in data:
            all_byes.append(int(item))

        return all_byes[0]

    @st.cache_data
    def total_legbyes(_self):
        all_legbyes = []
        _self.my_cursor.execute('''
        SELECT SUM(legbyes) AS 'legbyes' FROM ipl_OLAP.all_deliveries
        WHERE innings < 3
        ''')
        data = _self.my_cursor.fetchone()
        for item in data:
            all_legbyes.append(int(item))

        return all_legbyes[0]

    @st.cache_data
    def total_wickets(_self):
        _self.my_cursor.execute('''
        SELECT COUNT(wicket_type) FROM ipl_OLAP.all_deliveries
        WHERE wicket_type != '' AND innings < 3
        ''')
        data = _self.my_cursor.fetchone()
        return data[0]

    # IPL Bowling Stats END

    # TEAM stats START

    @st.cache_data
    def teams_table(_self, team):
        team_name = team

        if team_name in _self.fetch_current_teams():
            status = 'Active'
        else:
            status = "Defunct *-*"

        _self.my_cursor.execute('''
                                SELECT COUNT(*) as matches_played FROM all_matches
                                WHERE team1 = %s OR team2 = %s
                                ''', (team_name, team_name))
        against = _self.my_cursor.fetchone()[0]

        _self.my_cursor.execute('''
                                        SELECT COUNT(*) as matches_played FROM all_matches
                                        WHERE winner LIKE %s
                                        ''', (team_name,))
        won = _self.my_cursor.fetchone()[0]

        _self.my_cursor.execute('''
                                                SELECT COUNT(*) as titles FROM all_matches
                                                WHERE winner LIKE %s AND match_type = 'Final'
                                                ''', (team_name,))
        titles = _self.my_cursor.fetchone()[0]

        _self.my_cursor.execute('''
        SELECT MIN(all_matches.season) FROM ipl_OLAP.all_matches
        WHERE team1 = %s OR team2 = %s;
                                     ''', (team_name, team_name))
        first_season = _self.my_cursor.fetchone()[0]

        _self.my_cursor.execute('''
        
        SELECT team2 AS 'Team' , against AS 'Played'
        FROM (SELECT a1.team2,
               SUM(num_match) AS 'against',
               DENSE_RANK() over (ORDER BY SUM(num_match) DESC) AS 'rank'
        FROM (SELECT team2, COUNT(team2) AS 'num_match' FROM ipl_OLAP.all_matches
        WHERE team1 = %s
        GROUP BY team2
        UNION ALL
        SELECT team1, COUNT(team2) FROM ipl_OLAP.all_matches
        WHERE team2 = %s
        GROUP BY team1) a1
        GROUP BY a1.team2) b1
        WHERE b1.rank = 1
                                             ''', (team_name, team_name))
        most_against = _self.my_cursor.fetchall()
        t=[]
        m=[]
        for i in most_against:
            t.append(i[0])
            m.append(f'({i[1]})')
        most_against_df = pd.DataFrame({'Team': t, 'Matches':m})
        most_against_df = most_against_df.to_string(index=False, header=False)


        # because I don't know why
        _self.my_cursor.fetchall()

        _self.my_cursor.execute('''
                                SELECT  COUNT(*) FROM ipl_OLAP.all_matches
                                WHERE winner = %s AND toss_decision = 'bat'
                                                        ''', (team_name,))
        won_bat = _self.my_cursor.fetchone()[0]

        _self.my_cursor.execute('''
                                SELECT  COUNT(*) FROM ipl_OLAP.all_matches
                                WHERE winner = %s AND toss_decision = 'field'
                                                ''', (team_name,))
        won_field = _self.my_cursor.fetchone()[0]

        df = pd.DataFrame({'Team Status': status, 'First Season': first_season, 'Matches Played': against, 'Most Against': most_against_df , 'Won': won, 'Lost': against - won,
                           'Won by Batting First': won_bat, 'Won by Fielding First': won_field,
                           'Win %': f'{round(float(won / against * 100), 2)} %', 'Titles Won': titles}, index=['Value'])
        return df.transpose()





    def matches_won_lost(_self, team_name):
        query = '''
        WITH bigtable1 AS (SELECT a1.toss_decision, won, lost FROM (SELECT toss_decision,COUNT(*) AS 'lost' FROM ipl_OLAP.all_matches
        WHERE (team1 = %s OR team2 = %s ) AND winner != %s
        GROUP BY toss_decision
        ) a1
        LEFT JOIN
        (SELECT  toss_decision, COUNT(*) AS 'won' FROM ipl_OLAP.all_matches
        WHERE (team1 = %s OR team2 = %s ) AND winner = %s
        GROUP BY toss_decision) a2
        ON a1.toss_decision = a2.toss_decision
        UNION
        SELECT a1.toss_decision, won, lost FROM (SELECT toss_decision, COUNT(*) AS 'lost' FROM ipl_OLAP.all_matches
        WHERE (team1 = %s OR team2 = %s ) AND winner != %s
        GROUP BY toss_decision) a1
        RIGHT JOIN
        (SELECT  toss_decision, COUNT(*) AS 'won' FROM ipl_OLAP.all_matches
        WHERE (team1 = %s OR team2 = %s ) AND winner = %s
        GROUP BY toss_decision) a2
        ON a1.toss_decision = a2.toss_decision)
        
        SELECT toss_decision, IF(won IS NULL, 0, won) AS _won, IF(lost IS NULL, 0 , lost) AS _lost FROM bigtable1;
        '''

        df = pd.read_sql(query, _self.mydb, params=(
        team_name, team_name, team_name, team_name, team_name, team_name, team_name, team_name, team_name, team_name,
        team_name, team_name,))
        return df.sort_values(by='toss_decision')

    def team_match_by_season(self, team):
        query = '''
        SELECT season, COUNT(*) AS 'num' FROM ipl_OLAP.all_matches
        WHERE team1=%s OR team2=%s
        GROUP BY season;
        '''
        df = pd.read_sql(query, self.mydb, params=(team, team))
        return df.sort_values(by='season')

    def match_wonloss_by_season(self, team):
        query = '''
        SELECT a1.season, won, lost FROM (SELECT season, COUNT(*) AS 'won' FROM ipl_OLAP.all_matches
        WHERE winner = %s
        GROUP BY season) a1
        JOIN
        (SELECT season, COUNT(*) AS 'lost' FROM ipl_OLAP.all_matches
        WHERE (team1 = %s OR team2 = %s) AND winner != %s
        GROUP BY season) a2
        ON a1.season = a2.season;
        '''
        df = pd.read_sql(query, self.mydb, params=(team, team, team, team))
        return df

    def team_match_by_city(self, team):
        query = '''
        SELECT season, city, COUNT(city) AS 'No. of Matches in City' FROM all_matches
        WHERE team1 = %s OR team2 = %s
        GROUP BY season, city;
        '''
        df = pd.read_sql(query, self.mydb, params=(team, team))
        return df

    def won_against(self, team):
        query = '''
       SELECT won_against, SUM(num_times) AS Won FROM (SELECT team2 AS 'won_against', COUNT(team2) 'num_times' FROM all_matches
        WHERE team1 = %s AND winner = %s
        GROUP BY won_against
        UNION ALL
        SELECT team1 AS 'won_against', COUNT(team1) 'num_times' FROM all_matches
        WHERE team2 = %s AND winner = %s
        GROUP BY won_against) g1
        GROUP BY won_against
        '''
        self.my_cursor.fetchall()
        df = pd.read_sql(query, self.mydb, params=(team, team, team, team))
        return df

    def loss_against(self, team):
        query = '''
        SELECT lost_against, SUM(num_times) AS Lost  FROM (SELECT team2 AS 'lost_against', COUNT(team2) 'num_times' FROM all_matches
        WHERE team1 = %s AND winner != %s
        GROUP BY lost_against
        UNION ALL
        SELECT team1 AS 'lost_against', COUNT(team1) 'num_times' FROM all_matches
        WHERE team2 = %s AND winner != %s
        GROUP BY lost_against) h1
        GROUP BY lost_against
        '''
        self.my_cursor.fetchall()
        df = pd.read_sql(query, self.mydb, params=(team, team, team, team))
        return df

    def against_team_by_season(self, team):
        query = '''
        SELECT season, against, SUM(num_matches) AS 'matches' FROM (SELECT season, team2 AS 'against', COUNT(team2) AS 'num_matches' FROM all_matches
        WHERE team1 = %s
        GROUP BY season, team2
        UNION ALL
        SELECT season, team1, COUNT(team1) AS 'num_matches' FROM all_matches
        WHERE team2 = %s
        GROUP BY season, team1) i1
        GROUP BY season, against
        '''
        self.my_cursor.fetchall()
        df = pd.read_sql(query, self.mydb, params=(team, team))
        return df

    def grouped_stacked_won(self, team):
        query = '''
        SELECT season, against, SUM(won) AS all_won FROM (SELECT season, team2 AS against, COUNT(team2) AS won FROM all_matches
        WHERE team1 = %s AND winner = %s
        GROUP BY Season, team2
        UNION ALL
        SELECT season, team1, COUNT(team1) AS won FROM all_matches
        WHERE team2 = %s AND winner = %s
        GROUP BY Season, team1) a1
        GROUP BY season, against;
        '''
        self.my_cursor.fetchall()
        df = pd.read_sql(query, self.mydb, params=(team, team, team, team))
        return df

    def grouped_stacked_lost(self,team):
        query = '''
        SELECT season, against, SUM(lost) AS all_lost FROM (SELECT season, team2 AS against, COUNT(team2) AS lost FROM all_matches
        WHERE team1 = %s AND winner != %s
        GROUP BY Season, team2
        UNION ALL
        SELECT season, team1, COUNT(team1) AS won FROM all_matches
        WHERE team2 = %s AND winner != %s
        GROUP BY Season, team1) a1
        GROUP BY season, against
        '''
        df = pd.read_sql(query, self.mydb, params=(team, team, team, team))
        return df

    def all_match_piechart_by_team(self,team):
        query = '''
        SELECT Against, SUM(matches) AS 'No. of Matches' FROM (SELECT team2 AS 'Against', COUNT(team2) AS 'matches' FROM all_matches
        WHERE team1 = %s
        GROUP BY team2
        UNION ALL
        SELECT team1, COUNT(team1) AS 'matches' FROM all_matches
        WHERE team2 = %s
        GROUP BY team1) a1
        GROUP BY Against
        '''
        df = pd.read_sql(query, self.mydb, params=(team,team))
        return df

    def all_maidens(self):
        self.my_cursor.execute('''
                SELECT  COUNT(overs)  AS 'maiden_overs' FROM (SELECT season, match_id, innings, FLOOR(ball) AS overs,COUNT(ball) AS num_of_ball, SUM(runs_off_bat)+SUM(extras) AS 'total' FROM all_deliveries
                WHERE innings < 3
                GROUP BY season, match_id, innings, FLOOR(ball)
                HAVING total=0 AND num_of_ball  = 6 ) b1
                        ''')
        data = self.my_cursor.fetchall()
        s = []
        for i in data:
            s.append(i[0])

        return s[0]

    @st.cache_data
    def all_hattricks(_self):
        _self.my_cursor.execute('''
                       CALL hatTrick_player_by_season()
                                ''')
        data = _self.my_cursor.fetchall()
        s = []
        b=[]
        ht=[]
        tht=[]
        for i in data:
            s.append(i[0])
            b.append(i[1])
            ht.append(i[2])
            tht.append(i[3])
        df = pd.DataFrame({'Season': s, 'Bowler':b, 'Hat Tricks': ht, 'Total':tht})
        return df

    @st.cache_data
    def maiden_overs_by_season(_self):
        _self.my_cursor.execute('''
        SELECT season, COUNT(overs)  AS 'maiden_overs' FROM (SELECT season, match_id, innings, FLOOR(ball) AS overs,COUNT(ball) AS num_of_ball, SUM(runs_off_bat)+SUM(extras) AS 'total' FROM ipl_OLAP.all_deliveries
        WHERE innings < 3
        GROUP BY season, match_id, innings, FLOOR(ball)
        HAVING total=0 AND num_of_ball  = 6 ) b1
        GROUP BY season
        ORDER BY season ASC
                ''')
        data = _self.my_cursor.fetchall()
        s = []
        num =[]
        for i in data:
            s.append(i[0])
            num.append(i[1])
        return s,num

    def hattricks_by_season(self):
        self.my_cursor.execute('''
                
                        ''')
        data = self.my_cursor.fetchall()
        s = []
        num = []
        for i in data:
            s.append(i[0])
            num.append(i[1])
        return s, num

    def all_batsman_names(self):
        batsman = []
        self.my_cursor.execute('''
        SELECT striker AS 'batsman' FROM ipl_OLAP.all_deliveries
        GROUP BY striker
        ''')
        data = self.my_cursor.fetchall()
        for item in data:
            batsman.append(item[0])

        return batsman

    def all_bowler_names(self):
        bowler = []
        self.my_cursor.execute('''
        SELECT bowler FROM ipl_OLAP.all_deliveries
        GROUP BY bowler
        ''')
        data = self.my_cursor.fetchall()
        for item in data:
            bowler.append(item[0])

        return bowler


if __name__ == "__main__":
    pass
