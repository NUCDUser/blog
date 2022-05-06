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
        let tagUrl = `/search/tag/${newValue}`;
        window.location.assign(tagUrl);
        return;
    } else if (searchInput.value.startsWith("@")) {
        let newValue = searchInput.value
            .slice(1)
            .replaceAll(" ", "_")
            .toLowerCase();
        let tagUrl = `/search/category/${newValue}`;
        window.location.assign(tagUrl);
        return;
    }
    let tagUrl = `/search/${searchInput.value}`;
    window.location.assign(tagUrl);
    return;
};
