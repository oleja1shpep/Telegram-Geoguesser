RULES = [("""
**Основное:**
Дается неограниченное количество времени на ответ
Можно перемещаться по улицам в любых направлениях

**Мультиплеер:**
Нажми кнопку *Сгенерировать панораму*, чтобы получить случайный ключ генерации                          
Пришли его друзьям, чтобы вы смогли отгадывать одинаковые места!
Чтобы установить панораму, отправьте *seed* боту в соответствующем меню режима

**Лимиты:**                               
В день выдаётся 20 игр на все режимы 
Хотите убрать лимит? Поддержите авторов любой суммой больше 49₽ и отправьте подтверждение @govzman
Сделать это можно в главном меню!"""),
                              ("""
**Basic:**
An unlimited amount of time is given to respond
You can move through the streets in any direction

**Multiplayer:**
Click the *Generate Panorama* button to get a random generation key
Send it to your friends so that you can guess the same places!
To set the panorama, send *seed* to the bot in the corresponding mode menu

**Limits:**
There are 20 games per day for all modes
Want to remove the limit? Support the authors with any amount over 49₽ and send a confirmation to @govzman
You can do this in the main menu!""")]

MULTIPLAYER_INFORMATION = [("""                    
Чтобы сыграть с друзьями, сгенерируйте панораму, используя соответствующую кнопку
                            
Если вам уже прислали *seed* для панорамы, отправьте его здесь
"""),
("""
To play with friends, generate a panorama using the corresponding button
       
If you have already got the *seed* for a panorama, send in here""")]


HOW_TO_PLAY = [
    ("""
- Вы оказываетесь в случайной точке на карте мира
- Можете перемещаться на панораме в любых направлениях

Ваша задача: по панораме определить ваше местоположение на реальной карте мира, поставив метку на предполагаемое место вашего нахождения

Каждый раунд по умолчанию будут присылаться интересные факты про геолокацию (это можно отключить в настройках)
"""),
    ("""
- You find yourself at a random point on the world map
- You can move on the panorama in any direction

Your goal is to use the panorama to determine your location on the real map of the world, putting a label on your intended location

Each match you will get entertaining facts about geolocation (you can turn it off in settings)
""")]

GREETING = [("""Привет, {}!\nЯ - аналог игры Geoguessr в Telegram! 
Здесь ты можешь угадывать места по панорамам со всего мира! 
Соревнуйся со своими друзьями и другими игроками"""
),
("""Nice to meet you, {}!\nI am an analogue of the GeoGuessr in Telegram! 
Here you can guess places all over the world! 
Compete with your friends and other players"""
)]

GENERATE_SEED = [
    (
        """*seed*: `{}`\nОтправь его друзьям, чтобы поделиться панорамой!\n\nЧтобы установить панораму, отправьте *seed* боту, находясь в меню соответствующего режима"""
    ),
    (
        """*seed*: `{}`\nSend it to your friends to share the panorama!\n\nTo set panorama, send *seed* to bot while in the menu of the corresponding gamemode"""
    )
]
