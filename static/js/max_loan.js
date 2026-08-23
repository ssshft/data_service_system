const upColor = '#FD1050';
const downColor = '#0CF49B';

function removeGateioAll() {
    if ($('#gateio_account_max_loan').hasClass('dataTable')) {
        var table = $('#gateio_account_max_loan').dataTable({destroy: true,  "order": [], "columnDefs": [{ "type": "num", "targets": [1]}]});
        table.fnClearTable(); //清空一下table
        table.fnDestroy(); //还原初始化了的datatable
    }
}

function removeOkxAll() {
    if ($('#okx_account_max_loan').hasClass('dataTable')) {
        var table = $('#okx_account_max_loan').dataTable({destroy: true,  "order": [], "columnDefs": [{ "type": "num", "targets": [1]}]});
        table.fnClearTable(); //清空一下table
        table.fnDestroy(); //还原初始化了的datatable
    }
}

function get_gateio_market_max_loan() {
    $.ajax({
        type: "GET",
        url: "/get_gateio_market_max_loan",
        dataType: "json",
        success: function(data) {
            var market_max_loan_list = data["value"];
            for (var i = 0; i < market_max_loan_list.length; i++) {
                body = '<tr><td>' + market_max_loan_list[i][0] + '</td><td>' + market_max_loan_list[i][1] + '</td><td>' + market_max_loan_list[i][2] + '</td><td>' + market_max_loan_list[i][3] + '</td><td>' + market_max_loan_list[i][4] + '</td><td>' + market_max_loan_list[i][5] + '</td><td>' + market_max_loan_list[i][6] + '</td><td>' + market_max_loan_list[i][7] + '</td><td>' + market_max_loan_list[i][8] + '</td><td>' + market_max_loan_list[i][10] + '</td></tr>';
                $("#gateio_market_max_loan tbody").append(body);
            }
            $('#gateio_market_max_loan').DataTable();
        }
    });
}

function displayGateioAccount() {
    removeGateioAll();
    var x = document.getElementById("gateio_account_name");
    var index = x.selectedIndex;
    var account_name = x.options[index].value;
    var input_data = {account: account_name};
    $.ajax({
        type: "GET",
        url: "/get_gateio_max_loan",
        data: input_data,
        dataType: "json",
        success: function(data) {
            var max_loan_list = data["value"];
            for (var i = 0; i < max_loan_list.length; i++) {
                body = '<tr><td>' + max_loan_list[i][1] + '</td><td>' + max_loan_list[i][2] + '</td><td>' + max_loan_list[i][3] + '</td><td>' + max_loan_list[i][4] + '</td></tr>';
                $("#gateio_account_max_loan tbody").append(body);
            }
            $('#gateio_account_max_loan').DataTable();
        }
    });
}

function displayOkxAccount() {
    removeOkxAll();
    var x = document.getElementById("okx_account_name");
    var index = x.selectedIndex;
    var account_name = x.options[index].value;
    var input_data = {account: account_name};
    $.ajax({
        type: "GET",
        url: "/get_okx_max_loan",
        data: input_data,
        dataType: "json",
        success: function(data) {
            var max_loan_list = data["value"];
            for (var i = 0; i < max_loan_list.length; i++) {
                body = '<tr><td>' + max_loan_list[i][1] + '</td><td>' + max_loan_list[i][2] + '</td><td>' + max_loan_list[i][3]  + '</td><td>' + max_loan_list[i][4] + '</td><td>' + max_loan_list[i][5] + '</td><td>' + max_loan_list[i][6] + '</td><td>' + max_loan_list[i][7] + '</td><td>' + max_loan_list[i][8]+ '</td></tr>';
                $("#okx_account_max_loan tbody").append(body);
            }
            $('#okx_account_max_loan').DataTable();
        }
    });
}

function init() {
    get_gateio_market_max_loan();
}
