ymaps.ready(function () {
    // Ищем панораму в переданной точке.

    // 55.972790, 36.906859 - левый верхний
    // 55.392818, 38.342368 - правый нижний 

    var founded = false; 
    
    while (founded == false) {
        ymaps.panorama.locate([55.4 + Math.random() * 0.6, 36.9 + Math.random() * 0.45]).done( // [55.733685, 37.588264]
            function (panoramas) {
                // Убеждаемся, что найдена хотя бы одна панорама.
                if (panoramas.length > 0) {
                    founded = true;
                    // Создаем плеер с одной из полученных панорам.
                    var player = new ymaps.panorama.Player(
                        'player1',
                        // Панорамы в ответе отсортированы по расстоянию
                        // от переданной в panorama.locate точки. Выбираем первую,
                        // она будет ближайшей.
                        panoramas[0],
                        // Зададим направление взгляда, отличное от значения
                        // по умолчанию.
                        { direction: [256, 16], controls: [] },
                    );
                    console.log(player.getPanorama().getPosition().join(', '))
                } else {
                    console.log("panorama wasn't founded!")
                }
            },
            function (error) {
                // Если что-то пошло не так, сообщим об этом пользователю.
                alert(error.message);
            }
        );
        break;
    }

    var myMap = new ymaps.Map("map", {
        center: [55.76, 37.64],
        zoom: 10,
        controls: []
    }, {
        searchControlProvider: 'yandex#search'
    }),

        // Создаем геообъект с типом геометрии "Точка".
        myGeoObject = new ymaps.GeoObject({
            // Описание геометрии.
            geometry: {
                type: "Point",
                coordinates: [55.8, 37.8]
            },
            // Свойства.
            properties: {
                // Контент метки.
                iconContent: 'Тут',
                hintContent: 'Тащи!'
            }
        }, {
            // Опции.
            // Иконка метки будет растягиваться под размер ее содержимого.
            preset: 'islands#blackStretchyIcon',
            // Метку можно перемещать.
            draggable: true
        })

    myMap.geoObjects
        .add(myGeoObject)


    myMap.events.add('click', function (e) {
        var coords = e.get('coords');
        myGeoObject.geometry.setCoordinates(coords);
    });
});

