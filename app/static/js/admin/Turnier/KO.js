const KO = {
    "render": function () {
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
                return i * 4 + 2
        }
        return undefined;
    },
    "getGameLayer": function (game) {
        return Math.min(KO.getPlayerPoints(game.player1), KO.getPlayerIndex(game.player2));
    },
}