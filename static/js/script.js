let list_checkboxes = document.querySelectorAll('.checkbox__input.secondary'),
    first_checkbox = document.querySelector('.checkbox__input.primary'),
    main_button = document.querySelector('.main__button');

let tracks = [],
    track = {};


main_button.addEventListener('click', () => {
    stringJSON = JSON.stringify(tracks);
    
    $.ajax({
        data: stringJSON,
        dataType: 'POST',
        url: 'get-songs/',
        success: function(response) {
            alert('Успех');
        },
        error: function(response) {
            alert('Неудача');
        }
    });
});

first_checkbox.addEventListener('click', () => {
    if (first_checkbox.checked) {
        list_checkboxes.forEach(item => {
            item.checked = true;
            add_track_in_list(item);
        });
    } else {
        list_checkboxes.forEach(item => {
            item.checked = false;
            add_track_in_list(item);
        });
    }
});

function add_track_in_list(item) {
    var parent = item.parentElement,
        children = parent.children;
    
    track = {
        name: children[2].textContent,
        artist: children[3].textContent,
        album: children[4].textContent,
        duration: children[5].textContent
    };

    if(item.checked) {
        tracks.push(track);
        console.log(tracks);
    } else {
        index = tracks.indexOf(tracks.filter(item => item.name == track.name));
        tracks.splice(index,1);
        console.log(tracks);
    }
}

list_checkboxes.forEach(item => {
    item.addEventListener('click', () => {
        add_track_in_list(item);
    });
});
