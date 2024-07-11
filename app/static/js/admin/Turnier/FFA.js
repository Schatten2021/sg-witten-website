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
        const id = row.children[1].children[0].value;
        Data.players.push({
            "verein": row.children[2].children[0].value,
            "id": id,
            "points": 0,
        })

        //update table
        const table = gamesDiv.children[0]
        const tableHead = table.children[0].children[0];
        const tableHeaderElem = tableHead.appendChild(document.createElement("th"));
        tableHeaderElem.innerText = getPlayerName(id)
        tableHeaderElem.className = "ffa-name-header"
        const tableBody = table.children[1];
        for (let i = 0; i < tableBody.children.length; i++) {
            const currentRow = tableBody.children[i];
            const dropdown = currentRow.appendChild(document.createElement("td")).appendChild(Blueprints.resultsDropdown.cloneNode(true));
            dropdown.id = null;
            dropdown.className = "ffa-game";
            dropdown.addEventListener("change", () => {
                FFA.gameResultChange(i, index);
            })
            Data.games.FFA[i].push("")
        }
        const gameRow = tableBody.appendChild(document.createElement("tr"));
        Data.games.FFA.push([]);
        const rowHeader = gameRow.appendChild(document.createElement("th"))
        rowHeader.innerText = getPlayerName(id);
        rowHeader.scope = "row";
        for (let i = 0; i < Data.players.length; i++) {
            if (i === index) {
                const elem = gameRow.appendChild(document.createElement("td"));
                elem.innerText = "X";
                elem.className = "ffa-game-self"
                continue;
            }
            const dropdown = gameRow.appendChild(document.createElement("td")).appendChild(Blueprints.resultsDropdown.cloneNode(true));
            dropdown.id = null;
            dropdown.className = "ffa-game";
            dropdown.addEventListener("change", () => {
                FFA.gameResultChange(index, i);
            })
            Data.games.FFA[index].push("")
        }
    },
    "changePerson": function (index, row) {
        Data.players[index].id = row.children[1].value;
        //TODO update table
    },
}