const upColor = '#FD1050';
const downColor = '#0CF49B';

function removeBinanceAll() {
    if ($('#binance_kline').hasClass('dataTable')) {
        var table = $('#binance_kline').dataTable({destroy: true,  "order": [], "columnDefs": [{ "type": "num", "targets": [1]}]});
        table.fnClearTable(); //清空一下table
        table.fnDestroy(); //还原初始化了的datatable
    }
}

function removeGateioAll() {
    if ($('#gateio_kline').hasClass('dataTable')) {
        var table = $('#gateio_kline').dataTable({destroy: true,  "order": [], "columnDefs": [{ "type": "num", "targets": [1]}]});
        table.fnClearTable(); //清空一下table
        table.fnDestroy(); //还原初始化了的datatable
    }
}

function removeBybitAll() {
    if ($('#bybit_kline').hasClass('dataTable')) {
        var table = $('#bybit_kline').dataTable({destroy: true,  "order": [], "columnDefs": [{ "type": "num", "targets": [1]}]});
        table.fnClearTable(); //清空一下table
        table.fnDestroy(); //还原初始化了的datatable
    }
}


function displayBinanceKline() {
    removeGateioAll();
    var start_date = $("#bn_kline_start_date").val();
    var end_date = $("#bn_kline_end_date").val();
    var input_data = {start: start_date, end: end_date};
    $.ajax({
        type: "GET",
        url: "/get_binance_kline",
        data: input_data,
        dataType: "json",
        success: function(data) {
            var line_list = data["value"];
            for (var i = 0; i < line_list.length; i++) {
                body = '<tr><td>' + line_list[i][0] + '</td><td>' + line_list[i][1] + '</td><td>' + line_list[i][2] + '</td><td>' + line_list[i][3] + '</td><td>' + line_list[i][4] + '</td><td>' + line_list[i][5] + '</td><td>' + line_list[i][6] + '</td><td>' + line_list[i][7] + '</td><td>' + line_list[i][8] + '</td></tr>';
                $("#binance_kline tbody").append(body);
            }
            $('#binance_kline').DataTable();
        }
    });
}

function displayGateioKline() {
    removeGateioAll();
    var start_date = $("#ga_kline_start_date").val();
    var end_date = $("#ga_kline_end_date").val();
    var input_data = {start: start_date, end: end_date};
    $.ajax({
        type: "GET",
        url: "/get_gateio_kline",
        data: input_data,
        dataType: "json",
        success: function(data) {
            var line_list = data["value"];
            for (var i = 0; i < line_list.length; i++) {
                body = '<tr><td>' + line_list[i][0] + '</td><td>' + line_list[i][1] + '</td><td>' + line_list[i][2] + '</td><td>' + line_list[i][3] + '</td><td>' + line_list[i][4] + '</td><td>' + line_list[i][5] + '</td><td>' + line_list[i][6] + '</td><td>' + line_list[i][7] + '</td><td>' + line_list[i][8] + '</td></tr>';
                $("#gateio_kline tbody").append(body);
            }
            $('#gateio_kline').DataTable();
        }
    });
}

function displayBybitKline() {
    removeBybitAll();
    var start_date = $("#by_kline_start_date").val();
    var end_date = $("#by_kline_end_date").val();
    var input_data = {start: start_date, end: end_date};
    $.ajax({
        type: "GET",
        url: "/get_bybit_kline",
        data: input_data,
        dataType: "json",
        success: function(data) {
            var line_list = data["value"];
            for (var i = 0; i < line_list.length; i++) {
                body = '<tr><td>' + line_list[i][0] + '</td><td>' + line_list[i][1] + '</td><td>' + line_list[i][2] + '</td><td>' + line_list[i][3] + '</td><td>' + line_list[i][4] + '</td><td>' + line_list[i][5] + '</td><td>' + line_list[i][6] + '</td><td>' + line_list[i][7] + '</td><td>' + line_list[i][8] + '</td></tr>';
                $("#bybit_kline tbody").append(body);
            }
            $('#bybit_kline').DataTable();
        }
    });
}


function init() {
    $('#form_bn_kline_start_date').datetimepicker({
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

    $('#form_bn_kline_end_date').datetimepicker({
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

    $('#form_ga_kline_start_date').datetimepicker({
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

    $('#form_ga_kline_end_date').datetimepicker({
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

    $('#form_by_kline_start_date').datetimepicker({
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

    $('#form_by_kline_end_date').datetimepicker({
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
