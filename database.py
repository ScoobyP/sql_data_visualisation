import mysql.connector
from dotenv import load_dotenv
import os

class DB:

    def __init__(self):
        try:
            load_dotenv()
            self.mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password=f'{os.getenv("password")}',
                port='3306',
                database = 'cricket'
            )
            self.my_cursor = self.mydb.cursor()
            print('Connection Established')
        except:
            print('Connection Error')

    def fetch_all_player_names(self):
        # Extracting all player names

        all_names = []
        self.my_cursor.execute('''
        SELECT non_striker FROM cricket.ipl_all_matches
        UNION
        SELECT striker FROM cricket.ipl_all_matches
        UNION
        SELECT bowler FROM cricket.ipl_all_matches
        ''')
        #self.mydb.commit()
        all_player_names = self.my_cursor.fetchall()

        for name in all_player_names:
            all_names.append(name[0])

        return all_names

    def fetch_all_teams(self):
        ipl_teams = []
        #Extracting all team names

        self.my_cursor.execute('''
        SELECT batting_team FROM ipl_all_matches
        UNION
        SELECT bowling_team FROM ipl_all_matches
        ''')

        team_names = self.my_cursor.fetchall()
        for team in team_names:
            ipl_teams.append(team[0])

        return ipl_teams

    def matches_by_all_teams(self):
        teams = []
        matches = []
        self.my_cursor.execute('''
        WITH big_table AS (SELECT A1.batting_team, matches_played, matches FROM (SELECT batting_team, COUNT(DISTINCT match_id) AS 'matches_played' FROM ipl_all_matches
        GROUP BY batting_team) A1
        JOIN 
        (SELECT DISTINCT bowling_team, COUNT(DISTINCT match_id) AS 'matches' FROM ipl_all_matches
        GROUP BY bowling_team) A2
        ON A1.batting_team = A2.bowling_team)
        
        SELECT batting_team, GREATEST(matches_played, matches) AS 'total_played' FROM big_table
        ''')
        no_of_matches = self.my_cursor.fetchall()
        for item in no_of_matches:
            teams.append(item[0])
            matches.append(item[1])

        return teams,matches

    def total_six(self):
        sixes = []
        self.my_cursor.execute('''
        SELECT COUNT(*) FROM ipl_all_matches
        WHERE runs_off_bat = 6
        ''')
        data = self.my_cursor.fetchall()
        for item in data:
            sixes.append(item)

        return sixes[0][0]

    def total_fours(self):
        fours = []
        self.my_cursor.execute('''
        SELECT COUNT(*) FROM ipl_all_matches
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
        SELECT t1.season, total_sixes, total_fours FROM (SELECT season, COUNT(runs_off_bat) AS 'total_sixes' FROM ipl_all_matches
        WHERE runs_off_bat = 6
        GROUP BY season) t1
        JOIN (SELECT season, COUNT(runs_off_bat) AS 'total_fours' FROM ipl_all_matches
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
        SELECT COUNT(ball) FROM ipl_all_matches
                ''')
        data = self.my_cursor.fetchall()
        for item in data:
            balls_thrown.append(item[0])

        return balls_thrown

    def total_runs_given_in_extras(self):
        extras = []
        self.my_cursor.execute('''
        SELECT SUM(extras)+SUM(wides)+SUM(noballs) AS 'total_extras' FROM ipl_all_matches
                ''')
        data = self.my_cursor.fetchall()
        for item in data:
            extras.append(item[0])

        return extras

    def total_wickets_taken(self):
        wickets = []
        self.my_cursor.execute('''
        SELECT COUNT(wicket_type) FROM ipl_all_matches
        WHERE wicket_type != ''
                ''')
        data = self.my_cursor.fetchall()
        for item in data:
            wickets.append(item[0])

        return wickets

    def total_wickets_by_category_by_season(self):
        season = []
        wickets_category = []
        total_wickets =[]
        self.my_cursor.execute('''
        SELECT season, wicket_type, COUNT(wicket_type) AS 'total_wickets' FROM ipl_all_matches
        WHERE wicket_type != ''
        GROUP BY season, wicket_type
                ''')
        data = self.my_cursor.fetchall()
        for item in data:
            season.append(item[0])
            wickets_category.append(item[1])
            total_wickets.append(item[2])

        return season, wickets_category, total_wickets

    def all_extras_by_category_season(self):
        season = []
        wides = []
        noballs = []
        extras = []
        byes = []
        legbyes = []
        self.my_cursor.execute('''
        SELECT A1.season, A1.wides, A2.no_ball, A3.extras, A4.byes, A5.legbyes FROM (SELECT season, COUNT(wides) AS 'wides' FROM ipl_all_matches
        WHERE wides != ''
        GROUP BY season) A1
        JOIN  (SELECT season, COUNT(noballs) AS 'no_ball' FROM ipl_all_matches
        WHERE noballs != ''
        GROUP BY season) A2
        ON A1.season = A2.season
        JOIN (SELECT season, COUNT(extras) AS 'extras' FROM ipl_all_matches
        WHERE extras != ''
        GROUP BY season) A3
        ON A2.season = A3.season
        JOIN (SELECT season, COUNT(byes) AS 'byes' FROM ipl_all_matches
        WHERE byes != ''
        GROUP BY season) A4
        ON A3.season = A4.season
        JOIN (SELECT season, COUNT(legbyes) AS 'legbyes' FROM ipl_all_matches
        WHERE legbyes != ''
        GROUP BY season) A5
        ON A4.season = A5.season

        ''')
        data = self.my_cursor.fetchall()
        for item in data:
            season.append(item[0])
            wides.append(item[1])
            noballs.append(item[2])
            extras.append(item[3])
            byes.append(item[4])
            legbyes.append(item[5])

        return season, wides, noballs, extras, byes, legbyes

    def total_wides(self):
        all_wides = []
        self.my_cursor.execute('''
        SELECT COUNT(wides) AS 'wides' FROM ipl_all_matches
        WHERE wides != ''
        ''')
        data = self.my_cursor.fetchall()
        for item in data:
            all_wides.append(item[0])

        return all_wides[0]

    def total_noballs(self):
        all_noballs = []
        self.my_cursor.execute('''
        SELECT COUNT(noballs) AS 'no_balls' FROM ipl_all_matches
        WHERE noballs != ''
        ''')
        data = self.my_cursor.fetchall()
        for item in data:
            all_noballs.append(item[0])

        return all_noballs[0]

    def total_extras(self):
        all_extras = []
        self.my_cursor.execute('''
        SELECT COUNT(extras) AS 'extras' FROM ipl_all_matches
        WHERE extras != ''
        ''')
        data = self.my_cursor.fetchall()
        for item in data:
            all_extras.append(item[0])

        return all_extras[0]

    def total_byes(self):
        all_byes = []
        self.my_cursor.execute('''
        SELECT COUNT(byes) AS 'byes' FROM ipl_all_matches
        WHERE byes != ''
        ''')
        data = self.my_cursor.fetchall()
        for item in data:
            all_byes.append(item[0])

        return all_byes[0]

    def total_legbyes(self):
        all_legbyes = []
        self.my_cursor.execute('''
        SELECT COUNT(legbyes) AS 'legbyes' FROM ipl_all_matches
        WHERE legbyes != ''
        ''')
        data = self.my_cursor.fetchall()
        for item in data:
            all_legbyes.append(item[0])

        return all_legbyes[0]

    def total_wickets(self):
        self.my_cursor.execute('''
        SELECT COUNT(wicket_type) FROM ipl_all_matches
        WHERE wicket_type != ''
        ''')
        data = self.my_cursor.fetchone()
        return data[0]

    def total_matches(self):
        self.my_cursor.execute('''
        SELECT COUNT(DISTINCT match_id) AS 'all_matches' FROM ipl_all_matches
        ''')
        data = self.my_cursor.fetchone()
        return data[0]

    def all_batsman_names(self):
        batsman = []
        self.my_cursor.execute('''
        SELECT striker AS 'batsman' FROM ipl_all_matches
        GROUP BY striker
        ''')
        data = self.my_cursor.fetchall()
        for item in data:
            batsman.append(item[0])

        return batsman

    def all_bowler_names(self):
        bowler = []
        self.my_cursor.execute('''
        SELECT bowler FROM ipl_all_matches
        GROUP BY bowler
        ''')
        data = self.my_cursor.fetchall()
        for item in data:
            bowler.append(item[0])

        return bowler


