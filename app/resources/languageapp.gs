// BiliClass LanguageApp gateway v3. Replace ALL of Code.gs with this code.
// The setup guide fills a private code automatically. Do not publish that code.
// An empty setup code keeps support for the older Script Properties setup.
// Deploy Web app: Execute as Me; Who has access: Anyone.
// A deployment uses its owner's LanguageApp quota across ALL connected computers.
const BILICLASS_SETUP_CODE = '';

function doGet() {
  return ContentService.createTextOutput('Điểm kết nối Apps Script của BiliClass. '
    + 'Để kiểm tra dịch, hãy bấm Thử kết nối trong BiliClass → Cài đặt → Dịch thuật. '
    + 'Không cần chọn doPost rồi bấm Chạy trong trình soạn mã.');
}

function doPost(e) {
  const reply = data => ContentService.createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
  let request;
  try {
    if (!e || !e.postData || e.postData.contents.length > 64000) return reply({error: 'request'});
    request = JSON.parse(e.postData.contents);
    if (!request || typeof request !== 'object' || Array.isArray(request)) return reply({error: 'request'});
  } catch (_) { return reply({error: 'request'}); }
  const properties = PropertiesService.getScriptProperties();
  const code = BILICLASS_SETUP_CODE || properties.getProperty('BILICLASS_ACCESS_CODE');
  if (!code || !/^[A-Za-z0-9_-]{16,200}$/.test(code) || request.accessCode !== code)
    return reply({error: 'auth'});
  const texts = request.texts;
  if (!Array.isArray(texts) || !texts.length || texts.length > 25 ||
      !['vi', 'en'].includes(request.source) || !['vi', 'en'].includes(request.target) ||
      texts.some(t => typeof t !== 'string' || !t.trim() || t.length > 4500) ||
      texts.reduce((n, t) => n + t.length, 0) > 4500) return reply({error: 'request'});
  // Conservative owner-wide guard: <=4500 calls in a rolling 24-hour window.
  // This is not Google's quota balance/reset time. Rejected/ambiguous calls stay counted.
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(3000)) return reply({error: 'rate'});
  try {
    const now = Date.now();
    let ledger = JSON.parse(properties.getProperty('BILICLASS_USAGE') || '[]');
    ledger = ledger.filter(row => row[0] + 3600000 > now - 24 * 60 * 60 * 1000);
    // Hourly buckets stay counted for at least 24 hours, at most 25 hours.
    const hour = Math.floor(now / 3600000) * 3600000;
    if (ledger.reduce((n, row) => n + row[1], 0) + texts.length > 4500) return reply({error: 'quota'});
    const last = ledger[ledger.length - 1];
    if (last && last[0] === hour) last[1] += texts.length;
    else ledger.push([hour, texts.length]);
    properties.setProperty('BILICLASS_USAGE', JSON.stringify(ledger));
  } catch (_) { return reply({error: 'quota'}); }
  finally { lock.releaseLock(); }
  const translations = [];
  try {
    for (const text of texts) translations.push(LanguageApp.translate(text, request.source, request.target, {contentType: 'html'}));
    return reply({translations});
  } catch (error) {
    const message = String(error);
    return reply({error: /short time|per second|rate/i.test(message) ? 'rate' : /quota|limit|too many times/i.test(message) ? 'quota' : 'service', translations});
  }
}
