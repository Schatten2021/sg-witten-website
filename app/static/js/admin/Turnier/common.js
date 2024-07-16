const form = document.getElementById("form");
const contestantsTableBody = document.getElementById("personen-table-body");
const gamesDiv = document.getElementById("games");
const cupTypeInput = document.getElementById("turnier-art-select");
const showDWZInput = document.getElementById("show-DWZ-Input");
const showAgeInput = document.getElementById("show-age-Input");
const newPersonRow = contestantsTableBody.children[0];
const datesInputDiv = document.getElementById("dates")
const Blueprints = {
    "peopleDropdown": document.getElementById("all_people"),
    "teamDropdown": document.getElementById("all_teams"),
    "resultsDropdown": document.getElementById("possible_game_outcomes"),
    "feinwertungenDropdown": document.getElementById("Feinwertungen"),
    "dateInput": document.getElementById("dateInput"),
}
let FeinwertungDropdowns = []
const descriptionInput = document.getElementById("description");
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

    const DWZInput = rowElement
        .appendChild(document.createElement("td"))
        .appendChild(document.createElement("input"));
    DWZInput.type = "number";
    DWZInput.min = 0;
    DWZInput.parentElement.className = "DWZ-input-td"
    DWZInput.addEventListener("change", () => {
        Data.players[index].DWZ = parseInt(DWZInput.value);
    })
    if (!showDWZInput.checked)
        DWZInput.parentElement.style.display = "none";

    const AgeGroupInput = rowElement
        .appendChild(document.createElement("td"))
        .appendChild(document.createElement("input"));
    AgeGroupInput.type = "number";
    AgeGroupInput.min = 0;
    AgeGroupInput.parentElement.className = "age-input-td"
    AgeGroupInput.addEventListener("change", () => {
        Data.players[index].ageGroup = parseInt(AgeGroupInput.value);
    })
    if (!showAgeInput.checked)
        AgeGroupInput.parentElement.style.display = "none";

    for (let i = 0; i < FeinwertungDropdowns.length; i++) {
        rowElement.appendChild(document.createElement("td"));
        switch (cupTypeInput.value) {
            case "jeder gegen jeden":
                FFA.displayFeinwertung(6+i, FeinwertungDropdowns[i]);
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

    Data.players.push({
            "verein": teamDropdown.value,
            "id": personDropdown.value,
            "points": 0,
        })
    switch (cupTypeInput.value) {
        case "jeder gegen jeden":
            FFA.addPerson(index, rowElement);
            break;
        default:
            console.error("Unhandled cup type " + cupTypeInput.value);
            break;
    }
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
        row.children[4].children[0].value = player.DWZ;
        row.children[5].children[0].value = player.ageGroup;
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
                "DWZ": player.DWZ,
                "ageGroup": player.ageGroup,
            }
        }),
        "games": games,
        "feinwertungen": FeinwertungDropdowns.map((elem) => elem.value)
            .filter((val) => ["SB", "Buchholz", "BuchholzBuchholz"].some((elem) => elem === val)),
        "description": descriptionInput.value,
        "dates": Data.dates.filter((elem) => elem.start !== "" && elem.end !== ""),
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

function changeStyleOfClass(className = "", styleName = "display", newValue = "none") {
    const elements = document.getElementsByClassName(className)
    for (let i = 0; i < elements.length; i++) {
        elements[i].style[styleName] = newValue;
    }
}

function copyDropdown({name = "", callback = () => {}, className = "", parent = undefined, next = undefined, createTD = true}) {
    const dropdown = Blueprints[name].cloneNode(true);
    dropdown.id = null;
    dropdown.addEventListener("change", callback)
    dropdown.className = className;
    let elem;
    if (createTD) {
        elem = document.createElement("td");
        elem.appendChild(dropdown);
    } else {
        elem = dropdown;
    }
    if (parent === undefined)
        return elem;
    if (next === undefined) {
        parent.appendChild(elem);
    } else {
        parent.insertBefore(elem, next);
    }
    return elem;
}

function addDateInput(addToData=true) {
    const index = datesInputDiv.children.length;
    if (addToData)
        Data.dates.push({"start": "", "end": ""})
    const elem = datesInputDiv.insertBefore(Blueprints.dateInput.cloneNode(true), datesInputDiv.children[datesInputDiv.children.length-1]);
    elem.id = undefined;
    const label = elem.children[0]
    const deleteButton = label.children[2];
    deleteButton.addEventListener("click", () => {
        Data.dates[index] = {"start": "", "end": ""}
        elem.remove()
    })
    const startInput = label.children[0];
    startInput.addEventListener("change", () => {
        Data.dates[index].start = getDate(startInput).toISOString()
    })
    const endInput = label.children[1];
    endInput.addEventListener("change", () => {
        Data.dates[index].end = getDate(endInput).toISOString()
    })
    return label;
}

function setDate(input, date = new Date().toISOString()) {
    date = new Date(date);
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, "0");
    const day = (date.getDate()).toString().padStart(2, "0");
    const hour = (date.getHours()).toString().padStart(2, "0");
    const minute = (date.getMinutes()).toString().padStart(2, "0");
    const string = `${year}-${month}-${day}T${hour}:${minute}`;
    console.debug("setting ", input, string)
    input.value = string;
}
function getDate(input) {
    return new Date(input.value)
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
    showAgeInput.addEventListener("change", () => {
        if (showAgeInput.checked)
            changeStyleOfClass("age-input-td", "display", "")
        else
            changeStyleOfClass("age-input-td", "display", "none")
    })
    showAgeInput.checked = Data.showAge;
    showDWZInput.addEventListener("change", () => {
        if (showDWZInput.checked)
            changeStyleOfClass("DWZ-input-td", "display", "")
        else
            changeStyleOfClass("DWZ-input-td", "display", "none")
    })
    showDWZInput.checked = Data.showDWZ;
    descriptionInput.addEventListener("input", () => {
        descriptionInput.style.height = "5px"
        descriptionInput.style.height = descriptionInput.scrollHeight + 5 + 'px';
    })
    descriptionInput.dispatchEvent(new Event("input"))
    for (let i = 0; i < Data.dates.length; i++) {
        const date = Data.dates[i];
        const label = addDateInput(false);
        setDate(label.children[0], date.start);
        setDate(label.children[1], date.end)
    }
})()
