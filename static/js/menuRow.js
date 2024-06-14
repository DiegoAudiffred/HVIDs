
currPage = 1;
search = ""
currentOrder = "id"


window.addEventListener('DOMContentLoaded', (event) => {
    currentOrder = "id"
    getCardsReplace2("", 1);
});






function getCardsReplace2(search, page = 1, element) {
    if (element && element.id) {
        var searchBarFId = element.id;

        var match = searchBarFId.match(/(\d+)$/);
        var number = match ? parseInt(match[1], 10) : null;


        //var targetId = "searchBarMenu_" + number;

        search = search;
        currPage = 1;

        fetch('AjaxSearch2', {
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
                var cardHolderId = 'cardHolder2_' + number;
                var elementosLista = [];

                var tempDiv = document.createElement('div');

                tempDiv.innerHTML = text;

                var cardHolder = document.getElementById(cardHolderId);

                cardHolder.innerHTML = '';

                for (var i = 0; i < tempDiv.children.length; i++) {
                    var child = tempDiv.children[i];

                    var nuevoId = child.id + number;

                    child.id = nuevoId;

                    child.querySelectorAll('[id]').forEach(function (element) {
                        element.id = element.id  + number;
                    });

                    cardHolder.appendChild(child);

                    elementosLista.push({
                        'id': nuevoId,
                        'imagen': child.querySelector('img').src,
                        'texto': child.querySelector('span').textContent
                    });

                }

            });





    }
  
     else {
     
        search = search
        currPage = 1;

        fetch('AjaxSearch2', {
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
                document.getElementById('cardHolder2_').innerHTML = ``
                document.getElementById('cardHolder2_').innerHTML += text


            })
    }    


}





$(document).ready(function () {
    $('.dropdown').each(function (key, dropdown) {
        var $dropdown = $(dropdown);
        $dropdown.find('.dropdown-menu a').on('click', function () {
            $dropdown.find('button').text($(this).text()).append(' <span class="caret"></span>');
        });
    });
});