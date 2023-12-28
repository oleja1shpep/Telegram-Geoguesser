let panorama;
let myMap;
let marker;
let panorama_pos = "";

async function fetchData(city) {
    try {
        const response = await fetch("https://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode=" + city + "&format=json");
        const data = await response.json();
        // обработка данных
        const center = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
        let [lowerX, lowerY] = center.split(' ').map(Number);
        console.log(lowerY, lowerX);
        return await [lowerY, lowerX]
    } catch (error) {
        return await [55.763903, 37.542487]
    }
}


async function findPanorama(x, delta_x, y, delta_y) {
    let length = 0;
    let i = 0;
    while (length == 0) {
        try {
            const panoramas = await ymaps.panorama.locate([x + Math.random() * delta_x, y + Math.random() * delta_y]);
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
            // alert(error.message);
        }
        i++;
        console.log(`${i} - len: ${length}, bool: ${(i >= 5) || (length > 0)}`)
        if (i >= 25) {
            return await false;
        }
    }
    return await true;
}

console.log(window.location.hash)


let x, delta_x, y, delta_y, center_x, center_y, zoom;

let hash = window.location.hash.split('?')[0]
console.log(hash)

if (hash == "#Moscow") {
    x = 55.6
    delta_x = 0.23
    y = 37.38
    delta_y = 0.4
    center_x = 55.752534
    center_y = 37.621429
    zoom = 10
} else if (hash == "#SPB") {
    x = 59.81
    delta_x = 0.25
    y = 30.2
    delta_y = 0.27
    center_x = 59.938472
    center_y = 30.308016
    zoom = 10
} else {
    x = 55.6
    delta_x = 0.23
    y = 37.38
    delta_y = 0.4
    center_x = 55.752534
    center_y = 37.621429
    zoom = 5
}

if (hash == "#Russia") {
    ymaps.ready(async function () {
        const url1 = 'https://raw.githubusercontent.com/oleja1shpep/Telegram-Geoguesser/MiniAppBranch/cities.txt'
        const response = await fetch(url1);
        const data = await response.text();
        var city = await readRandomLineFromText(data);
        console.log(city);

        var [lowerX, lowerY] = await fetchData(city);
        var j = 0;
        res = await findPanorama(lowerX - 0.02, 0.04, lowerY - 0.02, 0.04)
        while (!res && (j < 5)) {
            city = await readRandomLineFromText(data);
            console.log(city);
            [lowerX, lowerY] = await fetchData(city);
            res = await findPanorama(lowerX - 0.02, 0.04, lowerY - 0.02, 0.04)
            ++j;
        }
        if (!res && (j >= 5)) {
            findPanorama(55.763903, 0.01, 37.542487, 0.01)
        }

        myMap = new ymaps.Map("map", {
            center: [62.518617, 106.100958],
            zoom: 2,
            controls: []
        }, {
            searchControlProvider: 'yandex#search'
        }),

            // Создаем геообъект с типом геометрии "Точка".
            marker = new ymaps.GeoObject({
                // Описание геометрии.
                geometry: {
                    type: "Point",
                    coordinates: [62.518617, 106.100958]
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
    // } else if (window.location.hash == "#Moscow" || window.location.hash == "#SPB") {
} else if (hash == "#Belarus") {
    ymaps.ready(async function () {
        const url1 = 'https://raw.githubusercontent.com/oleja1shpep/Telegram-Geoguesser/MiniAppBranch/cities_belarus.txt'
        const response = await fetch(url1);
        const data = await response.text();
        var city = await readRandomLineFromText(data);
        console.log(city);

        var [lowerX, lowerY] = await fetchData(city);
        var j = 0;
        res = await findPanorama(lowerX - 0.02, 0.04, lowerY - 0.02, 0.04)
        while (!res && (j < 5)) {
            city = await readRandomLineFromText(data);
            console.log(city);
            [lowerX, lowerY] = await fetchData(city);
            res = await findPanorama(lowerX - 0.02, 0.04, lowerY - 0.02, 0.04)
            ++j;
        }
        if (!res && (j >= 5)) {
            findPanorama(27.562411, 0.0001, 53.902272, 0.0001)
        }

        myMap = new ymaps.Map("map", {
            center: [53.703751, 28.902882],
            zoom: 6,
            controls: []
        }, {
            searchControlProvider: 'yandex#search'
        }),

            // Создаем геообъект с типом геометрии "Точка".
            marker = new ymaps.GeoObject({
                // Описание геометрии.
                geometry: {
                    type: "Point",
                    coordinates: [53.703751, 28.902882]
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
} else {
    ymaps.ready(function () {
        console.log("!", x, delta_x, y, delta_y, center_x, center_y, zoom)
        // Ищем панораму в переданной точке.
        findPanorama(x, delta_x, y, delta_y);

        myMap = new ymaps.Map("map", {
            center: [center_x, center_y],
            zoom: zoom,
            controls: []
        }, {
            searchControlProvider: 'yandex#search'
        }),

            // Создаем геообъект с типом геометрии "Точка".
            marker = new ymaps.GeoObject({
                // Описание геометрии.
                geometry: {
                    type: "Point",
                    coordinates: [center_x, center_y]
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
}

function GetPanoramaCords() {
    console.log(panorama_pos);
    var res = `${panorama_pos} ${marker.geometry.getCoordinates().join(' ')}`;
    return res;
}

function readRandomLineFromText(text) {
    const lines = text.split('\n');
    const randomIndex = Math.floor(Math.random() * lines.length);
    return lines[randomIndex];
}
