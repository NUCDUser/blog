const searchButton = document.querySelector("#search-button");
const searchInput = document.querySelector("#search-input");
const searchForm = document.querySelector("#search-form");

// Overwrites the same function so that it only works when searching
searchButton.onclick = function () {
    searchInput.focus();
};

searchForm.onsubmit = function (e) {
    e.preventDefault();
    console.log(searchInput.value);
    if (searchInput.value.startsWith("#")) {
        let newValue = searchInput.value
            .slice(1)
            .replaceAll(" ", "-")
            .toLowerCase();
        let tagUrl = `/blog/search/tag/${newValue}`;
        console.log(tagUrl);
        console.log(newValue);
        window.location.assign(tagUrl);
        return;
    }
    let tagUrl = `/blog/search/${searchInput.value}`;
    window.location.assign(tagUrl);
    return;
};
