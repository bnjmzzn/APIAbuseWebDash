var socket = io();

socket.on("receive_data", function(data){
    const displayStateElement = $("#displayProgramState")
    displayStateElement.text(data.program_state)
    updateStateColor(displayStateElement, data.program_state)

    $("#displayIpAddress").text(data.ip_address);
    generateTable(data.account_list);
    sortTable();
    updateStats();
});

socket.on("log_update", function(data) {
    appendLog(data);
});

socket.on("update_program_state", function(data){
    const displayStateElement = $("#displayProgramState")
    displayStateElement.text(data.program_state)
    updateStateColor(displayStateElement, data.program_state)
});

socket.on("update_row", function(accountData) {
    updateRow(accountData);
    updateStats()
});

$("#btnPing").click(function() {
    const startTime = Date.now();
    socket.emit("ping");
    
    socket.once("pong", function() {
        const endTime = Date.now();
        const latency = endTime - startTime;
        $("#displayPing").text(latency + "ms");
    });
});

$("#btnGetCoins").click(function() {
    const data = {"accounts_list": getSelectedRows(),}
    socket.emit("get_coins", data);
});

$("#btnClaimCoins").click(function() {
    const data = {"accounts_list": getSelectedRows()}
    socket.emit("claim_coins", data);
});

$("#btnTransferCoins").click(function() {
    const data = {
        "accounts_list": getSelectedRows(),
        "amount": $("#inputAmount").val(),
        "target_id": $("#inputTransferTargetID").val(),
    }
    socket.emit("transfer_coins", data);
});

$("#btnCheckCoins").click(function() {
    const data = {
        "accounts_list": getSelectedRows(),
        "target_id": $("#inputCheckTargetID").val(),
    }
    socket.emit("check_coins", data);
});

$("#btnHalt").click(function() {
    socket.emit("HALT");
});

$("#btnContinue").click(function() {
    socket.emit("CONTINUE");
});

$("#toggleButton").click(function() {
    $("#content").toggle();
});

