
currentOrder = "id"
search = ""
date = ""
window.addEventListener('DOMContentLoaded', (event) => {
    getCardsPaged("", 1);
    currentOrder = "id"

    date = ""
});




function changeOrder(str) {
    element = document.getElementById(str)
    dataValue = element.getAttribute("data-value");
    if (dataValue.startsWith("-")) {
        element.setAttribute("data-value", dataValue.replace("-", ""))
        dataValue = dataValue.replace("-", "")
        document.getElementById(str + "Chevron").setAttribute("d", "M19.5 8.25l-7.5 7.5-7.5-7.5")
    }
    else {
        element.setAttribute("data-value", "-" + dataValue)
        dataValue = "-" + dataValue
        document.getElementById(str + "Chevron").setAttribute("d", "M4.5 15.75l7.5-7.5 7.5 7.5")

    }
    currPage = 1;
    currentOrder = dataValue
    getCardsReplace(search, 1)

}

window.onscroll = function (ev) {
    if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight) {
        total = document.getElementById("totalPaginas").value
        if (currPage < total) {
            currPage++;
            getCardsPaged(currPage);
        }
    }
};

function getCardsReplace(search, page = 1, date = '') {
    currentSearch = search
    currPage = 1;

    fetch('AjaxSearch', {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ 'jsonBody': { "search": search, "page": page, "orderBy": currentOrder, "date": date } })
    })
        .then(response => response.text())
        .then(text => {
            document.getElementById('cardHolder').innerHTML = ``
            document.getElementById('cardHolder').innerHTML += text

        })
}

function getCardsPaged(page = 1) {
    fetch('AjaxSearch', {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ 'jsonBody': { "search": search, "page": page, "orderBy": currentOrder, "date": date } })
    })
        .then(response => response.text())
        .then(text => {
            document.getElementById('cardHolder').innerHTML += text

        })
}