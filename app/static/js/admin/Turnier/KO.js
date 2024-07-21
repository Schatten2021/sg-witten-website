const KO = {
    "render": function () {
    },
    "getSortedPeople": function () {
        const games = Data.games.KO;
        //get the victories for each player
        let victories = {}
        for (let i = 0; i < Data.players.length; i++) {
            victories[i] = 0;
        }
        for (let i = 0; i < games.length; i++) {
            const game = games[i];
            if (resultsDataTable[game.result] > 0)
                victories[game.player1] += 1
            else
                victories[game.player2] += 1
        }
        //get the Level of the game
        let gameData = {}
        for (let i = 0; i < games.length; i++) {
            const game = games[i];
            gameData[i] = {
                "level": Math.min(victories[game.player1], victories[game.player2]),
                "index": i
            };
        }
        let levels = []
        const maxLevel = victories.reduce((previousMax, currentValue) => Math.max(previousMax, currentValue), 0)
        for (let i = 0; i < maxLevel.length; i++) {
            levels.push([])
        }
        for (let i = 0; i < gameData.length; i++) {
            levels[gameData.level].push(gameData.index)
        }

        //sort the levels
        let previousLevelPlayers = levels[levels.length - 1].flatMap((gameIndex) => [games[gameIndex].player1, games[gameIndex].player2])
        for (let i = levels.length - 2; i >= 0; i--) {
            //sort the level
            let currentLevel = levels[i];
            // get the resulting indices
            const gameIndices = currentLevel.map((gameIndex) => {
                const game = games[gameIndex];
                const player1Index = previousLevelPlayers.indexOf(game.player1);
                const player2Index = previousLevelPlayers.indexOf(game.player2);
                return player1Index !== -1 ? player1Index : player2Index;
            })
            //sort according to the indices; Indices that weren't found are put to the end of the level
            const gameResultingIndices = gameIndices.map((elem, index) => index).sort((a, b) => {
                const j = gameIndices[a];
                const k = gameIndices[b];
                if (j === -1 || k === -1) {
                    if (j === -1 && k === -1)
                        return 0;
                    if (j === -1)
                        return -1;
                    return 1;
                }
            })
            // finally get the sorted indices back.
            currentLevel = currentLevel.map((value, index) => currentLevel[gameResultingIndices[index]]);
            levels[i] = currentLevel
            //get the next level
            previousLevelPlayers = []
            for (let j = 0; j < currentLevel.length; j++) {
                const game = games[currentLevel[j]];
                previousLevelPlayers.push(game.player1);
                previousLevelPlayers.push(game.player2);
            }
        }
        //TODO: when there are _freispiele_, the games should get pushed up one level.
        return levels.map((level) => level.map((index) => games[index]));
    }
}