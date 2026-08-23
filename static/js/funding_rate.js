
function removeBnFrAll() {
    if ($('#bn_funding_rate').hasClass('dataTable')) {
        var table = $('#bn_funding_rate').dataTable({destroy: true,  "order": [], "columnDefs": [{ "type": "num", "targets": [1]}]});
        table.fnClearTable(); //清空一下table
        table.fnDestroy(); //还原初始化了的datatable
    }
}

function removeGaFrAll() {
    if ($('#ga_funding_rate').hasClass('dataTable')) {
        var table = $('#ga_funding_rate').dataTable({destroy: true,  "order": [], "columnDefs": [{ "type": "num", "targets": [1]}]});
        table.fnClearTable(); //清空一下table
        table.fnDestroy(); //还原初始化了的datatable
    }
}

function removeByFrAll() {
    if ($('#by_funding_rate').hasClass('dataTable')) {
        var table = $('#by_funding_rate').dataTable({destroy: true,  "order": [], "columnDefs": [{ "type": "num", "targets": [1]}]});
        table.fnClearTable(); //清空一下table
        table.fnDestroy(); //还原初始化了的datatable
    }
}

function removeOkFrAll() {
    if ($('#ok_funding_rate').hasClass('dataTable')) {
        var table = $('#ok_funding_rate').dataTable({destroy: true,  "order": [], "columnDefs": [{ "type": "num", "targets": [1]}]});
        table.fnClearTable(); //清空一下table
        table.fnDestroy(); //还原初始化了的datatable
    }
}

function displayBinanceFundingRate() {
    removeBnFrAll();
    var start_date = $("#bn_fr_start_date").val();
    var end_date = $("#bn_fr_end_date").val();
    var input_data = {start: start_date, end: end_date};
    $.ajax({
        type: "GET",
        url: "/get_binance_funding_rate",
        data: input_data,
        dataType: "json",
        success: function(data) {        
            var funding_rate_list = data["value"];
            for (var i = 0; i < funding_rate_list.length; i++) {
                body = '<tr><td>' + funding_rate_list[i][0] + '</td><td>' + funding_rate_list[i][1] + '</td><td>' + funding_rate_list[i][2] + '</td><td>' + funding_rate_list[i][3] + '</td></tr>';
                $("#bn_funding_rate tbody").append(body);
            }
            $('#bn_funding_rate').DataTable();
        }
    });
}

function displayGateioFundingRate() {
    removeGaFrAll();
    var start_date = $("#ga_fr_start_date").val();
    var end_date = $("#ga_fr_end_date").val();
    var input_data = {start: start_date, end: end_date};
    $.ajax({
        type: "GET",
        url: "/get_gateio_funding_rate",
        data: input_data,
        dataType: "json",
        success: function(data) {        
            var funding_rate_list = data["value"];
            for (var i = 0; i < funding_rate_list.length; i++) {
                body = '<tr><td>' + funding_rate_list[i][0] + '</td><td>' + funding_rate_list[i][1] + '</td><td>' + funding_rate_list[i][2] + '</td><td>' + funding_rate_list[i][3] + '</td></tr>';
                $("#ga_funding_rate tbody").append(body);
            }
            $('#ga_funding_rate').DataTable();
        }
    });
}

function displayBybitFundingRate() {
    removeByFrAll();
    var start_date = $("#by_fr_start_date").val();
    var end_date = $("#by_fr_end_date").val();
    var input_data = {start: start_date, end: end_date};
    $.ajax({
        type: "GET",
        url: "/get_bybit_funding_rate",
        data: input_data,
        dataType: "json",
        success: function(data) {        
            var funding_rate_list = data["value"];
            for (var i = 0; i < funding_rate_list.length; i++) {
                body = '<tr><td>' + funding_rate_list[i][0] + '</td><td>' + funding_rate_list[i][1] + '</td><td>' + funding_rate_list[i][2] + '</td><td>' + funding_rate_list[i][3] + '</td></tr>';
                $("#by_funding_rate tbody").append(body);
            }
            $('#by_funding_rate').DataTable();
        }
    });
}

function displayOkxFundingRate() {
    removeOkFrAll();
    var start_date = $("#ok_fr_start_date").val();
    var end_date = $("#ok_fr_end_date").val();
    var input_data = {start: start_date, end: end_date};
    $.ajax({
        type: "GET",
        url: "/get_okx_funding_rate",
        data: input_data,
        dataType: "json",
        success: function(data) {        
            var funding_rate_list = data["value"];
            for (var i = 0; i < funding_rate_list.length; i++) {
                body = '<tr><td>' + funding_rate_list[i][0] + '</td><td>' + funding_rate_list[i][1] + '</td><td>' + funding_rate_list[i][2] + '</td><td>' + funding_rate_list[i][3] + '</td></tr>';
                $("#ok_funding_rate tbody").append(body);
            }
            $('#ok_funding_rate').DataTable();
        }
    });
}

function init() {
    $('#form_bn_fr_start_date').datetimepicker({
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

    $('#form_bn_fr_end_date').datetimepicker({
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

    $('#form_ga_fr_start_date').datetimepicker({
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

    $('#form_ga_fr_end_date').datetimepicker({
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

    $('#form_by_fr_start_date').datetimepicker({
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

    $('#form_by_fr_end_date').datetimepicker({
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

    $('#form_ok_fr_start_date').datetimepicker({
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

    $('#form_ok_fr_end_date').datetimepicker({
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


