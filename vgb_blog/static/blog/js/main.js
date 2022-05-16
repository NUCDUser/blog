const searchBar = document.querySelector("#search-bar");
const searchButton = document.querySelector("#search-button");
const searchInput = document.querySelector("#search-input");

let searchBarOpen = false;

searchButton.onclick = function () {
    if (searchBarOpen) {
        searchBar.style.transform = "translateY(-70px)";
        searchBarOpen = false;
        return;
    }
    searchBar.style.transform = "translateY(0)";
    searchInput.focus();
    searchBarOpen = true;
};

const headlineCarousel = document.querySelector("#headlineCarousel");
const carouselIndicators = document.querySelector(".carousel-indicators");
const carouselNext = document.querySelector(".carousel-control-next");
const carouselPrev = document.querySelector(".carousel-control-prev");
const carouselControls = [carouselIndicators, carouselNext, carouselPrev];

headlineCarousel.addEventListener("mouseenter", function () {
    carouselControls.forEach((e) => {
        e.style.opacity = 1;
    });
});

headlineCarousel.addEventListener("mouseleave", function () {
    carouselControls.forEach((e) => {
        e.style.opacity = 0;
    });
});
