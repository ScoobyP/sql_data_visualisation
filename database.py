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

    def first_edition(self):
        self.my_cursor.execute('''
        SELECT season FROM all_deliveries
        GROUP BY  season
        ORDER BY season ASC LIMIT 1
        ''')
        data = self.my_cursor.fetchone()
        return data[0]

    def latest_edition(self):
        self.my_cursor.execute('''
        SELECT season FROM all_deliveries
        GROUP BY  season
        ORDER BY season DESC LIMIT 1
        ''')
        data = self.my_cursor.fetchone()
        return data[0]

    def next_edition(self):
        self.my_cursor.execute('''
        SELECT season + 1 AS 'next_season'
        FROM (SELECT season FROM all_deliveries
        GROUP BY  season
        ORDER BY season DESC LIMIT 1) t1
        ''')
        data = self.my_cursor.fetchone()
        return data[0]

    def num_of_current_teams(self):

        self.my_cursor.execute('''
                SELECT COUNT(DISTINCT all_deliveries.batting_team) AS 'num_teams'
                FROM all_deliveries
                WHERE season = (SELECT MAX(season) FROM all_deliveries);
                ''')
        data = self.my_cursor.fetchone()
        return data[0]

    def current_champion(self):

        self.my_cursor.execute('''
                SELECT winner FROM all_matches
                WHERE season = (SELECT MAX(season) FROM all_matches) AND
                                match_type = 'Final';
                ''')
        data = self.my_cursor.fetchone()
        return data[0]

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

    


    def fetch_current_and_defunct_teams(self):
        current_teams = self.fetch_current_teams()
        all_teams_pnp = []
        for team in self.matches_by_all_teams()[0]:
            if team not in current_teams:
                all_teams_pnp.append(team + ' *X*')
            else:
                all_teams_pnp.append(team)

        return sorted(all_teams_pnp)

    


    def matches_by_all_teams(self):
        teams = []
        matches = []
        self.my_cursor.execute('''
        WITH big_table AS (SELECT A1.batting_team, matches_played, matches FROM (SELECT batting_team, COUNT(DISTINCT match_id) AS 'matches_played' FROM ipl_OLAP.all_deliveries
        GROUP BY batting_team) A1
        JOIN 
        (SELECT DISTINCT bowling_team, COUNT(DISTINCT match_id) AS 'matches' FROM ipl_OLAP.all_deliveries
        GROUP BY bowling_team) A2
        ON A1.batting_team = A2.bowling_team)
        
        SELECT batting_team, GREATEST(matches_played, matches) AS 'total_played' FROM big_table
        ''')
        no_of_matches = self.my_cursor.fetchall()
        for item in no_of_matches:
            teams.append(item[0])
            matches.append(item[1])

        return sorted(teams), matches

    


    def fetch_cities_played_in(self):
        season = []
        city = []
        num_mat = []

        self.my_cursor.execute('''
        SELECT season, 
        city,
        COUNT(city) AS 'num_matches'
        FROM ipl_OLAP.all_matches
        GROUP BY season, city
        ''')
        data = self.my_cursor.fetchall()
        for i in data:
            season.append(i[0])
            city.append(i[1])
            num_mat.append(i[2])

        df_original = pd.DataFrame({'Season': season, 'City': city, 'Matches': num_mat})

        return df_original.sort_values('Season', ascending=True)

    


    def fetch_matches_by_season(self):
        num_matches = []
        season = []
        self.my_cursor.execute('''
        SELECT season, COUNT(*) AS 'num_matches' FROM ipl_OLAP.all_matches
        GROUP BY season
        ''')
        data= self.my_cursor.fetchall()
        for i in data:
            season.append(i[0])
            num_matches.append(i[1])

        return sorted(season), num_matches

    


    def total_ipl_runs(self):

        self.my_cursor.execute('''
        SELECT SUM(runs_off_bat)+SUM(extras) FROM ipl_OLAP.all_deliveries
        ''')
        runs = self.my_cursor.fetchone()
        return int(runs[0])#

    


    def total_runs(self):
        s = []
        run_scored= []
        run_extras = []
        all_runs = []
        self.my_cursor.execute('''
        SELECT season,SUM(runs_off_bat),SUM(extras), SUM(runs_off_bat)+SUM(extras) FROM ipl_OLAP.all_deliveries 
        GROUP BY season
        ''')
        data = self.my_cursor.fetchall()
        for i in data:
            s.append(i[0])
            run_scored.append(i[1])
            run_extras.append(i[2])
            all_runs.append(i[3])
        df= pd.DataFrame({'Season': s, 'Runs Scored': run_scored, 'Extras': run_extras, 'Total Runs': all_runs})
        return df

    


    def total_six(self):
        sixes = []
        self.my_cursor.execute('''
        SELECT COUNT(*) FROM ipl_OLAP.all_deliveries
        WHERE runs_off_bat = 6
        ''')
        data = self.my_cursor.fetchall()
        for item in data:
            sixes.append(item)

        return sixes[0][0]

    


    def total_fours(self):
        fours = []
        self.my_cursor.execute('''
        SELECT COUNT(*) FROM ipl_OLAP.all_deliveries
        WHERE runs_off_bat = 4
                ''')
        data = self.my_cursor.fetchall()
        for item in data:
            fours.append(item)

        return fours[0][0]

    


    def total_boundaries_by_season(self):
        season = []
        sixes = []
        fours = []
        self.my_cursor.execute('''
        SELECT t1.season, total_sixes, total_fours FROM (SELECT season, COUNT(runs_off_bat) AS 'total_sixes' FROM ipl_OLAP.all_deliveries
        WHERE runs_off_bat = 6
        GROUP BY season) t1
        JOIN (SELECT season, COUNT(runs_off_bat) AS 'total_fours' FROM ipl_OLAP.all_deliveries
        WHERE runs_off_bat = 4
        GROUP BY season) t2
        ON t1.season = t2.season
        ORDER BY t1.season
        ''')
        data = self.my_cursor.fetchall()
        for item in data:
            season.append(item[0])
            sixes.append(item[1])
            fours.append(item[2])

        return season, sixes, fours

    


    def total_balls_thrown(self):
        balls_thrown = []
        self.my_cursor.execute('''
        SELECT COUNT(ball) FROM ipl_OLAP.all_deliveries
                ''')
        data = self.my_cursor.fetchall()
        for item in data:
            balls_thrown.append(item[0])

        return balls_thrown

    


    def total_penalty(self):
        pen = []
        self.my_cursor.execute('''
        SELECT SUM(penalty) AS 'total_penalty' FROM ipl_OLAP.all_deliveries
        ''')
        data = self.my_cursor.fetchone()
        for i in data:
            pen.append(int(i))
        return pen[0]

    


    def total_wickets_by_category_by_season(self):
        season = []
        wickets_category = []
        total_wickets = []
        self.my_cursor.execute('''
        SELECT season, wicket_type, COUNT(wicket_type) AS 'total_wickets' FROM ipl_OLAP.all_deliveries
        WHERE wicket_type != ''
        GROUP BY season, wicket_type''')
        data = self.my_cursor.fetchall()
        for item in data:
            season.append(item[0])
            wickets_category.append(item[1])
            total_wickets.append(item[2])

        df = pd.DataFrame({'Season': season, 'Category': wickets_category, 'Total Wickets': total_wickets})
        df1 = df.sort_values(by='Season')
        return df1

    


    def all_extras_by_category_season(self):
        season = []
        wides = []
        noballs = []
        penalty = []
        byes = []
        legbyes = []
        self.my_cursor.execute('''
        SELECT season, SUM(wides), SUM(noballs), SUM(byes), SUM(legbyes), SUM(penalty)
        FROM ipl_OLAP.all_deliveries
        GROUP BY season
        ''')
        data = self.my_cursor.fetchall()
        for item in data:
            season.append(item[0])
            wides.append(item[1])
            noballs.append(item[2])
            byes.append(item[3])
            legbyes.append(item[4])
            penalty.append(item[5])

        df = pd.DataFrame({'Season': season, 'Wides':wides, 'No Balls': noballs, 'Penalty': penalty, 'Byes': byes, 'Leg Byes': legbyes  })
        df1 = df.sort_values(by='Season')
        return df1

    


    def total_wides(self):
        all_wides = []
        self.my_cursor.execute('''
        SELECT SUM(wides) AS 'wides' FROM ipl_OLAP.all_deliveries
        ''')
        data = self.my_cursor.fetchone()
        for item in data:
            all_wides.append(int(item))

        return all_wides[0]

    


    def total_noballs(self):
        all_noballs = []
        self.my_cursor.execute('''
        SELECT SUM(noballs) AS 'no_balls' FROM ipl_OLAP.all_deliveries
        ''')
        data = self.my_cursor.fetchone()
        for item in data:
            all_noballs.append(int(item))

        return all_noballs[0]

    


    def total_extras(self):
        all_extras = []
        self.my_cursor.execute('''
        SELECT SUM(extras) AS 'extras' FROM ipl_OLAP.all_deliveries
        ''')
        data = self.my_cursor.fetchone()
        for item in data:
            all_extras.append(int(item))

        return all_extras[0]

    


    def total_byes(self):
        all_byes = []
        self.my_cursor.execute('''
        SELECT SUM(byes) AS 'byes' FROM ipl_OLAP.all_deliveries
        ''')
        data = self.my_cursor.fetchone()
        for item in data:
            all_byes.append(int(item))

        return all_byes[0]

    


    def total_legbyes(self):
        all_legbyes = []
        self.my_cursor.execute('''
        SELECT SUM(legbyes) AS 'legbyes' FROM ipl_OLAP.all_deliveries
        ''')
        data = self.my_cursor.fetchone()
        for item in data:
            all_legbyes.append(int(item))

        return all_legbyes[0]

    


    def total_wickets(self):
        self.my_cursor.execute('''
        SELECT COUNT(wicket_type) FROM ipl_OLAP.all_deliveries
        WHERE wicket_type != ''
        ''')
        data = self.my_cursor.fetchone()
        return data[0]

    


    def total_matches(self):
        self.my_cursor.execute('''
        SELECT COUNT(DISTINCT match_id) AS 'all_matches' FROM ipl_OLAP.all_deliveries
        ''')
        data = self.my_cursor.fetchone()
        return data[0]

    


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