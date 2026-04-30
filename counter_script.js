// ============================================================
// Google Apps Script — Pro Video Downloader Visit Counter
// ============================================================
// HƯỚNG DẪN DEPLOY:
// 1. Tạo Google Sheet mới
// 2. Extensions > Apps Script > dán code này
// 3. Deploy > New deployment > Web app
//    - Execute as: Me
//    - Who has access: Anyone
// 4. Copy URL → dán vào COUNTER_API_URL trong app.py
// ============================================================

function doPost(e) {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName("Visits");
    if (!sheet) {
      sheet = ss.insertSheet("Visits");
      sheet.appendRow(["Device ID", "Event", "Timestamp"]);
    }
    var data = JSON.parse(e.postData.contents);
    var deviceId = data.device_id || "unknown";
    var event = data.event || "open";

    // Mỗi lần mở app / tải video = 1 lượt
    sheet.appendRow([deviceId, event, new Date()]);

    var totalVisits = Math.max(0, sheet.getLastRow() - 1);
    var daily = _getDailyBreakdown(sheet);

    return _resp({ total_visits: totalVisits, daily: daily });
  } catch (err) {
    return _resp({ error: err.toString(), total_visits: 0 });
  }
}

function doGet(e) {
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Visits");
    if (!sheet) return _resp({ total_visits: 0, daily: [] });
    var total = Math.max(0, sheet.getLastRow() - 1);
    var daily = _getDailyBreakdown(sheet);
    return _resp({ total_visits: total, daily: daily });
  } catch (err) {
    return _resp({ error: err.toString(), total_visits: 0 });
  }
}

function _getDailyBreakdown(sheet) {
  var values = sheet.getDataRange().getValues();
  var now = new Date();
  var days = [];
  for (var d = 6; d >= 0; d--) {
    var date = new Date(now);
    date.setDate(date.getDate() - d);
    var key = Utilities.formatDate(date, Session.getScriptTimeZone(), "dd/MM");
    var dateStr = Utilities.formatDate(date, Session.getScriptTimeZone(), "yyyy-MM-dd");
    var count = 0;
    for (var i = 1; i < values.length; i++) {
      var ts = values[i][2];
      if (ts instanceof Date) {
        var tsStr = Utilities.formatDate(ts, Session.getScriptTimeZone(), "yyyy-MM-dd");
        if (tsStr === dateStr) count++;
      }
    }
    days.push({ date: key, count: count });
  }
  return days;
}

function _resp(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
