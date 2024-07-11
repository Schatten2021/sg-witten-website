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
}
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
    return Data.people.find((person) => person.id === id).name;
}

function renderAllPeople() {
    while (contestantsTableBody.children.length > 1) {
        contestantsTableBody.removeChild(contestantsTableBody.children[0]);
    }
    for (let i = 0; i < Data.players.length; i++) {
        const player = Data.players[i];
        console.debug("adding player", player)
        addPerson((index, row) => {})
        const row = contestantsTableBody.children[i];
        row.children[1].children[0].value = player.id;
        row.children[2].children[0].value = player.verein;
        row.children[3].innerText = player.points;
    }
}

function sortPlayers() {
    const playerIndices = Data.players.map((item, index) => index)
        .sort((i, j) => Data.players[j].points - Data.players[i].points);
    const newPlayers = playerIndices.map((i) => Data.players[i]);
    const newFFAGames = playerIndices.map((i) => playerIndices.map((j) => Data.games.FFA[i][j]));
    Data.players = newPlayers;
    Data.games.FFA = newFFAGames;
}

function submit() {
    //TODO: gather data and submit it.
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
})()
