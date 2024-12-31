const DEFAULT_ROW_VALUES = {
    "tag": "----",
    "username": "Unknown",
    "api_key": "Unknown",
    "discord_id": "Unknown",
    "coins": "0",
    "claim_time": "--:--:--",
    "state": "SLEEP"
};

const STATE_COLORS = {
    "SLEEP": "text-violet-500 border-violet-500",
    "HALT": "text-red-500 border-red-500",
    "IDLE": "text-blue-500 border-blue-500",
    "INFO": "text-white border-white-500",
    "WARN": "text-yellow-500 border-yellow-500",
    "ERROR": "text-red-500 border-red-500",
    "GET_COINS": "text-green-500 border-green-500",
    "CLAIM_COINS": "text-green-500 border-green-500",
    "TRANSFER": "text-green-500 border-green-500",
}

// searching
$("#inputSearch").on("input", function() {
    var searchTerm = $(this).val().toLowerCase();

    $("#accountsList .accountContainer").each(function() { 
        var itemText = $(this).text().toLowerCase();
        if (itemText.indexOf(searchTerm) != -1) {
            $(this).prependTo("#accountsList");
        }
    });
});

// sorting
$("#selectSortBy, #selectOrder").on("change", function() {
    sortTable();
});

// select all checkbox
$("#rowHeader input[type='checkbox']").change(function() {
    var isChecked = $(this).prop("checked");
    $("#accountsList .accountContainer .checkbox input[type='checkbox']").prop("checked", isChecked);
    updateStats();
});

// checkbox (update stats)
$("#accountsList").on("change", "input[type='checkbox']", function() {
    updateStats();
});

// clear log
$("#btnClearLog").click(function() {
    $("#logsList").empty();
});

// nav bar
$("#sidebarNav button").click(function() {
    toggleSidebarContent(this)
});

// copy secret
$(document).on("click", ".tag, .username", function() {
    var value;

    const username = $(this).closest(".accountContainer").find(".username").text()
    const apiKeyValue = $(this).closest(".accountContainer").find(".api_key").text()
    const discordIDValue = $(this).closest(".accountContainer").find(".discord_id").text()

    if ($(this).hasClass("tag")) {
        value = apiKeyValue;
    } else if ($(this).hasClass("username")) {
        value = discordIDValue
    }

    const content = `Username: ${username}\nAPI key: ${apiKeyValue}\nDiscord ID: ${discordIDValue}`
    const data = {
        "type": "INFO",
        "content": content  
    }

    appendLog(data);

    navigator.clipboard.writeText(value).catch(function(error) {
        alert("Failed to copy: " + JSON.stringify(error));
    });
});


function updateStats() {
    let totalSelected = 0;
    let totalAccounts = 0;
    let totalCoins = 0;

    $("#accountsList .accountContainer").each(function() {
        totalAccounts++;

        if ($(this).find("input[type='checkbox']").prop("checked")) {
            totalSelected++;
        }

        let coins = $(this).find(".coins").text();
        coins = parseInt(coins);

        totalCoins += coins;
    });

    $("#displayTotalSelectedAccounts").text(totalSelected);
    $("#displayTotalAccounts").text(totalAccounts);
    $("#displayTotalCoins").text(totalCoins);
}

function generateTable(accountList) {
    const tableContainer = $("#accountsList");
    tableContainer.empty();

    accountList.forEach((accountData) => {
        const row = createRow(accountData);
        tableContainer.append(row);
    });
}

function createRow(accountData) {
    const row = $("#rowTemplate").clone();
    row.removeAttr("id");
    row.removeClass("hidden")
    
    Object.keys(accountData).forEach(function(key) {
        const value = accountData[key] || DEFAULT_ROW_VALUES[key];
        const element = row.find(`.${key}`);
        element.text(value);

        if (key == "state") {
            updateStateColor(element, value)
        } 
    })

    return row;
}

function updateRow(accountData) {
    const row = $("#accountsList .accountContainer").filter(function() {
        return $(this).find(".username").text() === accountData.username;
    });

    Object.keys(accountData).forEach(function(key) {
        let value = accountData[key] || DEFAULT_ROW_VALUES[key];

        const element = row.find(`.${key}`);
        if (element.text() !== value) {
            element.text(value);

            if (key == "state") {
                updateStateColor(element, value)
            } 

        }
    });
}

function sortTable() {
    var rows = $("#accountsList .accountContainer").get();
    var sortBy = $("#selectSortBy").val();
    var order = $("#selectOrder").val() === "orderAscending" ? 1 : -1;

    rows.sort(function(a, b) {
        function getValue(element) {
            var text = $(element).find("." + sortBy).text().toLowerCase();
            var number = parseFloat(text);
            return isNaN(number) ? text : number;
        }

        var aValue = getValue(a);
        var bValue = getValue(b);

        return (aValue < bValue ? -1 : aValue > bValue ? 1 : 0) * order;
    });

    $.each(rows, function(index, row) {
        $("#accountsList").append(row);
    });
}

function getSelectedRows() {
    let selectedRows = [];

    $("#accountsList .accountContainer").each(function() {
        if ($(this).find("input[type='checkbox']").prop("checked")) {
            let rowData = {
                tag: $(this).find(".tag").text(),
                username: $(this).find(".username").text(),
                api_key: $(this).find(".api_key").text(),
                discord_id: $(this).find(".discord_id").text(),
                coins: parseInt($(this).find(".coins").text()),
                claim_time: $(this).find(".claim_time").text(),
                state: $(this).find(".state").text()
            };
            selectedRows.push(rowData);
        }
    });

    return selectedRows;
}

function updateStateColor(element, state) {
    $(element)
        .removeClass(function (index, className) {
            return (className.match(/text-\S+/g) || []).join(" ") + " " + (className.match(/border-\S+/g) || []).join(" ");
        })
        .addClass("border-2 " + STATE_COLORS[state])
}

function toggleSidebarContent(button) {
    const buttonToContent = {
        "btnToggleInfo": "contentInfo",
        "btnToggleControls": "contentControls",
        "btnToggleAccounts": "contentAccounts",
        "btnToggleLogs": "contentLogs"
    };

    const buttonId = button.id;
    const contentId = buttonToContent[buttonId];

    $("#content").prepend($(`#${buttonToContent[buttonId]}`))

    $("#" + contentId).toggle();
    $(button).toggleClass("border-l-4");
    $(button).find("iconify-icon").toggleClass("text-yellow-300");
}

function appendLog(data) {
    var newLog = $("#logTemplate").clone();
    newLog.find(".type").text(data.type || "Unknown");
    updateStateColor(newLog.find(".type"), data.type)
    newLog.find(".time").text(data.time || "No time provided");
    newLog.find(".content").text(data.content || "No content provided");
    newLog.removeClass("hidden");

    $("#logsList").append(newLog);
    $("#logsList").scrollTop($("#logsList")[0].scrollHeight);
}