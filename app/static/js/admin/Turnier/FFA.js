const FFA = {
    "render": function () {
        console.info("rendering FFA tournament")
        sortPlayers()
        const table = gamesDiv.appendChild(document.createElement("table"));
        table.className = "table table-bordered"
        FFA.renderTableHeader(table.appendChild(document.createElement("thead")).appendChild(document.createElement("tr")));
        FFA.renderTableBody(table.appendChild(document.createElement("tbody")));
    },
    "renderTableHeader": function (tableHead) {
        const header = tableHead.appendChild(document.createElement("th"));
        header.innerText = "Name";
        for (let i = 0; i < Data.players.length; i++) {
            const elem = document.createElement("th");
            elem.scope = "col";
            elem.innerText = getPlayerName(Data.players[i].id);
            elem.className = "ffa-name-header";
            tableHead.appendChild(elem);
        }
    },
    "renderTableBody": function (tableBody) {
        for (let i = 0; i < Data.players.length; i++) {
            const player = Data.players[i];
            const row = tableBody.appendChild(document.createElement("tr"));
            const rowHeader = row.appendChild(document.createElement("th"));
            rowHeader.innerText = getPlayerName(player.id);
            for (let j = 0; j < Data.players.length; j++) {
                if (i === j) {
                    const elem = row.appendChild(document.createElement("td"));
                    elem.innerText = "X";
                    elem.className = "ffa-game-self"
                    continue;
                }
                const gameResult = Data.games.FFA[i][j];
                const element = row.appendChild(document.createElement("td"));
                const dropdown = element.appendChild(Blueprints.resultsDropdown.cloneNode(true));
                const resultInfo = resultsDataTable[gameResult];
                dropdown.id = null;
                dropdown.value = gameResult
                dropdown.className = `ffa-game ${resultInfo.class}`
                dropdown.addEventListener("change", () => {
                    FFA.gameResultChange(i, j)
                })
            }
        }
    },
    "gameResultChange": function(row, col) {
        //TODO: implement
    },
    "addPerson": function (index, row) {
        Data.players.push({
            "verein": row.children[2].children[0].value,
            "id": row.children[1].children[0].value,
            "points": 0,
        })
        //TODO: update table
    },
    "changePerson": function (index, row) {
        Data.players[index].id = row.children[1].value;
        //TODO update table
    },
}