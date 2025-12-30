// ===== 全域選取 =====
const links = document.querySelectorAll('nav a');
const pages = document.querySelectorAll('.page'); // intro / remote / health
const home = document.getElementById('home'); // 首頁 header-banner
const homeCards = document.querySelector('.home-card'); // 首頁下方內容
const deviceStatus = document.getElementById("device-status"); // 顯示設備狀態的區域
const esp32Stream = document.getElementById('camera'); // 顯示即時影像的區域
const socket = new WebSocket("ws://localhost:8000/ws");
// ===== 預設首頁 =====
home.style.display = "flex";
homeCards.style.display = "block";
links.forEach(l => { if (l.dataset.page === "home") l.classList.add("active"); });

// ===== 導覽列切換 =====
links.forEach(link => {
  link.addEventListener('click', e => {
    e.preventDefault();
    const targetPage = link.dataset.page;
    pages.forEach(page => page.style.display = "none");

    if(targetPage === "home") {
      home.style.display = "flex";
      homeCards.style.display = "block";
    } else {
      home.style.display = "none";
      homeCards.style.display = "none";
      const page = document.getElementById(targetPage);
      if(page) page.style.display = "block";
    }

    links.forEach(l => l.classList.remove("active"));
    link.classList.add("active");
  });
});

// ===== 控制 LED (多色) =====
function controlLed(color, state) {
  // 使用 Blynk API 更新 Virtual Pin
  const AUTH_TOKEN = "Lw5rbEUMUJEHZUQbPF1BWSFQpG4esDaZ"; // 改為您自己的 Auth Token
  const VIRTUAL_PIN = "v1"; // 假設我們控制的是 V1

  const url = `https://blynk.cloud/external/api/update/${VIRTUAL_PIN}?token=${AUTH_TOKEN}&value=${state ? 1 : 0}`;

  // 發送控制請求
  fetch(url)
    .then(res => res.text())
    .then(text => {
      deviceStatus.innerText = `LED ${color}: ${text}`;

      // 刷新即時影像
      refreshStream();
    })
    .catch(err => {
      deviceStatus.innerText = `LED ${color}: 錯誤`;
      console.error(err);
    });
}

// ===== 即時影像刷新 =====
function refreshStream() {
  if (esp32Stream) {
    // 更新即時影像的源，這裡假設您的 ESP32 提供視頻流
    esp32Stream.src = `${esp32_ip}/stream?time=${Date.now()}`;
  }
}

// ===== 自動刷新影像（每秒） =====
setInterval(() => {
  if (document.getElementById('remote').style.display === 'block') {
    refreshStream();
  }
}, 1000);

<script>
// 從 GitHub API 獲取 images 資料夾內的檔案
fetch('https://api.github.com/repos/RCL803/SAT/commits?path=images&per_page=1')
  .then(response => response.json())
  .then(commits => {
    const latestCommitSha = commits[0].sha;

    // 再用 commit SHA 抓檔案清單
    return fetch(`https://api.github.com/repos/RCL803/SAT/git/trees/${latestCommitSha}?recursive=1`);
  })
  .then(response => response.json())
  .then(tree => {
    // 找出 images 資料夾的檔案
    const images = tree.tree.filter(file => file.path.startsWith('images/') && file.type === 'blob');

    // 取最新的檔案（因為 commit API 已經是最新的）
    const latestImage = images[0].path.split('/').pop();

    // 建立 Raw URL
    const imageUrl = `https://raw.githubusercontent.com/RCL803/SAT/main/images/${latestImage}`;
    document.getElementById("bp-photo").src = imageUrl;
  })
  .catch(error => console.error('Error fetching latest image:', error));

fetch('https://raw.githubusercontent.com/RCL803/SAT/main/bp.json?t=' + Date.now())
  .then(res => res.json())
  .then(data => {
    document.getElementById("SYS").textContent = "測試成功: " + (data.SYS || "沒抓到資料");
    document.getElementById("DIA").textContent = data.DIA;
    document.getElementById("result").textContent = data.result;
  })
  .catch(err => console.error('讀取血壓數據失敗:', err));
</script>


// 頁面載入時自動呼叫
window.onload = fetchBPResults;
