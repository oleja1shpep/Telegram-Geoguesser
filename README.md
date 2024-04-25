## Проект “Telegram Geoguessr”

**Участники:**

1. Говзман Илья [tg](t.me/govzman)
2. Олег Рябов [tg](t.me/oleja_shpep)
3. Гараева Аделя [tg](t.me/adelyagaraeva)



**Распределение ролей:**
1. Говзман Илья: 
 - Google Maps API
 - Мини-приложение с панорамой и выбором местоположения
 - Связь с базой данных
2. Рябов Олег: 
 - Работа с MongoDB
 - Телеграм бот
3. Гараева Аделя:
 - Перевод
 - Разработка режимов

**Описание проекта:**
Мы создали Телеграм-бот, который повторяет известную игру [“Geoguessr”](https://www.geoguessr.com/). Суть игры такова: игроку показывается панорама местности, и его задача угадать в какой точке мира он находится и отметить на карте своё предполагаемое местоположение. Чем ближе игрок поставит метку к действительной геолокации, тем больше очков он получит.

Основным способом взаимодействия с игрой является Телеграм-бот, в котором можно выбирать различные сценарии использования. Он сопряжен с мини-приложением, а также с базой данных всех пользователей бота.

Мини-приложение используется для: удобного взаимодействия с панорамами, выбора предполагаемой геопозиции и отправки результата в мини-приложение.

Основные задачи Телеграм-бота это: запуск игры, регистрация пользователя, выбор режимов игры и вывод статистики по играм пользователей в том или ином режиме.

**Мини-приложение:**
	Мини-приложение используется для удобного взаимодействия с панорамами Google Maps. Мы выбрали именно этот способ показа панорамы местности, потому что так играть будет удобно как с компьютера, так и со смартфона.

**Тг-бот:**
	Основные задачи Телеграм-бота это: запуск игры, регистрация пользователя, выбор режимов игры и вывод топа игроков по среднему количеству очков в том или ином режиме.

**База данных:**
	Доступ к базе данных осуществляется при помощи библиотеки PyMongo. В базу данных будет записываться уникальный id пользователя в Телеграме, дата его регистрации, а также результаты каждого сыгранного им матча. Сделано это для того, чтобы пользователь мог узнать рейтинг игроков и посмотреть статистику своих игр внутри каждого режима.

**Взаимодействие с ботом:**
Чтобы начать взаимодействие с ботом нужно прислать команду /start. Далее появится форма для входа/регистрации пользователя. После входа, появляется меню с выбором режимов игры. После выбора режима, игрок попадает в меню данного режима, в котором находятся кнопки "Играть", "Рейтинг", "Мои результаты". 

Нажав кнопку "Играть", игрок будет брошен в случайное место на карте мира, где есть панорамы Google Maps. Появляется мини-приложение с панорамой, где игрок может перемещаться при помощи встроенного метода перемещения в Google Maps. Далее при помощи этого мини-приложения пользователь отправляет предполагаемую геопозицию. Затем бот в зависимости от дальности метки игрока, до его местоположения на гугл картах считает количество очков и присылает его пользователю.

Нажав кнопку "Рейтинг" пользователь узнает топ 10 игроков в данном режиме и свое место в этом рейтинге.

Нажав кнопку "Мои результаты" игрок сможет узнать результаты своих последних игр в данном режиме.