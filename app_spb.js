let panorama;
let myMap;
let marker;
let panorama_pos = "";

async function findPanorama() {
    let length = 0;
    let i = 0;
    while (length == 0) {
        try {
            const panoramas = await ymaps.panorama.locate([59.81 + Math.random() * 0.25, 30.2 + Math.random() * 0.27]); // 59.810058, 30.202484 | 60.062432, 30.467086
            length = panoramas.length;
            // Убеждаемся, что найдена хотя бы одна панорама.
            if (panoramas.length > 0) {
                founded = true;
                // Создаем плеер с одной из полученных панорам.
                panorama = new ymaps.panorama.Player(
                    'pano',
                    // Панорамы в ответе отсортированы по расстоянию
                    // от переданной в panorama.locate точки. Выбираем первую,
                    // она будет ближайшей.
                    panoramas[0],
                    // Зададим направление взгляда, отличное от значения
                    // по умолчанию.
                    { direction: [256, 16], controls: [] },
                );
                panorama.events.add(['panoramachange', 'renderload'], (a) => {
                    console.log('AAA', a);
                    setInterval(() => { panorama._engine._renderer._billboards._billboards = [] }, 100)
                })

                panorama_pos = panorama.getPanorama().getPosition().join(' ');
                console.log(panorama_pos);
            } else {
                console.log("panorama wasn't founded!")
            }
        } catch {
            // Если что-то пошло не так, сообщим об этом пользователю.
            alert(error.message);
        }
        i++;
        console.log(`${i} - len: ${length}, bool: ${(i >= 35) || (length > 0)}`)
        if ((i >= 20) || (length > 0)) {
            break;
        }
    }
}

ymaps.ready(function () {
    // Ищем панораму в переданной точке.

    // 55.604232, 37.386655 - левый нижний
    // 55.879429, 37.769319 - правый верхний 

    findPanorama();

    myMap = new ymaps.Map("map", {
        center: [59.938472, 30.308016],
        zoom: 10,
        controls: []
    }, {
        searchControlProvider: 'yandex#search'
    }),

        // Создаем геообъект с типом геометрии "Точка".
        marker = new ymaps.GeoObject({
            // Описание геометрии.
            geometry: {
                type: "Point",
                coordinates: [55.752534, 37.621429]
            },
            // Свойства.
            properties: {
                // Контент метки.
                iconContent: 'Тут!',
                hintContent: 'Тащи!'
            }
        }, {
            // Опции.
            // Иконка метки будет растягиваться под размер ее содержимого.
            preset: 'islands#blueDotIcon',
            // Метку можно перемещать.
            draggable: true
        })

    myMap.geoObjects
        .add(marker)

    myMap.events.add('click', function (e) {
        var coords = e.get('coords');
        marker.geometry.setCoordinates(coords);
    });
});

function GetPanoramaCords() {
    console.log(panorama_pos);
    var res = `${panorama_pos} ${marker.geometry.getCoordinates().join(' ')}`;
    return res;
}