import random

def generate_seed():
    seed = ''
    for i in range(6):
        symb = random.randint(0, 25)
        if (symb == 8):
            seed += 'i'
        elif (symb == 11):
            seed += 'L'
        elif (random.randint(0, 1)):
            seed += chr(65 + symb).lower()
        else:
            seed += chr(65 + symb).upper()
    return seed

def coordinates_from_seed(seed, mode):
    random.seed(seed)
    if mode == 'msk':
        x, y = 55.6, 37.38
        x2, y2 = 55.83, 37.78
        zoom = 10 
    elif mode == 'spb':
        x, y = 59.81,  30.2
        x2, y2 = 60.06, 30.47
        zoom = 10
    else:
        x = -90, -180
        x2, y2 = 90, 180
        zoom = 1
        rand_case = random.randint(1, 3); 
        # South America
        if rand_case == 1:
            x, y = -47.362302, -71.624672
            x2, y2 = -9.733599, -65.100000
        elif rand_case == 2:
            x, y = -41.466691, -65.067317
            x2, y2 = -9.733599, -56.807827
        elif rand_case == 3:
            x, y = -35.169281, -56.718168 
            x2, y2 = -9.733599, -48.613274
    lat, lng = x + random.random() * (x2 - x), y + random.random() * (y2 - y)
    return lat, lng, zoom

if __name__ == '__main__':
    seed = generate_seed()
    print(seed)
    print(coordinates_from_seed(seed, 'world'))