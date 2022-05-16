const searchButton = document.querySelector("#search-button");
const searchInput = document.querySelector("#search-input");

// Overwrites the same function so that it only works when searching
searchButton.onclick = function () {
    searchInput.focus();
};
