const form = document.getElementById("chatForm");
const input = document.getElementById("messageInput");
const chatArea = document.getElementById("chatArea");
const welcome = document.getElementById("welcome");
const sendBtn = document.getElementById("sendBtn");
const statusText = document.getElementById("statusText");
const statusPill = document.querySelector(".status-pill");
const sidebar = document.getElementById("sidebar");
const proModal = document.getElementById("proModal");
let history = [];
let busy = false;

async function checkStatus() {
  try {
    const r = await fetch("/api/status");
    const d = await r.json();
    statusText.textContent = d.configured ? "AI connected" : "Setup required";
    statusPill.classList.toggle("connected", !!d.configured);
  } catch {
    statusText.textContent = "Connection unavailable";
  }
}
checkStatus();

function addMessage(role, text, extraClass="") {
  const row = document.createElement("div");
  row.className = `message ${role} ${extraClass}`.trim();
  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "user" ? "You" : "D";
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  row.append(avatar, bubble);
  chatArea.appendChild(row);
  chatArea.scrollTop = chatArea.scrollHeight;
  row.scrollIntoView({behavior:"smooth", block:"end"});
  return {row, bubble};
}
function resizeInput(){input.style.height="auto";input.style.height=Math.min(input.scrollHeight,180)+"px";}
input.addEventListener("input", resizeInput);

async function sendMessage(text) {
  text = (text || "").trim();
  if (!text || busy) return;
  welcome.style.display = "none";
  busy = true;
  sendBtn.disabled = true;
  input.value = "";
  resizeInput();
  addMessage("user", text);
  history.push({role:"user", content:text});
  const pending = addMessage("assistant", "Thinking…", "typing");
  try {
    const response = await fetch("/api/chat", {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({messages:history})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "The AI service could not respond.");
    pending.bubble.textContent = data.reply;
    pending.row.classList.remove("typing");
    history.push({role:"assistant", content:data.reply});
  } catch (e) {
    pending.bubble.textContent = e.message || "Something went wrong. Please try again.";
    pending.row.classList.remove("typing");
  } finally {
    busy = false;
    sendBtn.disabled = false;
    input.focus();
  }
}
form.addEventListener("submit", e => {e.preventDefault(); sendMessage(input.value);});
document.querySelectorAll(".prompt").forEach(btn => btn.addEventListener("click", () => {
  const prompt = btn.dataset.prompt;
  sidebar.classList.remove("open");
  if (prompt) sendMessage(prompt);
}));
document.getElementById("newChat").addEventListener("click", () => {
  history = [];
  chatArea.replaceChildren();
  welcome.style.display = "";
  input.value = "";
  resizeInput();
  sidebar.classList.remove("open");
});
document.getElementById("menuBtn").addEventListener("click", () => sidebar.classList.toggle("open"));
document.getElementById("upgradeBtn").addEventListener("click", () => proModal.hidden = false);
document.getElementById("closeModal").addEventListener("click", () => proModal.hidden = true);
document.getElementById("gotIt").addEventListener("click", () => proModal.hidden = true);
proModal.addEventListener("click", e => {if (e.target === proModal) proModal.hidden = true;});
input.addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) {e.preventDefault(); form.requestSubmit();}
});
