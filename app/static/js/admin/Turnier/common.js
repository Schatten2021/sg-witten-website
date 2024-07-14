const form = document.getElementById("form");
const contestantsTableBody = document.getElementById("personen-table-body");
const gamesDiv = document.getElementById("games");
const cupTypeInput = document.getElementById("turnier-art-select");
const showDWZInput = document.getElementById("show-DWZ-Input");
const showAgeInput = document.getElementById("show-age-Input");
const newPersonRow = contestantsTableBody.children[0];
const Blueprints = {
    "peopleDropdown": document.getElementById("all_people"),
    "teamDropdown": document.getElementById("all_teams"),
    "resultsDropdown": document.getElementById("possible_game_outcomes"),
    "feinwertungenDropdown": document.getElementById("Feinwertungen"),
}
let FeinwertungDropdowns = []
function addPerson(callback = null) {
    const index = contestantsTableBody.children.length - 1;
    const rowElement = document.createElement("tr");

    const rankDisplay = document.createElement("td");
    rankDisplay.innerText = contestantsTableBody.children.length;
    rowElement.appendChild(rankDisplay)

    const personElement = document.createElement("td");
    const personDropdown = Blueprints.peopleDropdown.cloneNode(true);
    personDropdown.id = null;
    personDropdown.addEventListener("change", () => {
        switch (cupTypeInput.value) {
            case "jeder gegen jeden":
                FFA.changePerson(index, rowElement);
                break;
            default:
                console.error("Unhandled cup type " + cupTypeInput.value);
                break;
        }
    })
    personElement.appendChild(personDropdown);
    rowElement.appendChild(personElement);

    const teamElement = document.createElement("td");
    const teamDropdown = Blueprints.teamDropdown.cloneNode(true);
    teamDropdown.id = null;
    teamElement.appendChild(teamDropdown);
    rowElement.appendChild(teamElement);

    const pointElement = document.createElement("td");
    pointElement.innerText = "0";
    rowElement.appendChild(pointElement);

    for (let i = 0; i < FeinwertungDropdowns.length; i++) {
        rowElement.appendChild(document.createElement("td"));
        switch (cupTypeInput.value) {
            case "jeder gegen jeden":
                FFA.displayFeinwertung(4+i, FeinwertungDropdowns[i]);
                break;
            default:
                throw Error("Invalid cup type " + cupTypeInput.value);
        }
    }

    contestantsTableBody.insertBefore(rowElement, newPersonRow);
    if (callback !== null) {
        callback(index, newPersonRow);
        return;
    }
    switch (cupTypeInput.value) {
        case "jeder gegen jeden":
            FFA.addPerson(index, rowElement);
            break;
        default:
            console.error("Unhandled cup type " + cupTypeInput.value);
            break;
    }
}

function getSelectedPeople() {
    let selectedPeople = [];
    for (let i = 0; i < contestantsTableBody.children.length - 1; i++) {
        const row = contestantsTableBody.children[i];
        const personDropdown = row.children[1];
        selectedPeople.push(personDropdown.value);
    }
    return selectedPeople;
}
function getPlayerName(id) {
    id = parseInt(id)
    return Data.people.find((person) => person.id === id).name;
}

function renderAllPeople() {
    while (contestantsTableBody.children.length > 1) {
        contestantsTableBody.removeChild(contestantsTableBody.children[0]);
    }
    for (let i = 0; i < Data.players.length; i++) {
        const player = Data.players[i];
        addPerson((index, row) => {})
        const row = contestantsTableBody.children[i];
        row.children[1].children[0].value = player.id;
        row.children[2].children[0].value = player.verein;
        row.children[3].innerText = player.points;
    }
}

function sortPlayers() {
    let playerIndices
    switch (cupTypeInput.value) {
        case "jeder gegen jeden":
            playerIndices = Data.players.map((item, index) => index)
                .sort((i, j) => FFA.comparePlayers(i, j));
            break;
        default:
            playerIndices = Data.players.map((item, index) => index)
                .sort((i, j) => Data.players[j].points - Data.players[i].points);
            break;
    }
    const newPlayers = playerIndices.map((i) => Data.players[i]);
    const newFFAGames = playerIndices.map((i) => playerIndices.map((j) => Data.games.FFA[i][j]));
    Data.players = newPlayers;
    Data.games.FFA = newFFAGames;
    renderAllPeople();
}

async function submit(e) {
    e.preventDefault();
    const name = form.elements["name"].value;
    const type = cupTypeInput.value;
    let games = []

    function getFFAGames() {
        for (let i = 0; i < Data.players.length; i++) {
            for (let j = i + 1; j < Data.players.length; j++) {
                const game = Data.games.FFA[i][j];
                if (game === "") {
                    continue
                }
                games.push({
                    "player1": i,
                    "player2": j,
                    "result": game,
                })
            }
        }
    }

    switch (type) {
        case "jeder gegen jeden":
            getFFAGames();
            break;
        default:
            throw Error(`Invalid type ${type}`);
    }
    const data = {
        "name": name,
        "type": type,
        "players": Data.players.map((player) => {
            return {
                "personId": player.id,
                "vereinsId": player.verein,
                "freispiel": player.freispiel,
            }
        }),
        "games": games,
        "feinwertungen": FeinwertungDropdowns.map((elem) => elem.value)
            .filter((val) => ["SB", "Buchholz", "BuchholzBuchholz"].some((elem) => elem === val)),
    }
    const response = await fetch(window.location.href, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data),
    })
    if (response.ok)
        console.debug(await response.json())
}

function FeinwertungSelected(index, select) {
    sortPlayers()
    switch (cupTypeInput.value) {
        case "jeder gegen jeden":
            FFA.displayFeinwertung(index, select);
            break;
        default:
            throw Error("Invalid cup type")
    }
}

function addFeinwertung() {
    const dropdown = Blueprints.feinwertungenDropdown.cloneNode(true);
    dropdown.id = null;
    const contestantsTableHead = contestantsTableBody.parentElement.children[0].children[0];
    const index = contestantsTableHead.children.length;
    dropdown.addEventListener("change", () => {
        FeinwertungSelected(index, dropdown);
        if (index + 1 === contestantsTableHead.children.length)
            addFeinwertung();
    })
    const tableElement = contestantsTableHead.appendChild(document.createElement("th"));
    tableElement.scope = "col";
    tableElement.appendChild(dropdown)
    FeinwertungDropdowns.push(dropdown)
    for (let i = 0; i < contestantsTableBody.children.length; i++) {
        const row = contestantsTableBody.children[i];
        row.appendChild(document.createElement("td"));
    }
    switch (cupTypeInput.value) {
        case "jeder gegen jeden":
            FFA.displayFeinwertung(index, dropdown);
            break;
    }
}

//setup function
(() => {
    sortPlayers()
    form.addEventListener("submit", submit);
    cupTypeInput.addEventListener("change", () => {
        switch (cupTypeInput.value) {
            case "jeder gegen jeden":
                FFA.render();
                break;
            default:
                console.error(`Unhandled cup type ${cupTypeInput.value}`);
                break;
        }
    });

    renderAllPeople();
    cupTypeInput.dispatchEvent(new Event("change"));
    addFeinwertung();
    for (let i = 0; i < Data.feinwertungen.length; i++) {
        const elem = FeinwertungDropdowns[FeinwertungDropdowns.length - 1];
        elem.value = Data.feinwertungen[i];
        elem.dispatchEvent(new Event("change"));
    }
})()
