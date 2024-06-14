
currPage = 1;
search = ""
currentOrder = "id"


window.addEventListener('DOMContentLoaded', (event) => {
    currentOrder = "id"
    getCardsReplace("", 1);
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
    getCardsReplace(search, currPage)

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


function getCardsReplace(search, page = 1) {
    search = search
    console.log(search)
    currPage = 1;
    fetch('AjaxSearch', {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ 'jsonBody': { "search": search, "page": page, "orderBy": currentOrder } })
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
        body: JSON.stringify({ 'jsonBody': { "search": search, "page": page, "orderBy": currentOrder } })
    })
        .then(response => response.text())
        .then(text => {
            document.getElementById('cardHolder').innerHTML += text

        })
}

$(document).ready(function () {
    $('.dropdown').each(function (key, dropdown) {
        var $dropdown = $(dropdown);
        $dropdown.find('.dropdown-menu a').on('click', function () {
            $dropdown.find('button').text($(this).text()).append(' <span class="caret"></span>');
        });
    });
});