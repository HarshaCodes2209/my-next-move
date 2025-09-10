window.addEventListener("scroll", function () {
    const header = document.getElementById("header");
    if (window.scrollY > 50) {
        header.classList.add("scrolled");
    } else {
        header.classList.remove("scrolled");
    }
});


let lastScrollTop = 0;
const footer = document.querySelector('footer');

window.addEventListener('scroll', function () {
    let currentScroll = window.pageYOffset || document.documentElement.scrollTop;

    if (currentScroll > lastScrollTop) {
        footer.style.display = 'none';
    } else {
        footer.style.display = 'block';
    }

    lastScrollTop = currentScroll <= 0 ? 0 : currentScroll;
});