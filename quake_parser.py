from dataclasses import dataclass
from typing import Dict, List, Set
import re
from datetime import datetime
import json
from pathlib import Path


@dataclass
class Game:
    """Represents a single Quake game session."""
    total_kills: int = 0
    players: Set[str] = None
    kills: Dict[str, int] = None
    kills_by_means: Dict[str, int] = None
    status: str = "completed"
    start_time: datetime = None
    end_time: datetime = None

    def __post_init__(self):
        self.players = set()
        self.kills = {}
        self.kills_by_means = {}


class QuakeLogParser:
    """Parser for Quake 3 Arena server logs."""

    def __init__(self, log_file_path: str):
        self.log_file_path = Path(log_file_path)
        self.games: Dict[str, Game] = {}

    def parse_game(self, game_lines: List[str]) -> Game:
        """Parse a single game session from log lines."""
        game = Game()
        has_kills = False

        for line in game_lines:
            # Track game start time
            if "InitGame:" in line:
                try:
                    time_str = line.split()[0]
                    game.start_time = datetime.strptime(time_str, "%H:%M")
                except (ValueError, IndexError):
                    pass

            # Track game end time
            if "Exit:" in line or "ShutdownGame:" in line:
                try:
                    time_str = line.split()[0]
                    game.end_time = datetime.strptime(time_str, "%H:%M")
                except (ValueError, IndexError):
                    pass

            # Parse kill events
            kill_match = re.match(r"Kill: \d+ \d+ \d+: (.+) killed (.+) by (.+)", line)
            if kill_match:
                has_kills = True
                killer, victim, means = kill_match.groups()
                game.total_kills += 1

                # Update kills by means
                game.kills_by_means[means] = game.kills_by_means.get(means, 0) + 1

                # Handle victim
                if victim != "<world>":
                    game.players.add(victim)
                    if victim not in game.kills:
                        game.kills[victim] = 0

                # Handle killer
                if killer != "<world>":
                    game.players.add(killer)
                    game.kills[killer] = game.kills.get(killer, 0) + 1
                else:
                    game.kills[victim] = game.kills.get(victim, 0) - 1

        # Mark game as aborted if no kills occurred
        if not has_kills:
            game.status = "aborted"

        return game

    def generate_ranking(self) -> List[str]:
        """Generate a ranking of players across all games."""
        total_kills: Dict[str, int] = {}

        # Aggregate kills across all games
        for game in self.games.values():
            if game.status == "completed":
                for player, kills in game.kills.items():
                    total_kills[player] = total_kills.get(player, 0) + kills

        # Sort players by kills and generate ranking
        ranking = sorted(
            total_kills.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [f"{i+1}. {player} - {kills} kills" 
                for i, (player, kills) in enumerate(ranking)]

    def parse_log(self) -> Dict:
        """Parse the entire log file and generate a report."""
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as file:
                log_lines = file.readlines()

            current_game: List[str] = []
            game_count = 0

            # Group lines by game
            for line in log_lines:
                if "InitGame:" in line:
                    if current_game:
                        game_count += 1
                        self.games[f"game_{game_count}"] = self.parse_game(current_game)
                    current_game = [line]
                elif current_game:
                    current_game.append(line)

            # Process the last game
            if current_game:
                game_count += 1
                self.games[f"game_{game_count}"] = self.parse_game(current_game)

            # Generate final report
            return {
                "games": {
                    game_id: {
                        "total_kills": game.total_kills,
                        "players": sorted(list(game.players)),
                        "kills": game.kills,
                        "kills_by_means": game.kills_by_means,
                        "status": game.status,
                        "start_time": game.start_time.strftime("%H:%M") if game.start_time else None,
                        "end_time": game.end_time.strftime("%H:%M") if game.end_time else None
                    }
                    for game_id, game in self.games.items()
                },
                "ranking": self.generate_ranking()
            }

        except Exception as e:
            print(f"Error reading log file: {e}")
            return {}


def main():
    """Main entry point for the parser."""
    parser = QuakeLogParser('qgames.log.txt')
    report = parser.parse_log()
    print("\nFinal Report:")
    print(json.dumps(report, indent=4))


if __name__ == "__main__":
    main() 