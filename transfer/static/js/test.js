const button = document.querySelector('.main-button');

tracks = [
    {
        artist: 'John Newman',
        duration: '3:24',
        album: 'Freedom',
        name: 'Love me again'
    },
    {
        artist: 'John Newman',
        duration: '3:24',
        album: 'Freedom',
        name: 'Love me again'
    },
    {
        artist: 'John Newman',
        duration: '3:24',
        album: 'Freedom',
        name: 'Love me again'
    },
];

button.addEventListener('click', () => {
    let stringJSON = JSON.stringify(tracks);
    let csrf = $("input[name=csrfmiddlewaretoken]").val();

    $.ajax({
        data: {stringJSON: stringJSON,
                csrfmiddlewaretoken: csrf},
        dataType: 'json',
        type: 'POST',
        url: '/get-songs/',
        success: function (response){
            alert('Успех')
                  },
        error: function (response){
            alert('Неудача')
                  }

    });
    return false;

});


