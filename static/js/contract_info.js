const upColor = '#FD1050';
const downColor = '#0CF49B';

function removeBinanceAll() {
    if ($('#binance_contract_info').hasClass('dataTable')) {
        var table = $('#binance_contract_info').dataTable({destroy: true,  "order": [], "columnDefs": [{ "type": "num", "targets": [1]}]});
        table.fnClearTable(); //清空一下table
        table.fnDestroy(); //还原初始化了的datatable
    }
}

function removeGateioAll() {
    if ($('#gateio_contract_info').hasClass('dataTable')) {
        var table = $('#gateio_contract_info').dataTable({destroy: true,  "order": [], "columnDefs": [{ "type": "num", "targets": [1]}]});
        table.fnClearTable(); //清空一下table
        table.fnDestroy(); //还原初始化了的datatable
    }
}

function removeBybitAll() {
    if ($('#bybit_contract_info').hasClass('dataTable')) {
        var table = $('#bybit_contract_info').dataTable({destroy: true,  "order": [], "columnDefs": [{ "type": "num", "targets": [1]}]});
        table.fnClearTable(); //清空一下table
        table.fnDestroy(); //还原初始化了的datatable
    }
}

function removeOkxAll() {
    if ($('#okx_contract_info').hasClass('dataTable')) {
        var table = $('#okx_contract_info').dataTable({destroy: true,  "order": [], "columnDefs": [{ "type": "num", "targets": [1]}]});
        table.fnClearTable(); //清空一下table
        table.fnDestroy(); //还原初始化了的datatable
    }
}

function get_binance_contract_info() {
    removeBinanceAll();
    $.ajax({
        type: "GET",
        url: "/get_binance_contract_info",
        dataType: "json",
        success: function(data) {
            var contract_info_list = data["value"];
            for (var i = 0; i < contract_info_list.length; i++) {
                body = '<tr><td>' + contract_info_list[i][0] + '</td><td>' + contract_info_list[i][1] + '</td><td>' + contract_info_list[i][2] + '</td></tr>';
                $("#binance_contract_info tbody").append(body);
            }
            $('#binance_contract_info').DataTable();
        }
    });
}

function get_gateio_contract_info() {
    removeGateioAll();
    $.ajax({
        type: "GET",
        url: "/get_gateio_contract_info",
        dataType: "json",
        success: function(data) {
            var contract_info_list = data["value"];
            for (var i = 0; i < contract_info_list.length; i++) {
                body = '<tr><td>' + contract_info_list[i][0] + '</td><td>' + contract_info_list[i][1] + '</td><td>' + contract_info_list[i][2] + '</td></tr>';
                $("#gateio_contract_info tbody").append(body);
            }
            $('#gateio_contract_info').DataTable();
        }
    });
}

function get_bybit_contract_info() {
    removeBybitAll();
    $.ajax({
        type: "GET",
        url: "/get_bybit_contract_info",
        dataType: "json",
        success: function(data) {
            var contract_info_list = data["value"];
            for (var i = 0; i < contract_info_list.length; i++) {
                body = '<tr><td>' + contract_info_list[i][0] + '</td><td>' + contract_info_list[i][1] + '</td><td>' + contract_info_list[i][2] + '</td></tr>';
                $("#bybit_contract_info tbody").append(body);
            }
            $('#bybit_contract_info').DataTable();
        }
    });
}

function get_okx_contract_info() {
    removeOkxAll();
    $.ajax({
        type: "GET",
        url: "/get_okx_contract_info",
        dataType: "json",
        success: function(data) {
            var contract_info_list = data["value"];
            for (var i = 0; i < contract_info_list.length; i++) {
                body = '<tr><td>' + contract_info_list[i][0] + '</td><td>' + contract_info_list[i][1] + '</td><td>' + contract_info_list[i][2] + '</td></tr>';
                $("#okx_contract_info tbody").append(body);
            }
            $('#okx_contract_info').DataTable();
        }
    });
}


function init() {
    get_binance_contract_info();
    get_gateio_contract_info();
    get_bybit_contract_info();
    get_okx_contract_info();
}
