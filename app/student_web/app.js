"use strict";
const $ = id => document.getElementById(id);
const params = new URLSearchParams(location.hash.slice(1));
let joinCode = params.get("join") || "", sessionId = params.get("session") || "";
const storageKey = "biliclass:" + sessionId;
let saved = null;
try { saved = JSON.parse(sessionStorage.getItem(storageKey) || "null"); } catch (_) {}
let token = saved?.token || "", socket = null, reconnectTimer, snapshot = null, pending = saved?.pending || null, ended = false, backoff = 700, clockOffset = 0, lastReceived = Date.now();
function persist() { try { sessionStorage.setItem(storageKey, JSON.stringify({token,pending})); } catch (_) {} }
function message(text) { $("connection").textContent = text; }
function fail(text) { $("error").textContent = text; }
$("joinCode").value = joinCode;
function textForRound(r, item) { return r.language === "vi" ? item.vi : r.language === "en" ? item.en : item.vi + "\n" + item.en; }
function render(data, fromServer = false) {
    const old = snapshot; snapshot = data;
    if (fromServer) clockOffset = data.server_time * 1000 - Date.now();
    ended = data.status === "ended";
    $("lessonTitle").textContent = data.title;
    const r = data.round;
    $("roundStatus").textContent = ended ? "Tiết học đã kết thúc" : !r ? "Chờ thầy cô mở câu hỏi" : r.status === "open" ? "Đang nhận câu trả lời" : r.status === "revealed" ? "Đã công bố kết quả" : "Đã đóng câu hỏi";
    if (!r) { $("promptVi").textContent = "Sẵn sàng học cùng lớp"; $("promptEn").textContent = "Ready to learn together"; return; }
    $("promptVi").textContent = r.language === "en" ? "" : r.vi;
    $("promptEn").textContent = r.language === "vi" ? "" : r.en;
    const selected = pending?.round_id === r.id ? pending.answer : r.selected;
    const options = $("options");
    const identity = r.id + ":" + r.language;
    if (options.dataset.round !== identity) {
        options.replaceChildren(); options.dataset.round = identity;
        for (const choice of r.options) {
            const button = document.createElement("button"); button.type = "button"; button.className = "option"; button.dataset.option = choice.id;
            const label = document.createElement("strong"); label.textContent = choice.id;
            const content = document.createElement("span"); content.textContent = textForRound(r, choice);
            button.append(label,content); button.addEventListener("click", () => submit(r.id,choice.id)); options.append(button);
        }
    }
    for (const button of options.children) {
        button.classList.toggle("selected", selected === button.dataset.option);
        button.classList.toggle("correct", r.status === "revealed" && button.dataset.option === r.correct);
        button.setAttribute("aria-pressed", String(selected === button.dataset.option));
        button.disabled = ended || r.status !== "open" || socket?.readyState !== WebSocket.OPEN;
    }
    if (pending && pending.round_id !== r.id) { pending = null; persist(); }
    $("feedback").textContent = pending ? "Đang gửi câu trả lời…" : r.selected ? "Đã nhận lựa chọn " + r.selected : "";
    $("explanation").hidden = r.status !== "revealed";
    $("explanation").textContent = r.kind === "poll" ? "Đây là khảo sát; không có đáp án đúng hoặc sai." : (r.correct ? "Đáp án: " + r.correct + "\n" : "") + (r.rationale_vi || "") + "\n" + (r.rationale_en || "");
    if (old?.round?.id !== r.id) fail("");
}
function submit(round, answer) {
    if (socket?.readyState !== WebSocket.OPEN) { fail("Đang mất kết nối. Chờ kết nối lại rồi chọn đáp án."); return; }
    const random = new Uint8Array(16); crypto.getRandomValues(random);
    pending = {round_id:round, answer, submission_id:Array.from(random,v=>v.toString(16).padStart(2,"0")).join("")};
    persist(); socket.send(JSON.stringify(pending)); if(snapshot) render(snapshot);
}
function connect() {
    clearTimeout(reconnectTimer);
    const candidate = new WebSocket((location.protocol === "https:" ? "wss://" : "ws://") + location.host + "/student");
    socket = candidate;
    socket.onopen = () => { if(socket !== candidate) return; lastReceived = Date.now(); backoff = 700; message("Đã kết nối với lớp"); socket.send(JSON.stringify({token})); };
    socket.onmessage = event => {
        if(socket !== candidate) return;
        lastReceived = Date.now();
        const data = JSON.parse(event.data);
        if (data.type === "snapshot") {
            const shouldRetry = pending && data.round?.id === pending.round_id;
            render(data, true);
            if (shouldRetry && pending) socket.send(JSON.stringify(pending));
        } else if (data.type === "ack") {
            if (pending?.submission_id === data.submission_id) { pending = null; persist(); }
            if(snapshot?.round?.id === data.round_id) snapshot.round.selected = data.answer;
            if(snapshot) render(snapshot); fail("");
        } else if (data.type === "error") { fail(data.message); pending = null; persist(); if(snapshot) render(snapshot); }
    };
    socket.onclose = event => {
        if(socket !== candidate) return;
        if(ended) { message("Tiết học đã kết thúc"); return; }
        if(event.code === 1008) { fail("Mã kết nối hết hiệu lực. Vào lại lớp để tiếp tục."); $("join").hidden = false; token = ""; persist(); return; }
        message("Mất kết nối · đang thử lại…"); if(snapshot) render(snapshot);
        reconnectTimer = setTimeout(connect, backoff); backoff = Math.min(8000,backoff * 1.6);
    };
    socket.onerror = () => { if(socket === candidate) message("Đang kiểm tra kết nối với máy giáo viên…"); };
}
async function join(event) {
    event?.preventDefault(); fail(""); joinCode = $("joinCode").value.trim();
    if($("recoveryInput").value.trim()) token = $("recoveryInput").value.trim();
    try {
        const response = await fetch("/api/join", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({join:joinCode,token,seat:$("seat").value ? Number($("seat").value) : null})});
        const data = await response.json(); if(!response.ok) { if(token && response.status === 400) { token = ""; pending = null; persist(); } throw new Error(data.detail || "Chưa vào được lớp"); }
        token = data.token; persist(); $("recoveryCode").value = token; $("recovery").hidden = false; $("recoveryInput").value = ""; $("join").hidden = true; $("lesson").hidden = false; connect();
    } catch(error) { fail(error.message); }
}
$("joinForm").addEventListener("submit",join);
message("Sẵn sàng vào lớp");
if (token && joinCode) join();
setInterval(() => { const r=snapshot?.round; $("timer").textContent = r?.status === "open" ? Math.max(0,Math.ceil((r.deadline*1000-Date.now()-clockOffset)/1000)) + " giây" : ""; },250);

function reconnectAfterLoss() {
    const previous = socket; socket = null;
    if(previous) previous.close(4000, "connection lost");
    message("Mất kết nối · đang thử lại…"); if(snapshot) render(snapshot);
    clearTimeout(reconnectTimer); if(token && !ended) reconnectTimer = setTimeout(connect, backoff);
}
window.addEventListener("offline", reconnectAfterLoss);
window.addEventListener("online", () => { if(token && !ended && socket?.readyState !== WebSocket.OPEN && socket?.readyState !== WebSocket.CONNECTING) connect(); });
setInterval(() => { if(socket?.readyState === WebSocket.OPEN && Date.now()-lastReceived > 8000) reconnectAfterLoss(); },2000);
