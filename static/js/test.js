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
    stringJSON = JSON.stringify(tracks);

    const request = new XMLHttpRequest();

    // сообщаем соединению, что отправляем данные методом POST в конкретный python файл относительо HTML
    request.open('POST', '');

    // создаём настройку, что соединение будет принимать или передавать строку JSON
    request.setRequestHeader('Content-type', 'application/json');

    // отправляем данные (можно поместить любой строковый тип)
    request.send(stringJSON);

    // смотрим статус отправки данных на сервер
    request.addEventListener('readystatechange', () => {
        if (request.readyState === 4 && request.status === 200) {
            console.log('Я отправил данные, принимай их у себя');
        } else {
            console.log('Что-то не так...');
        }
    });
    
});

