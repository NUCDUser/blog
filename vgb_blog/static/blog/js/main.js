const searchBar = document.querySelector("#search-bar");
const searchButton = document.querySelector("#search-button");
const searchForm = document.querySelector("#search-form");
const searchInput = document.querySelector("#search-input");

let searchOpen = false;

searchButton.onclick = function () {
    if (searchOpen) {
        searchBar.style.transform = "translateY(-70px)";
        searchOpen = false;
        return;
    }
    searchBar.style.transform = "translateY(0)";
    searchInput.focus();
    searchOpen = true;
};

searchForm.onsubmit = function (e) {
    e.preventDefault();
    if (searchInput.value.startsWith("#")) {
        let newValue = searchInput.value
            .slice(1)
            .replaceAll(" ", "-")
            .toLowerCase();
        let tagUrl = `/blog/search/tag/${newValue}`;
        window.location.assign(tagUrl);
    }
    let tagUrl = `/blog/search/${searchInput.value}`;
    window.location.assign(tagUrl);
};
