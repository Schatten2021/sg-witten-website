const FFA = {
    "render": function () {
        console.info("rendering FFA tournament");
        for (let i = 0; i < Data.players.length; i++) {
            FFA.reloadPlayerScore(i)
        }
        sortPlayers();
        renderAllPeople()
        gamesDiv.innerHTML = "";
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
        const freispielHeader = tableHead.appendChild(document.createElement("th"));
        freispielHeader.innerText = "Freispiel";
        freispielHeader.className = "ffa-name-header"
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
            const freispiel = row.appendChild(document.createElement("td")).appendChild(document.createElement("input"));
            freispiel.type = "checkbox";
            freispiel.checked = player.freispiel;
            freispiel.addEventListener("change",() => {
                FFA.setFreispiel(i, freispiel);
            })
        }
    },
    "gameResultChange": function(row, col) {
        //                                 .<table>    .<tbody>
        const tableBody = gamesDiv.children[0].children[1];
        //                       .<tr>         .<td>         .<select>
        const element = tableBody.children[row].children[col+1].children[0];
        const counterElement = tableBody.children[col].children[row+1].children[0];
        FFA.setResult(element, element.value, row, col);
        FFA.setResult(counterElement, resultsDataTable[element.value].opposite, col, row);
        sortPlayers();
        renderAllPeople();
        FFA.render() //TODO: add reload button
    },
    "setResult": function(select, result, row, col) {
        const resultData = resultsDataTable[result];
        select.value = result;
        select.className = `ffa-game ${resultData.class}`;
        Data.games.FFA[row][col] = result;
        FFA.reloadPlayerScore(row);
    },
    "setFreispiel": function (index, checkbox) {
        Data.players[index].freispiel = checkbox.checked;
        FFA.reloadPlayerScore(index);
        sortPlayers();
        renderAllPeople();
        FFA.render();
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
        const tableHeaderElem = tableHead.insertBefore(document.createElement("th"), tableHead.children[tableHead.children.length - 1]);
        tableHeaderElem.innerText = getPlayerName(id)
        tableHeaderElem.className = "ffa-name-header"
        const tableBody = table.children[1];
        for (let i = 0; i < tableBody.children.length; i++) {
            const currentRow = tableBody.children[i];
            const dropdown = currentRow.insertBefore(document.createElement("td"), currentRow.children[currentRow.children.length - 1]).appendChild(Blueprints.resultsDropdown.cloneNode(true));
            dropdown.id = null;
            dropdown.className = "ffa-game";
            dropdown.addEventListener("change", () => {
                FFA.gameResultChange(i, index);
            })
            Data.games.FFA[i].push("")
        }
        const gameRow = tableBody.appendChild(document.createElement("tr"));
        const rowHeader = gameRow.appendChild(document.createElement("th"))
        Data.games.FFA.push([])
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
        const freispiel = gameRow.appendChild(document.createElement("td")).appendChild(document.createElement("input"));
        freispiel.type = "checkbox";
        freispiel.checked = false;
        freispiel.addEventListener("change",() => {
            FFA.setFreispiel(index, freispiel);
        })
        Data.games.FFA[index].push("")
    },
    "changePerson": function (index, row) {
        const id = row.children[1].children[0].value
        console.debug(id)
        const name = getPlayerName(id)
        Data.players[index].id = id;
        const table = gamesDiv.children[0]
        table.children[0].children[0].children[index+1].innerText = name
        table.children[1].children[index].children[0].innerText = name
    },
    "reloadPlayerScore": function (index) {
        Data.players[index].points = Data.games.FFA[index]
            .reduce((currentSum, val) => {
                // console.debug(currentSum, resultsDataTable[val].points)
                return currentSum + resultsDataTable[val].points
            }, 0)
        if (Data.players[index].freispiel) {
            Data.players[index].points++;
        }
    },
}