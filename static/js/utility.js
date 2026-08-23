function RefreshTable(tableId, json) {
	table = $(tableId).dataTable();
	oSettings = table.fnSettings();
	table.fnClearTable(this); //动态刷新关键部分语句，只会根据后台数据有变化才会刷新
	for (var i = 0; i < json.length; i++)
	{
		table.oApi._fnAddData(oSettings, json[i]); //注意取得的jason串的字符数量，要与html中列的数量要有对应
	}
	oSettings.aiDisplay = oSettings.aiDisplayMaster.slice();
	table.fnDraw();
}