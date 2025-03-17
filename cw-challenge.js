const fs = require('fs');

function parseGame(gameLines) {
    const players = new Set();
    const kills = {};
    const killsByMeans = {};
    let totalKills = 0;
    let hasShutdown = false;
    let hasKills = false;

    gameLines.forEach(line => {
        if (line.includes("ShutdownGame:")) {
            hasShutdown = true;
        }
        
        const match = line.match(/Kill: \d+ \d+ \d+: (.+) killed (.+) by (.+)/);
        if (match) {
            hasKills = true;
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

    // Determine game status
    let status = "completed";
    if (!hasKills) {
        status = "aborted";
    }

    return {
        total_kills: totalKills,
        players: Array.from(players).sort(),
        kills,
        kills_by_means: killsByMeans,
        status
    };
}

function generateRanking(games) {
    const totalKills = {};
    
    // Aggregate kills across all games
    Object.values(games).forEach(game => {
        // Skip aborted games
        if (game.status === "aborted") return;
        
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
        console.log("Starting to read log file...");
        const logContent = fs.readFileSync('qgames.log.txt', 'utf8');
        console.log("Log file read successfully");
        
        const logLines = logContent.split("\n");
        console.log(`Found ${logLines.length} lines in the log file`);
        
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
        
        console.log(`Processed ${gameCount} games`);
        
        // Generate final report
        const report = {
            games,
            ranking: generateRanking(games)
        };
        
        console.log("\nFinal Report:");
        console.log(JSON.stringify(report, null, 4));
    } catch (error) {
        console.error("Error reading log file:", error);
        console.error("Error details:", error.message);
        console.error("Stack trace:", error.stack);
    }
}

main();