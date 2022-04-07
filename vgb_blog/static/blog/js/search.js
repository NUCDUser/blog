const searchButton = document.querySelector("#search-button");
const searchInput = document.querySelector("#search-input");
const searchForm = document.querySelector("#search-form");

// Overwrites the same function so that it only works when searching
searchButton.onclick = function () {
    searchInput.focus();
};

searchForm.onsubmit = function (e) {
    e.preventDefault();
    if (searchInput.value.startsWith("#")) {
        let newValue = searchInput.value
            .slice(1)
            .replaceAll(" ", "-")
            .toLowerCase();
        searchInput.name = "slug";
        searchInput.value = newValue;
        searchForm.action = `/blog/tag/?slug=${newValue}`;
        searchForm.submit();
    }
    searchForm.submit();
};
