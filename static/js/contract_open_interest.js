const upColor = '#FD1050';
const downColor = '#0CF49B';

function removeBinanceAll() {
    if ($('#binance_contract_open_interest').hasClass('dataTable')) {
        var table = $('#binance_contract_open_interest').dataTable({destroy: true,  "order": [], "columnDefs": [{ "type": "num", "targets": [1]}]});
        table.fnClearTable(); //清空一下table
        table.fnDestroy(); //还原初始化了的datatable
    }
}

function removeGateioAll() {
    if ($('#gateio_contract_open_interest').hasClass('dataTable')) {
        var table = $('#gateio_contract_open_interest').dataTable({destroy: true,  "order": [], "columnDefs": [{ "type": "num", "targets": [1]}]});
        table.fnClearTable(); //清空一下table
        table.fnDestroy(); //还原初始化了的datatable
    }
}

function removeBybitAll() {
    if ($('#bybit_contract_open_interest').hasClass('dataTable')) {
        var table = $('#bybit_contract_open_interest').dataTable({destroy: true,  "order": [], "columnDefs": [{ "type": "num", "targets": [1]}]});
        table.fnClearTable(); //清空一下table
        table.fnDestroy(); //还原初始化了的datatable
    }
}


function displayBinanceOpenInterest() {
    removeGateioAll();
    var start_date = $("#bn_oi_start_date").val();
    var end_date = $("#bn_oi_end_date").val();
    var input_data = {start: start_date, end: end_date};
    $.ajax({
        type: "GET",
        url: "/get_binance_contract_open_interest",
        data: input_data,
        dataType: "json",
        success: function(data) {
            var contract_open_interest_list = data["value"];
            for (var i = 0; i < contract_open_interest_list.length; i++) {
                body = '<tr><td>' + contract_open_interest_list[i][0] + '</td><td>' + contract_open_interest_list[i][1] + '</td><td>' + contract_open_interest_list[i][2] + '</td><td>' + contract_open_interest_list[i][3] + '</td><td>' + contract_open_interest_list[i][4] + '</td></tr>';
                $("#binance_contract_open_interest tbody").append(body);
            }
            $('#binance_contract_open_interest').DataTable();
        }
    });
}

function displayGateioOpenInterest() {
    removeGateioAll();
    var start_date = $("#ga_oi_start_date").val();
    var end_date = $("#ga_oi_end_date").val();
    var input_data = {start: start_date, end: end_date};
    $.ajax({
        type: "GET",
        url: "/get_gateio_contract_open_interest",
        data: input_data,
        dataType: "json",
        success: function(data) {
            var contract_open_interest_list = data["value"];
            for (var i = 0; i < contract_open_interest_list.length; i++) {
                body = '<tr><td>' + contract_open_interest_list[i][0] + '</td><td>' + contract_open_interest_list[i][1] + '</td><td>' + contract_open_interest_list[i][2] + '</td><td>' + contract_open_interest_list[i][3] + '</td><td>' + contract_open_interest_list[i][4] + '</td></tr>';
                $("#gateio_contract_open_interest tbody").append(body);
            }
            $('#gateio_contract_open_interest').DataTable();
        }
    });
}

function displayBybitOpenInterest() {
    removeBybitAll();
    var start_date = $("#by_oi_start_date").val();
    var end_date = $("#by_oi_end_date").val();
    var input_data = {start: start_date, end: end_date};
    $.ajax({
        type: "GET",
        url: "/get_bybit_contract_open_interest",
        data: input_data,
        dataType: "json",
        success: function(data) {
            var contract_open_interest_list = data["value"];
            for (var i = 0; i < contract_open_interest_list.length; i++) {
                body = '<tr><td>' + contract_open_interest_list[i][0] + '</td><td>' + contract_open_interest_list[i][1] + '</td><td>' + contract_open_interest_list[i][2] + '</td><td>' + contract_open_interest_list[i][3] + '</td><td>' + contract_open_interest_list[i][4] + '</td></tr>';
                $("#bybit_contract_open_interest tbody").append(body);
            }
            $('#bybit_contract_open_interest').DataTable();
        }
    });
}


function init() {
    $('#form_bn_oi_start_date').datetimepicker({
	    language: 'zh-CN',
        format: "yyyy-mm-dd",
        weekStart: 1,
        todayBtn:  1,
		autoclose: 1,
		todayHighlight: 1,
		startView: 2,
		minView: 2,
		forceParse: 0
    });

    $('#form_bn_oi_end_date').datetimepicker({
	    language: 'zh-CN',
        format: "yyyy-mm-dd",
        weekStart: 1,
        todayBtn:  1,
		autoclose: 1,
		todayHighlight: 1,
		startView: 2,
		minView: 2,
		forceParse: 0
    });

    $('#form_ga_oi_start_date').datetimepicker({
	    language: 'zh-CN',
        format: "yyyy-mm-dd",
        weekStart: 1,
        todayBtn:  1,
		autoclose: 1,
		todayHighlight: 1,
		startView: 2,
		minView: 2,
		forceParse: 0
    });

    $('#form_ga_oi_end_date').datetimepicker({
	    language: 'zh-CN',
        format: "yyyy-mm-dd",
        weekStart: 1,
        todayBtn:  1,
		autoclose: 1,
		todayHighlight: 1,
		startView: 2,
		minView: 2,
		forceParse: 0
    });

    $('#form_by_oi_start_date').datetimepicker({
	    language: 'zh-CN',
        format: "yyyy-mm-dd",
        weekStart: 1,
        todayBtn:  1,
		autoclose: 1,
		todayHighlight: 1,
		startView: 2,
		minView: 2,
		forceParse: 0
    });

    $('#form_by_oi_end_date').datetimepicker({
	    language: 'zh-CN',
        format: "yyyy-mm-dd",
        weekStart: 1,
        todayBtn:  1,
		autoclose: 1,
		todayHighlight: 1,
		startView: 2,
		minView: 2,
		forceParse: 0
    });
}
