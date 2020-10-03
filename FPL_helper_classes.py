import numpy as np
import requests
from bs4 import BeautifulSoup
import os 
import csv

class Team_helper:
    def __init__(self):
        self.team_dict = {}

    def get_season_table(self, season):
        url = 'https://fixturedownload.com/results/epl-' + str(season)
        
        results_html = requests.get(url).text
        soup = BeautifulSoup(results_html, "lxml")
        results = soup.find("table")

        rows = results.find_all("tr")
        for row in rows[1:]:
            row_data = [i.text for i in row.find_all("td")][3:]
            self.update_dict(row_data)

    def update_dict(self, row_data):
        self.add_team_to_dict(row_data[0])
        self.add_team_to_dict(row_data[1])
        self.add_result_to_dict(row_data)
        
    def add_team_to_dict(self, team_name):
        if team_name not in self.team_dict:
            self.team_dict[team_name] = []
            
    def add_result_to_dict(self, row_data):
        result = row_data[2].split(' ')
        self.add_team_result(row_data[0], row_data[1], True, result[0], result[-1])
        self.add_team_result(row_data[1], row_data[0], False, result[-1], result[0])
        
    def add_team_result(self, team_name, opponent, home, goals_for, goals_against):
        self.team_dict[team_name].append([opponent, home, int(goals_for), int(goals_against)])
        
    def calculate_form(self, history):
        self.form_dict = {}
        
        for key in self.team_dict:
            self.form_dict[key] = []

        for key in self.team_dict:
            list_of_results = self.team_dict[key]
            list_of_results = [i[2:] for i in list_of_results]
            list_of_results = np.array(list_of_results)

            for i in range(38):
                average_stats = np.mean(list_of_results[max(i-history, 0):i], axis=0)
                self.form_dict[key].append(list(average_stats))

class Player_helper:
    def __init__(self):
        self.player_stat_dict = {}
        
    def read_all_player_data(self, season):
        data_path=f"data/{str(season)}/players"
        directory_list = [x[0] for x in os.walk(data_path)][1:]
        directory_list.sort()
        for directory in directory_list[1:]:
            player_id = self.get_player_id(directory)
            player_stats = self.read_player_csv(directory)
            
            if not np.all(player_stats == 0):
                self.player_stat_dict[player_id] = player_stats
    
    def read_player_csv(self, directory):
        path = directory + "/gw.csv"
        with open(path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            list_iterator = iter(csv_reader)
            headers = next(list_iterator)
            
            useful_headers = ['total_points', 'goals_scored', 'assists', 'clean_sheets', 'minutes', 'opponent_team']
            
            indexes = []
            for i, header in enumerate(headers):
                if header in useful_headers:
                    indexes.append(i)
                
            season_stats = []
            first_game_week = 0
            for row in list_iterator:
                #points, goals scored, assists, clean sheets, minutes, 
                gameweek_stats = [int(row[i]) for i in indexes]
                season_stats.append(gameweek_stats)
                
                if first_game_week == 0:
                    first_game_week = int(row[18])
        
            if len(season_stats) != 38:
                season_stats = (first_game_week-1)*[[0,0,0,0,0]] + season_stats
            
            if len(season_stats) == 38:
                array = np.array(season_stats)
                return array
            else:
                return np.zeros(2)

    def get_player_id(self, path):
        dir_breakdown = path.split('/')
        player_id = dir_breakdown[-1]
        return(player_id)