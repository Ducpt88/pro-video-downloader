// ============================================================
// Google Apps Script — Nhận Webhook từ Casso.vn
// Tự động thêm tên người chuyển khoản vào Google Sheet
// ============================================================
// HƯỚNG DẪN:
// 1. Mở Google Sheet (cái đã tạo) → Extensions → Apps Script
// 2. Dán toàn bộ code này vào
// 3. Deploy → New deployment → Web app
//    - Execute as: Me
//    - Who has access: Anyone
// 4. Copy URL → dán vào Casso.vn webhook
//
// SETUP CASSO (miễn phí):
// 1. Đăng ký tại https://my.casso.vn
// 2. Liên kết tài khoản ngân hàng (cái nhận tiền cafe)
// 3. Vào Cài đặt → Webhook → dán URL Google Apps Script
// 4. Xong! Mỗi khi có người chuyển khoản → tên tự động hiển thị trên app
// ============================================================

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    
    // Casso gửi danh sách giao dịch trong data.data
    var transactions = data.data || [];
    
    for (var i = 0; i < transactions.length; i++) {
      var tx = transactions[i];
      // Chỉ lấy giao dịch nhận tiền (amount > 0)
      var amount = tx.amount || 0;
      if (amount > 0) {
        // Lấy tên người chuyển từ mô tả giao dịch
        var description = tx.description || "";
        var counterName = _extractName(description);
        
        if (counterName) {
          // Kiểm tra trùng tên
          var existing = sheet.getRange("A:A").getValues().flat();
          var isDuplicate = existing.some(function(name) {
            return name && name.toString().toLowerCase() === counterName.toLowerCase();
          });
          
          if (!isDuplicate) {
            // Thêm tên mới vào sheet
            var lastRow = sheet.getLastRow();
            sheet.getRange(lastRow + 1, 1).setValue(counterName);
          }
        }
      }
    }
    
    return ContentService.createTextOutput(JSON.stringify({success: true}))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({error: err.toString()}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function _extractName(description) {
  // Casso description thường có dạng: "TEN NGUOI CHUYEN noi dung"
  // Hoặc: "NGUYEN VAN A chuyen tien"
  if (!description) return null;
  
  // Lấy phần tên từ đầu mô tả (trước các keyword)
  var keywords = ["chuyen tien", "moi cafe", "ung ho", "donate", "gui", "chuyen khoan", "ct tu"];
  var desc = description.trim();
  
  // Thử tách tên từ mô tả
  // Pattern phổ biến: "CT tu [TEN] toi [SDT/STK]"
  var ctMatch = desc.match(/CT tu (.+?) toi/i);
  if (ctMatch) return _cleanName(ctMatch[1]);
  
  // Pattern: "GD tu [TEN]"
  var gdMatch = desc.match(/GD tu (.+?)(?:\s+\d|$)/i);
  if (gdMatch) return _cleanName(gdMatch[1]);
  
  // Fallback: lấy phần đầu trước keyword
  var lower = desc.toLowerCase();
  for (var i = 0; i < keywords.length; i++) {
    var idx = lower.indexOf(keywords[i]);
    if (idx > 0) {
      return _cleanName(desc.substring(0, idx));
    }
  }
  
  // Nếu mô tả ngắn (<30 chars), dùng luôn
  if (desc.length > 0 && desc.length < 30) {
    return _cleanName(desc);
  }
  
  return null;
}

function _cleanName(name) {
  if (!name) return null;
  name = name.replace(/[^a-zA-ZÀ-ỹ\s]/g, "").trim();
  // Capitalize
  if (name.length < 2) return null;
  return name.split(" ").map(function(w) {
    return w.charAt(0).toUpperCase() + w.slice(1).toLowerCase();
  }).join(" ");
}

function doGet(e) {
  return ContentService.createTextOutput("Webhook is active!")
    .setMimeType(ContentService.MimeType.TEXT);
}
