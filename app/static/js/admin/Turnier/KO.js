const KO = {
    "render": function () {
        gamesDiv.innerHTML = "";
        KO.updatePlayers();
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
            element.className = "KO-player-header"
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
        const playerCount = nextPowerOfTwo(Data.players.length);
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
                element.innerText = resultInfo.strRepr === "" ? "/" : resultInfo.strRepr;
                element.dataset.gameResult = game;
                element.addEventListener("click", () => {
                    KO.changeGameResult(element, i, j)
                })
                // 2 ** i
                element.colSpan = 1 << i;
            }
        }
    },
    // visible functionality (events, etc.)
    "changeGameResult": function (element, i, j) {
        const gameIndex = j >> 1;
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
        KO.updatePlayers();
    },
    "setResult": function (element, result) {
        const resultData = resultsDataTable[result];
        element.dataset.gameResult = result;
        element.className = `${resultData.class} KO-gameInput`
        element.innerText = resultData.strRepr;
    },
    //other
    "getPlayerPoints": function (playerIndex) {
        let previousIndex = playerIndex;
        for (let i = 0; i < Data.games.KO.length; i++) {
            const gameIndex = Math.floor(previousIndex / 2);
            const player1 = (previousIndex & 1) === 0;
            const game = Data.games.KO[i][gameIndex];
            const result = game !== undefined ? (player1 ? game : -game) : -1;
            if (result <= 0)
                return i;
            previousIndex = gameIndex;
        }
        return Data.games.KO.length;
    },
    "updatePlayers": function () {
        for (let i = 0; i < Data.players.length; i++) {
            Data.players[i].points = KO.getPlayerPoints(i);
        }
        sortPlayers();
        renderAllPeople();
    },
    "getSortedPlayers": function () {
        const totalPlayerCount = nextPowerOfTwo(Data.players.length);
        let players = []
        const currentPlayers = Data.players;
        let playerIndex = 0;
        for (let i = 0; i < totalPlayerCount; i++) {
            const playersToFill = totalPlayerCount - i;
            const remainingPlayers = currentPlayers.length - playerIndex;
            players[i] = currentPlayers[playerIndex];
            if (playersToFill === 2 * remainingPlayers) {
                players[i+1] = undefined;
                i++;
            }
            playerIndex++;
        }
        return players
    },
    "getLayerCount": function () {
        const playerCount = nextPowerOfTwo(Data.players.length);
        let count = 0;
        while ((1 << count) < playerCount)
            count++;
        return count;
    },
    "updateGames": function () {
        //generate layers
        const layerCount = KO.getLayerCount();
        for (let i = Data.games.KO.length; i < layerCount; i++) {
            Data.games.KO.push([])
        }
        for (let i = 0; i < layerCount; i++) {
            const gameCount = 1 << (layerCount - i - 1);
            for (let j = Data.games.KO[i].length; j < gameCount; j++) {
                Data.games.KO[i].push(0)
            }
        }
    },
    "addPerson": function (index, rowElement) {
        KO.render()
    },
    "changePerson": function (index, rowElement) {
        KO.render();
    }
}