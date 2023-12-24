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

async function findPanorama(lowerX, lowerY) {
    let length = 0;
    let i = 0;
    while (length == 0) {
        try {
            const panoramas = await ymaps.panorama.locate([lowerX - 0.02 + Math.random() * 0.04, lowerY - 0.02 + Math.random() * 0.04]);
            length = panoramas.length;
            // Убеждаемся, что найдена хотя бы одна панорама.
            if (panoramas.length > 0) {
                founded = true;
                // Создаем плеер с одной из полученных панорам.
                var panorama = new ymaps.panorama.Player(
                    'pano',
                    panoramas[0],
                    { direction: [256, 16], controls: [] },
                );
                panorama.events.add(['panoramachange', 'renderload'], (a) => {
                    console.log('AAA', a);
                    setInterval(() => { panorama._engine._renderer._billboards._billboards = [] }, 100)
                })

                panorama_pos = panorama.getPanorama().getPosition().join(' ');
                console.log(panorama_pos);
            } else {
                console.log("panorama wasn't founded!", lowerX, lowerY)
            }
        } catch {
            // Если что-то пошло не так, сообщим об этом пользователю.
            // alert(error.message);
        }
        i++;
        console.log(`${i} - len: ${length}, bool: ${(i >= 5) || (length > 0)}`)
        if (length > 0) {
            return await true;
        }
        if (i >= 5) {
            return await false;
        }
    }
    return await true;
}

function readRandomLineFromText(text) {
    const lines = text.split('\n');
    const randomIndex = Math.floor(Math.random() * lines.length);
    return lines[randomIndex];
}

ymaps.ready(async function () {
    const url1 = 'https://raw.githubusercontent.com/oleja1shpep/Telegram-Geoguesser/MiniAppBranch/cities.txt'
    const response = await fetch(url1);
    const data = await response.text();
    var city = await readRandomLineFromText(data);
    console.log(city);

    // 55.604232, 37.386655 - левый нижний
    // 55.879429, 37.769319 - правый верхний 

    var [lowerX, lowerY] = await fetchData(city);
    var j = 0;
    res = await findPanorama(lowerX, lowerY)
    while (!res && (j < 5)) {
        city = await readRandomLineFromText(data);
        console.log(city);
        [lowerX, lowerY] = await fetchData(city);
        res = await findPanorama(lowerX, lowerY)
        ++j;
    }
    if (!res && (j >= 5)) {
        findPanorama(55.763903, 37.542487)
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

function GetPanoramaCords() {
    console.log(panorama_pos);
    var res = `${panorama_pos} ${marker.geometry.getCoordinates().join(' ')}`;
    return res;
}