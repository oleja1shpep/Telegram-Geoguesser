MOSCOW_SINGLE_PLAYER_RULES = [("""
Проверь своё знание Москвы!

Дается неограниченное количество времени на ответ
Можно перемещаться по улицам в любых направлениях"""),
("""
Check your knowledge of Moscow!

You are given an unlimited amount of time to answer
You can move through the streets in any direction""")]

RUSSIA_SINGLE_PLAYER_RULES = [("""
Как хорошо ты знаешь Россию?

Дается неограниченное количество времени на ответ
Можно перемещаться по улицам в любых направлениях"""),
("""
Check your knowledge of Russian!

You are given an unlimited amount of time to answer
You can move through the streets in any direction""")]

SPB_SINGLE_PLAYER_RULES = [("""
Проверь своё знание Санкт-Петербурга!

Дается неограниченное количество времени на ответ
Можно перемещаться по улицам в любых направлениях"""),
("""
Check your knowledge of St. Petersburg!

You are given an unlimited amount of time to answer
You can move through the streets in any direction""")]


USA_SINGLE_PLAYER_RULES = [("""
Как хорошо ты знаешь США?

Дается неограниченное количество времени на ответ
Можно перемещаться по улицам в любых направлениях"""),
("""
How well do you know USA?

You are given an unlimited amount of time to answer
You can move through the streets in any direction""")]

WORLD_SINGLE_PLAYER_RULES = [("""
Как хорошо ты знаешь земной шар?

Дается неограниченное количество времени на ответ
Можно перемещаться по улицам в любых направлениях"""),
("""
How well do you know Earth?

You are given an unlimited amount of time to answer
You can move through the streets in any direction""")]


HOW_TO_PLAY = [("""
- Вы оказываетесь в случайной точке на карте мира
- Можете перемещаться на панораме в любых направлениях

Ваша задача: по панораме определить ваше местоположение на реальной карте мира, поставив метку на предполагаемое место вашего нахождения

"""),
               ("""
- You find yourself at a random point on the world map
- You can move on the panorama in any direction

Your task is to use the panorama to determine your location on the real map of the world, putting a label on your intended location
               """)
               ]

GREETING = [("""Привет, {}!\nЯ - аналог игры Geoguessr в телеграме! Здесь ты можешь сыграть в отгадывание мест по всей России или по отдельным городам и посоревноваться с другими игроками"""
             ),
             ("""Nice to meet you, {}!\nI am an analogue of the Geoguessr game in telegram! Here you can play guessing places all over Russia or in individual cities and compete with other players"""
              )]

GPT_REQUEST = """
Give me some entertaining fact about {} using {} language. Message text should be no longer that 50 words. 
Please, answer according to following structure: <address> : <fact about address>
"""

GENERATE_SEED = [
    (
        """seed: `{}`\nПришли его друзьям, чтобы поделиться панорамой!"""
    ),
    (
        """seed: `{}`\nSend it to your friends to share the panorama!"""
    )
]