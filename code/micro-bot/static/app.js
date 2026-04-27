// static/app.js
const ws = new WebSocket("ws://" + location.host + "/ws");
const chat = document.getElementById("chat");

ws.onmessage = function (event) {
  const data = JSON.parse(event.data);
  addMsg("bot", data.text);
};

function send() {
  const input = document.getElementById("msg");
  addMsg("user", input.value);

  ws.send(JSON.stringify({ text: input.value }));
  input.value = "";
}

function addMsg(type, text) {
  const div = document.createElement("div");
  div.className = "msg " + type;
  div.textContent = type + ": " + text;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}
