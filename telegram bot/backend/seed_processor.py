import random
MODES = ['msk', 'spb', 'rus', 'usa', 'wrld']
MODE_TO_RADIUS = {'msk': 0, 'spb': 0, 'rus': 4, 'usa': 4, 'wrld': 5}

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
        x, y = 55.571, 37.364
        x2, y2 = 55.912, 37.844
        x_center, y_center = 55.753235, 37.622512
        zoom = 10 
    elif mode == 'spb':
        x, y = 59.81,  30.2
        x2, y2 = 60.06, 30.47
        x_center, y_center = 59.939043, 30.315826
        zoom = 10
    elif mode == 'rus':
        x, y =  54.943761, 31.875376
        x2, y2 = 69.321693, 135.542207
        x_center, y_center = 61.680306, 90.125792
        zoom = 3
        rand_case = random.randint(1, 12); 
        if rand_case == 1:
            x, y =  54.395809,  19.963150
            x2, y2 = 54.931611, 22.579783
        elif rand_case == 2:
            x, y =  56.042289, 28.869637
            x2, y2 = 61.054803, 31.639278
        elif rand_case == 3:
            x, y =  54.943761, 31.875376
            x2, y2 = 69.321693, 135.542207
        elif rand_case == 4:
            x, y = 54.922812, 31.870243
            x2, y2 = 55.793310, 135.645871
        elif rand_case == 5:
            x, y = 51.929353, 79.885300
            x2, y2 = 54.859996, 119.686307
        elif rand_case == 6:
            x, y =  50.458641, 103.302560
            x2, y2 = 52.367061, 119.393563
        elif rand_case == 7:
            x, y = 49.728084, 127.742623
            x2, y2 = 55.100807, 142.969699
        elif rand_case == 8:
            x, y = 44.834123, 134.834166
            x2, y2 = 49.749743, 136.589325
        elif rand_case == 9:
            x, y = 42.653027, 131.406969
            x2, y2 = 44.955345, 135.623084
        elif rand_case == 10:
            x, y = 51.906737, 34.449059
            x2, y2 = 55.154587, 59.800473
        elif rand_case == 11:
            x, y = 50.490628, 36.025059
            x2, y2 = 52.042008, 48.674186
        elif rand_case == 12:
            x, y = 43.601399, 40.401071
            x2, y2 = 50.058438, 46.346261
    else:
        x, y = -90, -180
        x2, y2 = 90, 180
        x_center, y_center = 0, 0
        zoom = 1
        rand_case = random.randint(1, 15); 
        # South America
        if rand_case == 1:
            x, y = -49.284542, -72.608645
            x2, y2 = -27.334468, -70.581439
        elif rand_case == 2:
            x, y = -48.412354, -70.501183
            x2, y2 = -17.094978, -65.757256
        elif rand_case == 3:
            x, y = -39.095993, -65.681480
            x2, y2 = -11.260235, -57.117673
        elif rand_case == 4:
            x, y = -34.945629, -56.990732
            x2, y2 = -8.313673, -52.840326
        elif rand_case == 5:
            x, y = -32.055120, -52.804520
            x2, y2 = -6.104159, -48.767408
        elif rand_case == 6:
            x, y = -23.983129, -48.551254
            x2, y2 = -1.695513, -38.936049
        elif rand_case == 7:
            x, y = -13.131989, -38.925841
            x2, y2 = -4.814302, -34.330878
        elif rand_case == 8:
            x, y = -17.064574, -73.302553
            x2, y2 = -13.282524, -65.818419
        elif rand_case == 9:
            x, y = -15.541132, -76.182122
            x2, y2 = -9.467373, -73.298731
        elif rand_case == 10:
            x, y = -13.334793, -78.098332
            x2, y2 = 2.718603, -76.216134
        elif rand_case == 11:
            x, y = -10.008889, -80.004263
            x2, y2 = 1.036968, -78.089577
        elif rand_case == 12:
            x, y =  -6.815206, -81.223244
            x2, y2 = 0.034623, -79.998050
        elif rand_case == 13:
            x, y = 0.313049, -76.095463
            x2, y2 = 11.123643, -73.011817
        elif rand_case == 14:
            x, y = 1.842713, -61.708479
            x2, y2 = 5.084230, -59.569147
        elif rand_case == 15:
            x, y = 7.415949, -82.701898
            x2, y2 = 9.419654, -78.384054

    lat, lng = x + random.random() * (x2 - x), y + random.random() * (y2 - y)
    return lat, lng, x_center, y_center, zoom


def check_seed(string, right_mode):
    unpacked = string.split('_')
    if len(unpacked) != 2: 
        return False
    mode, seed = unpacked
    if (mode != right_mode):
        return False
    if (len(seed) == 6 and all(map(lambda x: 'a' <= x <= 'z', list(seed.lower()))) and mode in MODES):
        return True
    return False
