
currPage = 1;
search = ""
currentOrder = "id"


window.addEventListener('DOMContentLoaded', (event) => {
    currentOrder = "id"
    getCardsReplace("", 1);
});




function getCardsReplace(search, page = 1) {
    search = search
    //console.log(search)
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



$(document).ready(function () {
    $('.dropdown').each(function (key, dropdown) {
        var $dropdown = $(dropdown);
        $dropdown.find('.dropdown-menu a').on('click', function () {
            $dropdown.find('button').text($(this).text()).append(' <span class="caret"></span>');
        });
    });
});