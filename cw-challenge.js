const fs = require('fs');

function parseGame(gameLines) {
    const players = new Set();
    const kills = {};
    const killsByMeans = {};
    let totalKills = 0;

    gameLines.forEach(line => {
        const match = line.match(/Kill: \d+ \d+ \d+: (.+) killed (.+) by (.+)/);
        if (match) {
            const [, killer, victim, means] = match;
            totalKills++;
            
            // Update kills by means
            killsByMeans[means] = (killsByMeans[means] || 0) + 1;
            
            if (victim !== "<world>") {
                players.add(victim);
                if (!(victim in kills)) kills[victim] = 0;
            }
            
            if (killer !== "<world>") {
                players.add(killer);
                kills[killer] = (kills[killer] || 0) + 1;
            } else {
                kills[victim] = (kills[victim] || 0) - 1;
            }
        }
    });

    return {
        total_kills: totalKills,
        players: Array.from(players).sort(),
        kills,
        kills_by_means: killsByMeans
    };
}

function generateRanking(games) {
    const totalKills = {};
    
    // Aggregate kills across all games
    Object.values(games).forEach(game => {
        Object.entries(game.kills).forEach(([player, kills]) => {
            totalKills[player] = (totalKills[player] || 0) + kills;
        });
    });
    
    // Sort players by kills
    const ranking = Object.entries(totalKills)
        .sort(([, a], [, b]) => b - a)
        .map(([player, kills], index) => `${index + 1}. ${player} - ${kills} kills`);
    
    return ranking;
}

async function main() {
    try {
        const logContent = fs.readFileSync('qgames.log.txt', 'utf8');
        const logLines = logContent.split("\n");
        
        const games = {};
        let currentGame = [];
        let gameCount = 0;
        
        // Group lines by game
        logLines.forEach(line => {
            if (line.includes("InitGame:")) {
                if (currentGame.length > 0) {
                    gameCount++;
                    games[`game_${gameCount}`] = parseGame(currentGame);
                }
                currentGame = [line];
            } else if (currentGame.length > 0) {
                currentGame.push(line);
            }
        });
        
        // Don't forget to process the last game
        if (currentGame.length > 0) {
            gameCount++;
            games[`game_${gameCount}`] = parseGame(currentGame);
        }
        
        // Generate final report
        const report = {
            games,
            ranking: generateRanking(games)
        };
        
        console.log(JSON.stringify(report, null, 4));
    } catch (error) {
        console.error("Error reading log file:", error);
    }
}

main();