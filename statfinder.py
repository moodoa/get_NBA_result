import re
import json
import requests
import pandas as pd

from bs4 import BeautifulSoup
from datetime import datetime, timedelta


class StatFinder():
    def __init__(self, date):
        self.site_url = "http://www.espn.com"
        self.date = date

    def receive(self):
        game_ids = self._get_game_ids()
        game_tuples = [
            (game_id, 0)
            for game_id in game_ids
        ]
        all_game_stats = []
        while len(game_tuples) > 0:
            game_id, retry_time = game_tuples.pop(0)
            if retry_time >= 3:
                continue
            if self._is_final(game_id):
                game_stats = self._get_game_stats(game_id)
                all_game_stats.append(game_stats)
            else:
                print((game_id, retry_time + 1))
                game_tuples.append((game_id, retry_time + 1))
                continue
        return all_game_stats

    def _get_game_ids(self):
        content = requests.get(f"{self.site_url}/nba/schedule/_/date/{self.date}").content
        soup = BeautifulSoup(content,"html.parser")
        sched_container = soup.find(name="div", attrs={"id":"sched-container"})
        today_game_id_html = []
        for tag in sched_container:
            if len(today_game_id_html) != 0 and tag.name == "h2":
                break
            elif tag.attrs == {"class": ["responsive-table-wrap"]}:
                today_game_id_html.append(tag)
        game_ids = []
        for idx in range(len(today_game_id_html)):
            elements = today_game_id_html[idx].select("a")
            for element in elements:
                if "/nba/game?gameId=" in element.attrs["href"]:
                    game_ids.append(element.attrs["href"].split("=")[1])
        return game_ids

    def _is_final(self, game_id):
        try:
            content = requests.get(f"{self.site_url}/nba/boxscore?gameId={game_id}").content
            soup = BeautifulSoup(content, "html.parser")
            status_detail = soup.find(name="span", attrs={"class":"status-detail"}).text
        except:
            return False
        return status_detail[:5] == "Final"

    def _get_game_stats(self, game_id):
        stat_json = {}
        content = requests.get(f"{self.site_url}/nba/game?gameId={game_id}").content
        soup = BeautifulSoup(content, "html.parser")
        z_time = soup.find(name="div", attrs={"class":"game-date-time"}).span["data-date"]
        stat_json["game_time"] = z_time
        away_quarter_score, home_quarter_score = self._get_quarter_score(game_id)
        
        url = f"{self.site_url}/nba/boxscore?gameId={game_id}"
        web = requests.get(url)
        content = web.content
        soup = BeautifulSoup(content, "html.parser")
        html = soup.find(name="div", attrs={"class": "competitors"})
        game_result = pd.read_html(str(html))[0]
        col = game_result.columns.to_list()
        col[0] = "Team"
        game_result.columns = col

        away = self._team_score_streak(soup, game_result, 0)
        home = self._team_score_streak(soup, game_result, 1)
        
        stat = soup.find(name="div", attrs={"id": "gamepackage-boxscore-module"})
        for abbr in soup.find_all(name="span", attrs={"class": "abbr"}):
            abbr.decompose()
        for position in stat.find_all(name="span", attrs={"class": "position"}):
            position.insert_before("/")
        
        team_away = self._get_team_df(stat, 0)
        team_home = self._get_team_df(stat, 1)

        away.update({"players": self._set_dnp_starter_status(team_away), "team_score": away_quarter_score})
        home.update({"players": self._set_dnp_starter_status(team_home), "team_score": home_quarter_score})

        stat_json["away"] = away
        stat_json["home"] = home

        return stat_json

    def _get_quarter_score(self, game_id):
        content = requests.get(f"https://www.espn.com/nba/boxscore?gameId={game_id}").content
        soup = BeautifulSoup(content,"html.parser")
        html = soup.find(name="div" , attrs={"class":"game-status"})
        score = pd.read_html(str(html))[0]
        score = score.rename(columns={"Unnamed: 0":"team","1":"1ST","2":"2ND","3":"3RD","4":"4TH","T":"TOT"})
        score = score.drop(columns="team")
        team_score = json.loads(score.to_json(orient="records"))
        return team_score[0], team_score[1] 

    def _team_score_streak(self, soup, game_result, index):
        streaks = []
        for record in soup.find_all(name="div", attrs={"class": "record"}):
            streaks.append(record.text)
        for streak_idx in range(len(streaks)):
            if "," in streaks[streak_idx]:
                streaks[streak_idx] = streaks[streak_idx].split(",")[0]

        abbreviation = game_result.iloc[index].to_list()[0]
        streak = streaks[index]

        return {
            "abbreviation": abbreviation,
            "streak": streak,
        }

    def _get_team_df(self, stat, idx):
        team = pd.read_html(str(stat))[idx]
        column_list = team.columns.tolist()
        column = []
        for col_a, col_b in column_list:
            column.append(col_a)
        column[0] = "Players"
        team.columns = column
        team.fillna("", inplace=True)
        return team

    def _set_dnp_starter_status(self, df):
        df["Players"] = df["Players"].apply(lambda x: x.split("/")[0])
        df["DNP"] = df["MIN"].apply(lambda x: True if str(x)[:3]=="DNP" else False)
        starter = df.head(5)["Players"].to_list()
        df["STARTER"] = df["Players"].apply(lambda x:True if x in starter else False)
        df = self._set_highlight(df)
        results = json.loads(df.to_json(orient="records"))
        return results

    def _set_highlight(self, df):
        players_df = df.iloc[:-2]
        total_df = df.iloc[-2:]
        for column in ["Players", "MIN", "FG", "3PT", "FT", "OREB", "DREB", "REB", "AST", "STL", "BLK", "TO", "PF", "+/-", "PTS"]:
            if column == "MIN":
                players_df[column] = players_df[column].apply(lambda x: {"text":x, "highlight":"good"} if str(x).isdigit() and int(x) > 40 else {"text":x, "highlight":""})
            elif column == "Players":
                players_df[column] = players_df[column].apply(lambda x: {"text":x, "highlight":self._is_triple_double(x, players_df)})
            elif column == "FG":
                players_df[column] = players_df[column].apply(lambda x: {"text":x, "highlight":self._get_fg_highlight(x)})
            elif column == "3PT":
                players_df[column] = players_df[column].apply(lambda x: {"text":x, "highlight":self._get_3pt_highlight(x)})
            elif column == "FT":
                players_df[column] = players_df[column].apply(lambda x: {"text":x, "highlight":self._get_ft_highlight(x)})
            elif column in ["OREB", "DREB", "REB", "AST", "STL", "BLK"]:
                players_df[column] = players_df[column].apply(lambda x: {"text":x, "highlight":self._get_stat_highlight(x)})
            elif column in ["TO", "PF"]:
                players_df[column] = players_df[column].apply(lambda x: {"text":x, "highlight":self._get_negative_stat_highlight(x)})
            elif column == "PTS":
                players_df[column] = players_df[column].apply(lambda x: {"text":x, "highlight":self._get_points_highlight(x)})
        df = pd.concat([players_df, total_df])
        return df

    def _is_triple_double(self, player, df):
        positive_stat = []
        for column in ["REB", "AST", "STL", "BLK", "PTS"]:
            try:
                positive_stat.append(int(df[df["Players"] == player][column].values[0]))
            except:
                positive_stat.append(0)
        count = 0 
        for stat in positive_stat:
            if stat >= 10:
                count +=1
        return "good" if count >= 3 else ""

    def _is_percentage(self, shoot_made_attempted):
        if shoot_made_attempted[0].isdigit() and "-" in shoot_made_attempted:
            attempted = int(shoot_made_attempted.split("-")[1])
            return True if attempted > 0 else False
    
    def _get_fg_highlight(self, shoot_made_attempted):
        if self._is_percentage(shoot_made_attempted):
            made = int(shoot_made_attempted.split("-")[0])
            attempted = int(shoot_made_attempted.split("-")[1])
            if made/attempted >= 0.7:
                return "good"
            elif made/attempted < 0.3:
                return "bad"
        return ""

    def _get_3pt_highlight(self, shoot_made_attempted):
        if self._is_percentage(shoot_made_attempted):
            made = int(shoot_made_attempted.split("-")[0])
            attempted = int(shoot_made_attempted.split("-")[1])
            if made/attempted >= 0.5:
                return "good"
            elif made/attempted <= 0.25:
                return "bad"
        return ""

    def _get_ft_highlight(self, shoot_made_attempted):
        if self._is_percentage(shoot_made_attempted):
            made = int(shoot_made_attempted.split("-")[0])
            attempted = int(shoot_made_attempted.split("-")[1])
            if made/attempted >= 0.9:
                return "good"
            elif made/attempted <= 0.5:
                return "bad"
        return ""

    def _get_stat_highlight(self, stat):
        if str(stat).isdigit():
            if int(stat) >= 10:
                return "good"
        return ""
    
    def _get_negative_stat_highlight(self, stat):
        if str(stat).isdigit():
            if int(stat) == 0:
                return "good"
            elif int(stat) >= 6:
                return "bad"
        return ""

    def _get_points_highlight(self, points):
        if str(points).isdigit():
            if int(points) >= 30:
                return "good"
        return ""

if __name__ == "__main__":
    finder = StatFinder("20200808")
    print(finder.receive())