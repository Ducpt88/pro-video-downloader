// ============================================================
// Google Apps Script — Pro Video Downloader Visit Counter
// ============================================================
// TRACKING TẬP TRUNG: Tất cả user gửi data lên đây
// Mỗi user thấy TỔNG lượt sử dụng từ TẤT CẢ users
// ============================================================
// HƯỚNG DẪN DEPLOY:
// 1. Tạo Google Sheet mới (đặt tên: "Pro Video Downloader Stats")
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
      // Format header
      sheet.getRange(1, 1, 1, 3).setFontWeight("bold");
    }
    var data = JSON.parse(e.postData.contents);
    var deviceId = data.device_id || "unknown";
    var event = data.event || "open";

    // Ghi nhận lượt sử dụng (mỗi open/download = 1 lượt)
    sheet.appendRow([deviceId, event, new Date()]);

    // Tính tổng TOÀN CẦU (tất cả users)
    var totalVisits = Math.max(0, sheet.getLastRow() - 1);
    var daily = _getDailyBreakdown(sheet);
    var uniqueDevices = _getUniqueDevices(sheet);

    return _resp({
      total_visits: totalVisits,
      unique_devices: uniqueDevices,
      daily: daily
    });
  } catch (err) {
    return _resp({ error: err.toString(), total_visits: 0 });
  }
}

function doGet(e) {
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Visits");
    if (!sheet) return _resp({ total_visits: 0, unique_devices: 0, daily: [] });

    var total = Math.max(0, sheet.getLastRow() - 1);
    var daily = _getDailyBreakdown(sheet);
    var uniqueDevices = _getUniqueDevices(sheet);

    return _resp({
      total_visits: total,
      unique_devices: uniqueDevices,
      daily: daily
    });
  } catch (err) {
    return _resp({ error: err.toString(), total_visits: 0 });
  }
}

// 30 ngày gần nhất — tất cả users gộp lại
function _getDailyBreakdown(sheet) {
  var values = sheet.getDataRange().getValues();
  var now = new Date();
  var days = [];
  for (var d = 29; d >= 0; d--) {
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

// Đếm số thiết bị unique (= số người dùng khác nhau)
function _getUniqueDevices(sheet) {
  var values = sheet.getDataRange().getValues();
  var devices = {};
  for (var i = 1; i < values.length; i++) {
    var did = values[i][0];
    if (did) devices[did] = true;
  }
  return Object.keys(devices).length;
}

function _resp(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
