// ===== 全域選取 =====
const links = document.querySelectorAll('nav a');
const pages = document.querySelectorAll('.page'); // intro / remote / health
const home = document.getElementById('home'); // 首頁 header-banner
const homeCards = document.querySelector('.home-card'); // 首頁下方內容

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
