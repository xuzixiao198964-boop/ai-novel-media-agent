// 平滑滚动
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    const href = this.getAttribute('href');
    if (href !== '#download' && href !== '#contact' && href !== '#privacy' && href !== '#terms') {
      e.preventDefault();
      const target = document.querySelector(href);
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    }
  });
});

// 导航栏滚动效果
let lastScroll = 0;
const nav = document.querySelector('nav');

window.addEventListener('scroll', () => {
  const currentScroll = window.pageYOffset;

  if (currentScroll > 100) {
    nav.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
  } else {
    nav.style.boxShadow = 'none';
  }

  lastScroll = currentScroll;
});
