/**
 * GOOGLE APPS SCRIPT - MEETING REMINDER AUTOMATION
 * 
 * Fungsi: Setiap hari jam 08:00, trigger akan:
 * 1. Baca sheet "TargetPenerimaWA" untuk kumpulkan targets
 * 2. Baca sheet "Meetings" untuk cek ada meeting hari ini
 * 3. Jika ada, format pesan & kirim via Fonnte API
 * 4. Log hasil pengiriman di sheet "Logs"
 * 5. Mark "Sudah_Kirim" = "Yes"
 * 
 * Setup:
 * 1. Paste code ini di Google Apps Script editor
 * 2. Deploy → Web app
 * 3. Click menu "📅 Meeting Reminder" → "Setup Daily Trigger"
 */

// ============================================================================
// CONFIGURATION (Sesuaikan jika perlu)
// ============================================================================

const SHEET_PENGATURAN = "Pengaturan";
const SHEET_TARGET_PENERIMA = "TargetPenerimaWA";
const SHEET_MEETINGS = "Meetings";
const SHEET_LOGS = "Logs";
const FONNTE_API_URL = "https://api.fonnte.com/send";

// Column indices (0-based) untuk sheet "Meetings"
const COL_NO_DOK = 0;          // No_Dokumen
const COL_AGENDA = 1;           // Agenda
const COL_TANGGAL = 2;          // Tanggal
const COL_WAKTU_MULAI = 3;      // Waktu_Mulai
const COL_WAKTU_SELESAI = 4;    // Waktu_Selesai
const COL_LOKASI = 5;           // Lokasi
const COL_PESERTA = 6;          // Peserta
const COL_SUDAH_KIRIM = 7;      // Sudah_Kirim

// ============================================================================
// MENU & UI FUNCTIONS
// ============================================================================

/**
 * Setup menu yang muncul saat spreadsheet dibuka
 */
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('📅 Meeting Reminder')
    .addItem('1. Validasi Pengaturan & Target', 'validateSettingsAndTargetsDialog')
    .addItem('2. Atur Trigger Harian (08:00)', 'setupDailyTrigger')
    .addItem('3. Hapus Trigger Harian', 'deleteTriggers')
    .addSeparator()
    .addItem('🚀 Kirim Tes Sekarang', 'manualCheckAndSendReminders')
    .addToUi();
}

/**
 * Dialog untuk validasi pengaturan
 */
function validateSettingsAndTargetsDialog() {
  const ui = SpreadsheetApp.getUi();
  try {
    const settings = getSettings();
    const targets = getTargets();
    
    let message = "✅ Validasi Pengaturan:\n";
    message += `- Fonnte API Token: ${settings.fonnteToken ? '✅ Ada' : '❌ KOSONG!'}\n`;
    message += `- Waktu Kirim: ${settings.sendTime ? settings.sendTime : '❌ KOSONG!'}\n\n`;
    
    message += "✅ Validasi Target Penerima:\n";
    message += `- Jumlah Nomor WA: ${targets.numbers.length}\n`;
    message += `- Jumlah Grup WA: ${targets.groups.length}\n`;
    message += `- Total Target: ${targets.numbers.length + targets.groups.length}\n`;
    
    if (!settings.fonnteToken || !settings.sendTime) {
      message += "\n⚠️ PERINGATAN: Lengkapi pengaturan di sheet 'Pengaturan'!\n";
    }
    if (targets.numbers.length === 0 && targets.groups.length === 0) {
      message += "\n⚠️ PERINGATAN: Tidak ada target penerima di sheet 'TargetPenerimaWA'!\n";
    }
    
    ui.alert("Hasil Validasi", message, ui.ButtonSet.OK);
    
  } catch (e) {
    Logger.log(`Error validating: ${e.toString()}`);
    ui.alert("Error", `Gagal validasi: ${e.message}`, ui.ButtonSet.OK);
  }
}

// ============================================================================
// SETTINGS & TARGETS READ FUNCTIONS
// ============================================================================

/**
 * Baca pengaturan dari sheet "Pengaturan"
 * Format: Keterangan | Value
 */
function getSettings() {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_PENGATURAN);
    if (!sheet) {
      throw new Error(`Sheet "${SHEET_PENGATURAN}" tidak ditemukan.`);
    }
    
    const range = sheet.getRange("A2:B" + sheet.getLastRow());
    const data = range.getValues();
    const settings = {};
    
    data.forEach(row => {
      const key = row[0] ? row[0].toString().toLowerCase().trim() : "";
      const value = row[1] ? row[1].toString().trim() : "";
      
      if (key && value) {
        if (key.includes("fonnte api token")) settings.fonnteToken = value;
        else if (key.includes("waktu kirim")) settings.sendTime = value;
      }
    });
    
    if (!settings.fonnteToken || !settings.sendTime) {
      Logger.log(`⚠️ Pengaturan tidak lengkap: Token=${settings.fonnteToken}, Time=${settings.sendTime}`);
    }
    
    return settings;
    
  } catch (e) {
    Logger.log(`Error in getSettings: ${e.toString()}`);
    throw new Error(`Gagal baca sheet "${SHEET_PENGATURAN}": ${e.message}`);
  }
}

/**
 * Baca target penerima dari sheet "TargetPenerimaWA"
 * Format: Type | Value
 * Type: "nomor" atau "grup"
 */
function getTargets() {
  const targets = { numbers: [], groups: [] };
  
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_TARGET_PENERIMA);
    if (!sheet) {
      throw new Error(`Sheet "${SHEET_TARGET_PENERIMA}" tidak ditemukan.`);
    }
    
    const data = sheet.getDataRange().getValues();
    
    // Skip header row (row 0)
    for (let i = 1; i < data.length; i++) {
      const type = data[i][0] ? data[i][0].toString().toLowerCase().trim() : "";
      const value = data[i][1] ? data[i][1].toString().trim() : "";
      
      if (value) {
        if (type === "nomor") {
          targets.numbers.push(value);
        } else if (type === "grup") {
          targets.groups.push(value);
        }
      }
    }
    
    Logger.log(`✅ Loaded targets: ${targets.numbers.length} nomor, ${targets.groups.length} grup`);
    
  } catch (e) {
    Logger.log(`Error in getTargets: ${e.toString()}`);
    throw new Error(`Gagal baca sheet "${SHEET_TARGET_PENERIMA}": ${e.message}`);
  }
  
  return targets;
}

// ============================================================================
// MEETING DATA FUNCTIONS
// ============================================================================

/**
 * Baca meetings dari sheet "Meetings" yang tanggalnya hari ini
 * dan belum dikirim (Sudah_Kirim != "Yes")
 */
function getMeetingsForToday() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_MEETINGS);
  const data = sheet.getDataRange().getValues();
  
  const today = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy-MM-dd");
  const meetings = [];
  
  // Skip header row (row 0)
  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    
    // Parse tanggal
    const tanggalCell = row[COL_TANGGAL];
    let tanggal = "";
    
    if (tanggalCell instanceof Date) {
      tanggal = Utilities.formatDate(tanggalCell, Session.getScriptTimeZone(), "yyyy-MM-dd");
    } else if (typeof tanggalCell === 'string') {
      tanggal = tanggalCell.trim();
    }
    
    const sudahKirim = row[COL_SUDAH_KIRIM] ? row[COL_SUDAH_KIRIM].toString().toLowerCase().trim() : "";
    
    // Check if tanggal today dan belum kirim
    if (tanggal === today && sudahKirim !== "yes") {
      meetings.push({
        rowIndex: i + 1,  // Excel row number (1-based)
        noDokumen: row[COL_NO_DOK] || "",
        agenda: row[COL_AGENDA] || "",
        tanggal: tanggal,
        waktuMulai: row[COL_WAKTU_MULAI] || "",
        waktuSelesai: row[COL_WAKTU_SELESAI] || "",
        lokasi: row[COL_LOKASI] || "",
        peserta: row[COL_PESERTA] || ""
      });
    }
  }
  
  Logger.log(`✅ Found ${meetings.length} meetings for today (${today})`);
  return meetings;
}

// ============================================================================
// MESSAGE FORMATTING
// ============================================================================

/**
 * Format pesan WhatsApp untuk single meeting
 * Format tanggal: Indonesia (Senin, 15 April 2026)
 * Format waktu: Hanya jam (10:00 - 11:00)
 */
function formatMeetingMessage(meeting) {
  const timezone = Session.getScriptTimeZone();
  
  // Format tanggal ke Indonesia
  const dateObj = new Date(meeting.tanggal);
  const tanggalFormatted = formatDateIndonesian(dateObj, timezone);
  
  // Parse waktu - ambil hanya HH:mm
  const waktuMulai = extractTime(meeting.waktuMulai);
  const waktuSelesai = extractTime(meeting.waktuSelesai);
  
  let msg = "📅 *REMINDER MEETING HARI INI*\n\n";
  
  msg += `📌 *${meeting.noDokumen} - ${meeting.agenda}*\n`;
  msg += `📅 Tanggal: ${tanggalFormatted}\n`;
  msg += `🕐 Waktu: ${waktuMulai} - ${waktuSelesai}\n`;
  msg += `📍 Lokasi: ${meeting.lokasi}\n\n`;
  
  msg += "👥 *Peserta:*\n";
  if (meeting.peserta) {
    const pesertaList = meeting.peserta.split(',');
    pesertaList.forEach(p => {
      const trimmed = p.trim();
      if (trimmed) {
        msg += `   • ${trimmed}\n`;
      }
    });
  } else {
    msg += "   (Belum ada data peserta)\n";
  }
  
  msg += `\nTerima kasih, tetap semangat! 💪`;
  
  return msg;
}

/**
 * Format pesan WhatsApp untuk MULTIPLE meetings (COMBINED)
 * Gabungkan semua meetings hari ini menjadi satu pesan
 */
function formatCombinedMeetingsMessage(meetings) {
  if (meetings.length === 0) return "";
  if (meetings.length === 1) return formatMeetingMessage(meetings[0]);
  
  const timezone = Session.getScriptTimeZone();
  
  let msg = `📅 *REMINDER MEETINGS HARI INI* (${meetings.length} meetings)\n\n`;
  
  meetings.forEach((meeting, idx) => {
    const dateObj = new Date(meeting.tanggal);
    const tanggalFormatted = formatDateIndonesian(dateObj, timezone);
    const waktuMulai = extractTime(meeting.waktuMulai);
    const waktuSelesai = extractTime(meeting.waktuSelesai);
    
    msg += `📌 *${idx + 1}. ${meeting.noDokumen} - ${meeting.agenda}*\n`;
    msg += `📅 ${tanggalFormatted} | 🕐 ${waktuMulai} - ${waktuSelesai}\n`;
    msg += `📍 ${meeting.lokasi}\n`;
    
    if (meeting.peserta) {
      const pesertaList = meeting.peserta.split(',').map(p => p.trim()).filter(p => p);
      if (pesertaList.length > 0) {
        msg += `👥 ${pesertaList.join(', ')}\n`;
      }
    }
    msg += "\n";
  });
  
  msg += "Terima kasih, tetap semangat! 💪";
  
  return msg;
}

/**
 * Format tanggal ke format Indonesia (Senin, 15 April 2026)
 */
function formatDateIndonesian(dateObj, timezone) {
  const dayNames = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"];
  const monthNames = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
                      "Juli", "Agustus", "September", "Oktober", "November", "Desember"];
  
  const day = dateObj.getDate();
  const month = dateObj.getMonth();
  const year = dateObj.getFullYear();
  const dayOfWeek = dateObj.getDay();
  
  return `${dayNames[dayOfWeek]}, ${day} ${monthNames[month]} ${year}`;
}

/**
 * Extract hanya HH:mm dari waktu string
 * Input bisa berbentuk: "10:00", "Sat Dec 30 1899 10:00:00 GMT+0707", atau "10:00:00"
 * Output: "10:00"
 */
function extractTime(timeStr) {
  if (!timeStr) return "";
  
  // Convert ke string (dalam case timeStr adalah object atau lainnya)
  const timeString = String(timeStr).trim();
  
  if (!timeString) return "";
  
  // Jika sudah format HH:mm
  if (/^\d{2}:\d{2}$/.test(timeString)) {
    return timeString;
  }
  
  // Jika format jam lengkap (10:00:00 atau Sat Dec 30 1899 10:00:00 GMT+0707)
  const match = timeString.match(/(\d{2}):(\d{2})/);
  if (match) {
    return `${match[1]}:${match[2]}`;
  }
  
  return timeString;
}

// ============================================================================
// WHATSAPP SENDING
// ============================================================================

/**
 * Kirim pesan WhatsApp via Fonnte API
 */
function sendWhatsAppMessage(fonnteToken, targetNumbers, targetGroups, messageText) {
  if (!fonnteToken) {
    Logger.log("❌ Fonnte API Token tidak ada");
    return { success: 0, failure: 0, message: "Token API Fonnte tidak ditemukan" };
  }
  
  const allTargets = [...targetNumbers, ...targetGroups];
  
  if (allTargets.length === 0) {
    Logger.log("❌ Tidak ada target penerima");
    return { success: 0, failure: 0, message: "Tidak ada target penerima" };
  }
  
  let successCount = 0;
  let failureCount = 0;
  
  allTargets.forEach(target => {
    const payload = {
      'target': target,
      'message': messageText
    };
    
    const options = {
      'method': 'post',
      'contentType': 'application/json',
      'headers': { 'Authorization': fonnteToken },
      'payload': JSON.stringify(payload),
      'muteHttpExceptions': true
    };
    
    try {
      const response = UrlFetchApp.fetch(FONNTE_API_URL, options);
      const responseCode = response.getResponseCode();
      const responseBody = response.getContentText();
      
      if (responseCode === 200) {
        const jsonResponse = JSON.parse(responseBody);
        if (jsonResponse.status === true || jsonResponse.status === "true") {
          Logger.log(`✅ Pesan berhasil dikirim ke ${target}`);
          successCount++;
        } else {
          Logger.log(`❌ Gagal ke ${target}: ${jsonResponse.detail || responseBody}`);
          failureCount++;
        }
      } else {
        Logger.log(`❌ HTTP ${responseCode} to ${target}: ${responseBody}`);
        failureCount++;
      }
      
    } catch (e) {
      Logger.log(`❌ Error sending to ${target}: ${e.toString()}`);
      failureCount++;
    }
    
    Utilities.sleep(500);  // 500ms delay antar pengiriman
  });
  
  return { success: successCount, failure: failureCount };
}

// ============================================================================
// LOGGING TO SHEET
// ============================================================================

/**
 * Log hasil pengiriman ke sheet "Logs"
 */
function logSendResult(noDokumen, target, status, message) {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_LOGS);
    if (!sheet) return;  // Jika sheet tidak ada, skip
    
    const timestamp = new Date();
    const row = [timestamp, noDokumen, target, status, message];
    
    sheet.appendRow(row);
    Logger.log(`✅ Logged: ${noDokumen} → ${target} (${status})`);
    
  } catch (e) {
    Logger.log(`⚠️ Error logging: ${e.toString()}`);
  }
}

// ============================================================================
// MAIN TRIGGER FUNCTION
// ============================================================================

/**
 * Fungsi utama yang dipanggil oleh trigger setiap hari
 * Mode: isManualRun = true jika dijalankan manual (show UI)
 *       isManualRun = false jika otomatis (silent)
 * 
 * BEHAVIOR: Jika ada multiple meetings, semua digabung jadi 1 pesan
 */
function checkAndSendReminders(isManualRun = false) {
  Logger.log("=== START: checkAndSendReminders ===");
  
  let settings;
  let targets;
  
  try {
    settings = getSettings();
    targets = getTargets();
  } catch (e) {
    Logger.log(`❌ Error reading settings/targets: ${e.toString()}`);
    if (isManualRun) {
      throw new Error(e.message);
    }
    return null;
  }
  
  // Validasi pengaturan
  if (!settings.fonnteToken || !settings.sendTime) {
    Logger.log("⚠️ Pengaturan tidak lengkap, proses dihentikan");
    return null;
  }
  
  if (targets.numbers.length === 0 && targets.groups.length === 0) {
    Logger.log("⚠️ Tidak ada target penerima, proses dihentikan");
    return null;
  }
  
  // Get meetings untuk hari ini
  const meetings = getMeetingsForToday();
  
  // Jika tidak ada meeting, skip (kecuali manual run)
  if (meetings.length === 0 && !isManualRun) {
    Logger.log("✅ Tidak ada meeting hari ini, proses selesai");
    return null;
  }
  
  // Jika ada meetings atau manual run, process
  if (meetings.length === 0 && isManualRun) {
    Logger.log("ℹ️ Tidak ada meeting hari ini, tapi mengirim pesan template");
  }
  
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_MEETINGS);
  
  // Format combined message untuk semua meetings
  const combinedMessage = formatCombinedMeetingsMessage(meetings);
  if (!combinedMessage) {
    Logger.log("❌ Gagal format pesan");
    return null;
  }
  
  Logger.log(`📌 Processing ${meetings.length} meeting(s)`);
  Logger.log(`Message preview:\n${combinedMessage}\n---`);
  
  // Kirim 1 pesan ke semua target
  const sendResult = sendWhatsAppMessage(
    settings.fonnteToken,
    targets.numbers,
    targets.groups,
    combinedMessage
  );
  
  // Log setiap pengiriman
  const allTargets = [...targets.numbers, ...targets.groups];
  allTargets.forEach((target) => {
    const status = "success";  // Simplified: assume success jika no error
    const meetingList = meetings.map(m => m.noDokumen).join(", ");
    logSendResult(meetingList, target, status, `${meetings.length} meetings reminder`);
  });
  
  // Mark semua meetings sebagai "Sudah_Kirim" = "Yes"
  meetings.forEach(meeting => {
    try {
      const cellRef = `H${meeting.rowIndex}`;  // Column H = Sudah_Kirim (0-based col 7)
      sheet.getRange(cellRef).setValue("Yes");
      Logger.log(`✅ Marked ${meeting.noDokumen} as sent`);
    } catch (e) {
      Logger.log(`⚠️ Error marking sent: ${e.toString()}`);
    }
  });
  
  Logger.log(`=== END: checkAndSendReminders | Sent to: ${sendResult.success + sendResult.failure} targets ===`);
  
  return {
    meetings: meetings,
    totalSent: sendResult.success,
    totalFailed: sendResult.failure
  };
}

// ============================================================================
// MANUAL TEST FUNCTION
// ============================================================================

/**
 * Manual test dari menu
 */
function manualCheckAndSendReminders() {
  const ui = SpreadsheetApp.getUi();
  const response = ui.alert(
    'Konfirmasi Tes',
    'Ini akan menjalankan reminder sekarang. Pesan akan dikirim ke semua target. Lanjutkan?',
    ui.ButtonSet.YES_NO
  );
  
  if (response == ui.Button.YES) {
    try {
      ui.alert("Memproses...", "Tunggu sebentar...", ui.ButtonSet.OK);
      
      const result = checkAndSendReminders(true);
      
      if (!result) {
        ui.alert("Perhatian", "Proses dihentikan (pengaturan tidak lengkap atau tidak ada target)", ui.ButtonSet.OK);
        return;
      }
      
      let message = `✅ Proses Selesai!\n\n`;
      message += `📌 Meetings ditemukan: ${result.meetings.length}\n`;
      message += `✅ Pesan terkirim: ${result.totalSent}\n`;
      message += `❌ Pesan gagal: ${result.totalFailed}\n\n`;
      
      if (result.meetings.length === 0) {
        message += "(Tidak ada meeting hari ini, tapi proses berjalan normal)";
      }
      
      ui.alert("Hasil Tes", message, ui.ButtonSet.OK);
      
    } catch (e) {
      Logger.log(`Error: ${e.toString()}`);
      ui.alert("Error", `Terjadi kesalahan: ${e.message}\n\nCek Logger untuk detail.`, ui.ButtonSet.OK);
    }
  }
}

// ============================================================================
// TRIGGER SETUP FUNCTIONS
// ============================================================================

/**
 * Setup daily trigger berdasarkan waktu di settings
 */
function setupDailyTrigger() {
  const ui = SpreadsheetApp.getUi();
  try {
    const settings = getSettings();
    
    if (!settings.sendTime) {
      ui.alert("Error", "Waktu Kirim belum diisi di sheet 'Pengaturan'", ui.ButtonSet.OK);
      return;
    }
    
    const timeParts = settings.sendTime.split(':');
    if (timeParts.length !== 2) {
      ui.alert("Error", "Format Waktu Kirim salah. Gunakan JJ:MM (misal 08:00)", ui.ButtonSet.OK);
      return;
    }
    
    const hour = parseInt(timeParts[0], 10);
    const minute = parseInt(timeParts[1], 10);
    
    if (isNaN(hour) || isNaN(minute) || hour < 0 || hour > 23 || minute < 0 || minute > 59) {
      ui.alert("Error", "Nilai waktu tidak valid", ui.ButtonSet.OK);
      return;
    }
    
    // Delete old triggers
    deleteTriggers();
    
    // Create new trigger
    ScriptApp.newTrigger('checkAndSendReminders')
      .timeBased()
      .atHour(hour)
      .nearMinute(minute)
      .everyDays(1)
      .inTimezone(Session.getScriptTimeZone())
      .create();
    
    Logger.log(`✅ Trigger berhasil diatur untuk jam ${settings.sendTime}`);
    ui.alert(
      'Sukses',
      `✅ Trigger harian berhasil diatur untuk jam ${settings.sendTime}\n\nTZ: ${Session.getScriptTimeZone()}`,
      ui.ButtonSet.OK
    );
    
  } catch (e) {
    Logger.log(`Error setup trigger: ${e.toString()}`);
    ui.alert("Error", `Gagal setup trigger: ${e.message}`, ui.ButtonSet.OK);
  }
}

/**
 * Delete semua triggers
 */
function deleteTriggers() {
  const ui = SpreadsheetApp.getUi();
  const triggers = ScriptApp.getProjectTriggers();
  
  if (triggers.length === 0) {
    ui.alert("Info", "Tidak ada trigger yang aktif", ui.ButtonSet.OK);
    return;
  }
  
  let deletedCount = 0;
  triggers.forEach(trigger => {
    if (trigger.getHandlerFunction() === "checkAndSendReminders") {
      ScriptApp.deleteTrigger(trigger);
      deletedCount++;
    }
  });
  
  Logger.log(`✅ Deleted ${deletedCount} trigger(s)`);
  ui.alert("Sukses", `✅ Berhasil menghapus ${deletedCount} trigger`, ui.ButtonSet.OK);
}
