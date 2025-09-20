const links = document.querySelectorAll('nav a');
const pages = document.querySelectorAll('.page'); // intro / remote / health
const home = document.getElementById('home'); // 首頁 header-banner
const homeCards = document.querySelector('.home-card'); // 首頁下方內容
const esp32Stream = document.getElementById("esp32-stream"); // ESP32 即時影像
const deviceStatus = document.getElementById("device-status"); // 顯示 LED 狀態

// ⚠️ 換成你的 ESP32 IP
const esp32_ip = "http://192.168.1.120";

// 預設顯示首頁
home.style.display = "flex";
homeCards.style.display = "block";
links.forEach(l => {
  if (l.dataset.page === "home") l.classList.add("active");
});

// 導覽列切換
links.forEach(link => {
  link.addEventListener('click', e => {
    e.preventDefault();
    const targetPage = link.dataset.page;

    // 隱藏所有 page
    pages.forEach(page => page.style.display = "none");

    if (targetPage === "home") {
      // 顯示首頁
      home.style.display = "flex";
      homeCards.style.display = "block";
    } else {
      // 隱藏首頁
      home.style.display = "none";
      homeCards.style.display = "none";

      // 顯示目標 page
      const page = document.getElementById(targetPage);
      if (page) page.style.display = "block";

      // 如果是遠端控制頁面 → 更新影像串流
      if (targetPage === "remote" && esp32Stream) {
        esp32Stream.src = `${esp32_ip}/stream?time=${Date.now()}`;
      }
    }

    // 導覽列高亮
    links.forEach(l => l.classList.remove("active"));
    link.classList.add("active");
  });
});

// LED 控制函式
function controlLed(color, state) {
  fetch(`${esp32_ip}/${state ? 'on' : 'off'}/${color}`)
    .then(res => res.text())
    .then(text => {
      if (deviceStatus) deviceStatus.innerText = `LED ${color}: ${text}`;
    })
    .catch(err => {
      if (deviceStatus) deviceStatus.innerText = `LED ${color}: 錯誤`;
      console.error(err);
    });
}
