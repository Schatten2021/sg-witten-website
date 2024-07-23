const KO = {
    "render": function () {
        gamesDiv.innerHTML = "";
        sortPlayers();
        KO.updateGames();
        const table = gamesDiv.appendChild(document.createElement("table"));
        table.className = "table table-bordered";
        KO.renderTableHeader(table.appendChild(document.createElement("thead")).appendChild(document.createElement("tr")));
        KO.renderTableBody(table.appendChild(document.createElement("tbody")));
    },
    "renderTableHeader": function (tr) {
        const players = KO.getSortedPlayers();
        for (let i = 0; i < players.length; i++) {
            const player = players[i];
            const element = tr.appendChild(document.createElement("th"));
            element.scope = "col";
            element.innerText = player === undefined ? "freispiel" : getPlayerName(player.id);
        }
    },
    "getPlayerNumber": function (gameLayer, gameIndex, player1) {
        let currentGameIndex = gameIndex;
        const games = Data.games.KO;
        let previousLayerGameIndex = player1 ? (gameIndex * 2) : (gameIndex * 2 + 1);
        for (let i = gameLayer - 1; i <= 0; i--) {
            currentGameIndex = previousLayerGameIndex;
            const game = games[i][currentGameIndex];
            if (game === undefined) {
                previousLayerGameIndex = gameIndex * 2; // assume white won, even though there is no information.
                continue
            }
            const result = Data.games.KO[i][currentGameIndex].result;
            const player1Won = resultsDataTable[result].points > 0;
            previousLayerGameIndex = player1Won ? (gameIndex * 2) : (gameIndex * 2 + 1);
        }
    },
    "renderTableBody": function (tbody) {
        const playerCount = KO.totalPlayerCount();
        for (let i = 0; i < Data.games.KO.length; i++) {
            const games = Data.games.KO[i];
            const row = tbody.appendChild(document.createElement("tr"));
            for (let j = 0; j < (playerCount >> i); j++) {
                const game = games[Math.floor(j/2)]
                const player1 = (j & 1) === 0;
                if (game === undefined) {
                    const element = row.appendChild(document.createElement("td"));
                    Data.games.KO[i][Math.floor(j/2)] = 0
                    element.className = `${resultsDataTable[''].class} KO-gameInput`
                    element.dataset.gameResult = "";
                    element.addEventListener("click", () => {
                        KO.changeGameResult(element, i, j)
                    })
                    // 2 ** i
                    element.colSpan = 1 << i;
                    continue
                }
                const strReprOfGame = game === 0 ? "" : game.toString()
                const resultInfo = resultsDataTable[(player1 ? strReprOfGame : resultsDataTable[strReprOfGame].opposite)]
                const element = row.appendChild(document.createElement("td"));
                element.className = `${resultInfo.class} KO-gameInput`
                element.innerText = resultInfo.strRepr;
                element.dataset.gameResult = game;
                element.addEventListener("click", () => {
                    KO.changeGameResult()
                })
                // const dropdown = element.children[0];
                // dropdown.value = (player1 ? game.result : resultInfo.opposite)
                console.debug(element)
                // 2 ** i
                element.colSpan = 1 << i;
            }
        }
    },
    "changeGameResult": function (element, i, j) {
        const gameIndex = Math.floor(j / 2);
        const player1 = (j & 1) === 0;
        if (Data.games.KO[i][gameIndex] === undefined) {
            Data.games.KO[i][gameIndex] = 0
        }
        const otherElement = element.parentNode.children[j + (player1 ? 1 : -1)];
        if (element.innerText !== "1") {
            KO.setResult(element, "1");
            KO.setResult(otherElement, "-1");
        } else {
            KO.setResult(element, "2");
            KO.setResult(otherElement, "-2");
        }
        Data.games.KO[i][gameIndex] = (player1 ? 1 : -1) * parseInt(element.dataset.gameResult);
    },
    "setResult": function (element, result) {
        const resultData = resultsDataTable[result];
        element.dataset.gameResult = result;
        element.className = `${resultData.class} KO-gameInput`
        element.innerText = resultData.strRepr;
    },
    "getPlayerPoints": function (playerIndex) {
        //TODO: This got a lot more complicated
    },
    "totalPlayerCount": function () {
        const freispielCount = Data.players.reduce((previousValue, currentValue) => previousValue + (currentValue.freispiel ? 1 : 0), 0);
        const result = nextPowerOfTwo(Data.players.length + freispielCount);
        return result === 1 ? 2 : result;
    },
    "getSortedPlayers": function () {
        let playerIndices = Data.players.map((value, index) => KO.getPlayerIndex(index));
        let sortedPlayers = [];
        const totalElementsInSortedPlayers = KO.totalPlayerCount()
        for (let i = 0; i < totalElementsInSortedPlayers; i++)
            sortedPlayers.push(undefined)
        let playersWithoutIndex = []
        for (let i = 0; i < playerIndices.length; i++) {
            const player = Data.players[i];
            const index = playerIndices[i];
            if (index === undefined)
                playersWithoutIndex.push(player)
            else
                sortedPlayers[index] = player;
        }
        let missingPlayerIndex = 0;
        for (let i = 0; i < sortedPlayers.length; i++) {
            if (sortedPlayers[i] !== undefined)
                continue
            const player = playersWithoutIndex[missingPlayerIndex];
            if (player === undefined)
                continue
            missingPlayerIndex++;
            sortedPlayers[i] = player;
            if (player.freispiel) {
                i++;
            }
        }
        return sortedPlayers
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
        if (Data.games.KO.length === 1)
            return undefined
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
    "getLayerCount": function () {
        const playerCount = KO.totalPlayerCount();
        let count = 0;
        while ((1 << count) < playerCount)
            count++;
        return count;
    },
    "updateGames": function () {
        const allGames = Data.games.KO.flat();
        const gamesLayers = allGames.map((game) => KO.getGameLayer(game));

        //generate layers
        let layers = [];
        for (let i = 0; i < KO.getLayerCount(); i++) {
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
        Data.games.KO = layers
    },
    "addPerson": function (index, rowElement) {
        KO.render()
    },
}