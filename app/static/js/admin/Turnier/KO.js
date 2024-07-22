const KO = {
    "render": function () {
        gamesDiv.innerHTML = "";
        sortPlayers();
    },
    "getPlayerPoints": function (playerIndex) {
        const gameVictories = Data.games.KO
            .reduce((previousValue, currentValue) =>
                    previousValue + currentValue
                        .reduce((previousValue, currentValue) => previousValue + KO.getPoints(playerIndex, currentValue), 0)
                , 0)
        const freispiel = Data.players[playerIndex].freispiel ? 1 : 0;
        return gameVictories + freispiel;
    },
    "getPoints": function (playerIndex, game) {
        if (game.player1 === playerIndex)
            return resultsDataTable[game.result].points;
        return resultsDataTable[resultsDataTable[game.result].opposite].points;
    },
    "getPlayerIndex": function (currentPlayerIndex) {
        //first layer
        if (Data.games.KO.length === 0)
            return undefined;
        const games = Data.games.KO[0];
        for (let i = 0; i < games.length; i++) {
            const game = games[i];
            if (game.player1 === currentPlayerIndex)
                return i * 2;
            if (game.player2 === currentPlayerIndex)
                return i * 2 + 1
        }
        const secondLayerGames = Data.games.KO[1];
        for (let i = 0; i < secondLayerGames.length; i++) {
            const game = secondLayerGames[i];
            if (game.player1 === currentPlayerIndex)
                return i * 4;
            if (game.player2 === currentPlayerIndex)
                return i * 4 + 2;
        }
        return undefined;
    },
    "getGameLayer": function (game) {
        return Math.min(KO.getPlayerPoints(game.player1), KO.getPlayerIndex(game.player2));
    },
    "updateGames": function () {
        const allGames = Data.games.KO.flat();
        const gamesLayers = allGames.map((game) => KO.getGameLayer(game));

        //generate layers
        const layerCount = nextPowerOfTwo(allGames.length);
        let layers = [];
        for (let i = 0; i < layerCount; i++) {
            layers.push([])
        }
        for (let i = 0; i < allGames.length; i++) {
            const game = allGames[i];
            const gamesLayer = gamesLayers[i];
            layers[gamesLayer].push(game);
        }
        for (let i = layers.length - 2; i > 0; i--) {
            const layer = layers[i];
            const layerIndices = layer.map((value, index) => index)
            const previousLayer = layers[i+1];
            let previousLayerPlayerIndices = {}
            for (let j = 0; j < previousLayerPlayerIndices.length; j++) {
                const game = previousLayer[j]
                previousLayerPlayerIndices[game.player1] = j * 2;
                previousLayerPlayerIndices[game.player2] = j * 2 + 1;
            }
            const layerTargetIndices = layer.map((game) => {
                if (previousLayerPlayerIndices[game.player1] !== undefined)
                    return previousLayerPlayerIndices[game.player1];
                if (previousLayerPlayerIndices[game.player2] !== undefined)
                    return previousLayerPlayerIndices[game.player2];
                return undefined
            })
            const newLayerIndices = layerIndices.sort((i, j) => {
                const game1Index = layerTargetIndices[i];
                const game2Index = layerTargetIndices[j];
                if (game1Index !== undefined && game2Index !== undefined)
                    return game1Index - game2Index;
                if (game1Index === undefined)
                    return 1;
                if (game2Index === undefined)
                    return -1;
                return 0;
            })
            layers[i] = newLayerIndices.map((j) => layer[j]);
        }
    },
}