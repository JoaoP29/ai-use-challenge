import pytest
from quake_parser import QuakeLogParser, Game
from datetime import datetime


@pytest.fixture
def sample_log_lines():
    return [
        "0:00 InitGame: \\sv_floodProtect\\1\\sv_maxPing\\0\\sv_minPing\\0\\sv_maxRate\\10000\\sv_minRate\\0\\sv_hostname\\Code Miner Server\\g_gametype\\0\\sv_privateClients\\2\\sv_maxclients\\16\\sv_allowDownload\\0\\dmflags\\0\\fraglimit\\20\\timelimit\\15\\g_maxGameClients\\0\\capturelimit\\8\\version\\ioq3 1.36 linux-x86_64 Apr 12 2009\\protocol\\68\\mapname\\q3dm17\\gamename\\baseq3\\g_needpass\\0",
        "0:15 Kill: 1022 2 22: <world> killed Isgalamido by MOD_TRIGGER_HURT",
        "0:30 Kill: 3 2 10: Isgalamido killed Dono da Bola by MOD_RAILGUN",
        "1:00 Kill: 3 2 10: Isgalamido killed Zeh by MOD_RAILGUN",
        "1:15 Exit: Fraglimit hit."
    ]


def test_parse_game(sample_log_lines):
    parser = QuakeLogParser("dummy.txt")
    game = parser.parse_game(sample_log_lines)
    
    assert game.total_kills == 3
    assert game.players == {"Isgalamido", "Dono da Bola", "Zeh"}
    assert game.kills == {
        "Isgalamido": 2,
        "Dono da Bola": -1,
        "Zeh": 0
    }
    assert game.kills_by_means == {
        "MOD_TRIGGER_HURT": 1,
        "MOD_RAILGUN": 2
    }
    assert game.status == "completed"
    assert game.start_time == datetime.strptime("0:00", "%H:%M")
    assert game.end_time == datetime.strptime("1:15", "%H:%M")


def test_aborted_game():
    parser = QuakeLogParser("dummy.txt")
    game = parser.parse_game([
        "0:00 InitGame: ...",
        "0:15 Exit: Timelimit hit."
    ])
    
    assert game.total_kills == 0
    assert game.players == set()
    assert game.kills == {}
    assert game.kills_by_means == {}
    assert game.status == "aborted"


def test_generate_ranking():
    parser = QuakeLogParser("dummy.txt")
    
    # Create sample games
    game1 = Game()
    game1.players = {"Isgalamido", "Dono da Bola"}
    game1.kills = {"Isgalamido": 2, "Dono da Bola": 0}
    game1.status = "completed"
    
    game2 = Game()
    game2.players = {"Isgalamido", "Zeh"}
    game2.kills = {"Isgalamido": 1, "Zeh": 3}
    game2.status = "completed"
    
    parser.games = {
        "game_1": game1,
        "game_2": game2
    }
    
    ranking = parser.generate_ranking()
    assert ranking == [
        "1. Zeh - 3 kills",
        "2. Isgalamido - 3 kills",
        "3. Dono da Bola - 0 kills"
    ] 