import json
import re
from datetime import datetime, timedelta

import pandas as pd
import requests
from requests_html import HTMLSession
from bs4 import BeautifulSoup


class NBAFeeder:
    def __init__(self):
        self.site_url = "http://www.espn.com"

        self.team_info = pd.read_csv("NBA_team_name.csv")
        self.team_info.columns = [
            "full_name",
            "abbreviation",
            "mandarin_name",
            "mandarin_abbr",
            "color1",
            "color2",
        ]

    def _load_team_info(self):
        team_info = pd.read_csv("./data/NBA_team_name.csv")
        team_info.columns = [
            "full_name",
            "abbreviation",
            "mandarin_name",
            "mandarin_abbr",
            "color1",
            "color2",
        ]
        return team_info

    def _get_game_ids(self):
        start_date = self.start_date.strftime("%Y%m%d")
        data = requests.get(
            f"https://secure.espn.com/core/nba/schedule/_/date/{start_date}?table=true"
        ).json()
        schedule = data["table"].split('<h2 class="table-caption">')[1]
        pattern = r'href="/nba/game/_/gameId/(\d+)"'
        game_ids = re.findall(pattern, schedule)
        return game_ids

    def _is_final(self, game_id):
        try:
            session = HTMLSession()
            r = session.get(f"https://www.espn.com/nba/boxscore/_/gameId/{game_id}")
            r.html.render()
            resp = r.html.raw_html
            soup = BeautifulSoup(resp, "lxml")
            status_detail = soup.select_one("div.ScoreCell__Time").text
        except:
            return False
        return status_detail[:5].lower() == "final", soup

    def _get_game_stats(self, game_id, box_soup):
        stat_json = {}

        box_soup = box_soup

        stat_json["game_time"] = datetime.today().strftime("%Y-%m-%d")
        stat_json["excerpt"] = f"📢 NBA 戰報 📢"

        away_quarter_score, home_quarter_score = self._get_quarter_score(box_soup)

        two_teams_name = box_soup.select_one("div.Gamestrip__Competitors").select(
            "div.ScoreCell__TeamName"
        )

        away = self._team_score_streak(two_teams_name[0].text)
        home = self._team_score_streak(two_teams_name[1].text)

        team_away = self._get_team_df(box_soup, 0)
        team_home = self._get_team_df(box_soup, 2)

        away.update(
            {
                "players": self._set_dnp_starter_eff_status(team_away),
                "team_score": away_quarter_score,
            }
        )
        home.update(
            {
                "players": self._set_dnp_starter_eff_status(team_home),
                "team_score": home_quarter_score,
            }
        )
        stat_json["away"] = away
        stat_json["home"] = home
        return stat_json

    def _get_stat_excerpt(self, soup, position):
        player = (
            soup.select_one("div.GameLeaders__Leaders")
            .select("span.Athlete__PlayerName")[position]
            .text
        )
        team = (
            soup.select_one("div.GameLeaders__Leaders")
            .select("span.Athlete__NameDetails")[position]
            .text.split("-")[-1]
            .strip()
        )
        points = (
            soup.select_one("div.GameLeaders__Leaders")
            .select("span.Athlete__Stats--value")[position * 3]
            .text
        )
        return player, team, points

    def _get_quarter_score(self, box_soup):
        html = box_soup.find(name="div", attrs={"class": "Table__Scroller"})
        score = pd.read_html(str(html))[0]
        score = score.rename(
            columns={
                "Unnamed: 0": "TNT",
                "1": "1ST",
                "2": "2ND",
                "3": "3RD",
                "4": "4TH",
                "T": "TOT",
            }
        )

        score = score.drop(columns="TNT")
        team_score = json.loads(score.to_json(orient="records"))
        return team_score[0], team_score[1]

    def _team_score_streak(self, abbr):
        abbreviation = abbr
        team_full_name = self.team_info[self.team_info["abbreviation"] == abbreviation][
            "full_name"
        ].to_list()[0]
        mandarin_name = self.team_info[self.team_info["abbreviation"] == abbreviation][
            "mandarin_name"
        ].to_list()[0]
        mandarin_abbr = self.team_info[self.team_info["abbreviation"] == abbreviation][
            "mandarin_abbr"
        ].to_list()[0]
        color1 = self.team_info[self.team_info["abbreviation"] == abbreviation][
            "color1"
        ].to_list()[0]
        color2 = self.team_info[self.team_info["abbreviation"] == abbreviation][
            "color2"
        ].to_list()[0]

        return {
            "abbreviation": abbreviation,
            "team_full_name": team_full_name,
            "mandarin_name": mandarin_name,
            "mandarin_abbr": mandarin_abbr,
            "color1": color1,
            "color2": color2,
            "streak": "",
        }

    def _get_team_df(self, box_soup, idx):
        p1 = pd.read_html(str(box_soup.select_one("div.Boxscore")))[idx]
        d1 = pd.read_html(str(box_soup.select_one("div.Boxscore")))[idx + 1]
        df = pd.concat([p1, d1], axis=1)
        df.columns = [str(x) for x in list(df.iloc[0])]
        df = df[df["MIN"] != "MIN"]
        if "nan" in df.columns:
            df.drop(columns="nan", inplace=True)
        df.rename(columns={"starters": "Players"}, inplace=True)
        return df

    def _set_dnp_starter_eff_status(self, df):
        # df["Players"] = df["Players"].apply(lambda x: x.split("/")[0])
        df["DNP"] = df["MIN"].apply(lambda x: True if str(x)[:3] == "DNP" else False)
        starter = df.head(5)["Players"].to_list()
        df["STARTER"] = df["Players"].apply(lambda x: True if x in starter else False)
        df = self._set_eff(df)
        df.fillna("", inplace=True)
        df = self._set_highlight(df)
        results = json.loads(df.to_json(orient="records"))
        return results

    def _set_eff(self, df):
        df["MISS"] = df["FG"].apply(lambda x: self._miss_ball_count(x)) + df[
            "FT"
        ].apply(lambda x: self._miss_ball_count(x))
        eff_df = pd.DataFrame()
        for col in ["REB", "AST", "STL", "BLK", "PTS", "TO", "MISS"]:
            series = df[col]
            eff_df[col] = pd.to_numeric(series, errors="coerce")
        df["EFF"] = (
            eff_df["REB"]
            + eff_df["AST"]
            + eff_df["BLK"]
            + eff_df["PTS"]
            + eff_df["STL"]
            - eff_df["TO"]
            - eff_df["MISS"]
        )
        df.drop(columns="MISS", inplace=True)
        df.iloc[(-2, -1)] = ""
        return df

    def _miss_ball_count(self, ratio):
        try:
            attemp = ratio.split("-")[1]
            made = ratio.split("-")[0]
            return int(attemp) - int(made)
        except:
            return ""

    def _set_highlight(self, df):
        players_df = df.iloc[:-2]
        total_df = df.iloc[-2:]
        for column in players_df.columns:
            if column == "MIN":
                players_df[column] = players_df[column].apply(
                    lambda x: {"text": x, "highlight": "good"}
                    if str(x).isdigit() and int(x) > 40
                    else {"text": x}
                )
            elif column == "Players":
                players_df[column] = players_df[column].apply(
                    lambda x: {"text": x}
                    if self._is_triple_double(x, players_df)
                    else {"text": x, "highlight": "good"}
                )
            elif column == "FG":
                players_df[column] = players_df[column].apply(
                    lambda x: {"text": x, "highlight": self._get_fg_highlight(x)}
                    if self._get_fg_highlight(x)
                    else {"text": x}
                )
            elif column == "3PT":
                players_df[column] = players_df[column].apply(
                    lambda x: {"text": x, "highlight": self._get_3pt_highlight(x)}
                    if self._get_3pt_highlight(x)
                    else {"text": x}
                )
            elif column == "FT":
                players_df[column] = players_df[column].apply(
                    lambda x: {"text": x, "highlight": self._get_ft_highlight(x)}
                    if self._get_ft_highlight(x)
                    else {"text": x}
                )
            elif column in ["OREB", "DREB", "REB", "AST", "STL", "BLK"]:
                players_df[column] = players_df[column].apply(
                    lambda x: {"text": x, "highlight": self._get_stat_highlight(x)}
                    if self._get_stat_highlight(x)
                    else {"text": x}
                )
            elif column in ["TO", "PF"]:
                players_df[column] = players_df[column].apply(
                    lambda x: {
                        "text": x,
                        "highlight": self._get_negative_stat_highlight(x),
                    }
                    if self._get_negative_stat_highlight(x)
                    else {"text": x}
                )
            elif column == "PTS":
                players_df[column] = players_df[column].apply(
                    lambda x: {"text": x, "highlight": self._get_points_highlight(x)}
                    if self._get_points_highlight(x)
                    else {"text": x}
                )
            elif column == "+/-":
                players_df[column] = players_df[column].apply(
                    lambda x: {"text": x, "highlight": self._get_plusminus_highlight(x)}
                    if self._get_plusminus_highlight(x)
                    else {"text": x}
                )
            elif column == "EFF":
                players_df[column] = players_df[column].apply(
                    lambda x: {
                        "text": self._set_integer_str(x),
                        "highlight": self._get_eff_highlight(x),
                    }
                    if self._get_eff_highlight(x)
                    else {"text": self._set_integer_str(x)}
                )
            elif column in ["DNP", "STARTER"]:
                pass
        for column in total_df.columns:
            if column in ["DNP", "STARTER"]:
                pass
            else:
                total_df[column] = total_df[column].apply(lambda x: {"text": x})
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
                count += 1
        # 如果未來有大三元需求可在這調整
        return count >= 3

    def _get_fg_highlight(self, shoot_made_attempted):
        if self._is_percentage(shoot_made_attempted):
            made = int(shoot_made_attempted.split("-")[0])
            attempted = int(shoot_made_attempted.split("-")[1])
            if made / attempted >= 0.7:
                return "good"
            elif made / attempted < 0.3:
                return "bad"
        return ""

    def _get_3pt_highlight(self, shoot_made_attempted):
        if self._is_percentage(shoot_made_attempted):
            made = int(shoot_made_attempted.split("-")[0])
            attempted = int(shoot_made_attempted.split("-")[1])
            if made / attempted >= 0.5:
                return "good"
            elif made / attempted <= 0.25:
                return "bad"
        return ""

    def _get_ft_highlight(self, shoot_made_attempted):
        if self._is_percentage(shoot_made_attempted):
            made = int(shoot_made_attempted.split("-")[0])
            attempted = int(shoot_made_attempted.split("-")[1])
            if made / attempted >= 0.9:
                return "good"
            elif made / attempted <= 0.5:
                return "bad"
        return ""

    def _is_percentage(self, shoot_made_attempted):
        attempted = 0
        if shoot_made_attempted[0].isdigit() and "-" in shoot_made_attempted:
            attempted = int(shoot_made_attempted.split("-")[1])
        return True if attempted > 0 else False

    def _get_stat_highlight(self, stat):
        if self._is_number(str(stat)):
            if float(stat) >= 10:
                return "good"
        return ""

    def _get_negative_stat_highlight(self, stat):
        if self._is_number(str(stat)):
            if float(stat) == 0:
                return "good"
            elif float(stat) >= 6:
                return "bad"
        return ""

    def _get_plusminus_highlight(self, stat):
        if self._is_number(str(stat)):
            if float(stat) >= 20:
                return "good"
            elif float(stat) <= -20:
                return "bad"
        return ""

    def _get_points_highlight(self, points):
        if self._is_number(str(points)):
            if float(points) >= 30:
                return "good"
        return ""

    def _set_integer_str(self, stat):
        try:
            if self._is_number(str(stat)):
                return str(int(stat))
        except:
            return stat
        return stat

    def _get_eff_highlight(self, stat):
        try:
            if self._is_number(str(stat)):
                if float(stat) >= 30:
                    return "good"
                elif float(stat) < 0:
                    return "bad"
        except:
            return ""
        return ""

    def _is_number(self, num):
        pattern = re.compile(r"^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$")
        result = pattern.match(num)
        return True if result else False


if __name__ == "__main__":
    bot = NBAFeeder()
    a, b = bot._is_final(401360442)
    print(a)
    stat = bot._get_game_stats(401360442, b)
    print(stat)
