import random
MODES = ['msk', 'spb', 'rus', 'usa', 'wrld']
MODE_TO_RADIUS = {'msk': 0, 'spb': 0, 'rus': 4, 'usa': 3, 'wrld': 5}

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
        rand_case = random.randint(1, 12)
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
    elif mode == 'usa':
        x, y = 34.949688, -113.990370
        x2, y2 = 42.801610, -85.994596
        x_center, y_center = 38.2149907, -101.4041103
        zoom = 4.5
        rand_case = random.randint(1, 25)
        if rand_case == 1:
            x, y = 38.023709, -124.508643
            x2, y2 = 48.259446, -122.829837
        elif rand_case == 2:
            x, y =  38.058365, -122.805347
            x2, y2 = 48.936160, -95.132851
        elif rand_case == 3:
            x, y = 36.265432, -122.713546
            x2, y2 =  38.076391, -95.104588
        elif rand_case == 4:
            x, y = 36.265432, -122.713546
            x2, y2 =  38.076391, -95.104588
        elif rand_case == 5:
            x, y =  34.459288, -121.294712
            x2, y2 =  36.272217, -95.115785
        elif rand_case == 6:
            x, y = 32.660267, -120.499896
            x2, y2 = 34.473495, -95.114916
        elif rand_case == 7:
            x, y = 31.940442, -112.912404
            x2, y2 = 32.660942, -95.107462
        elif rand_case == 8:
            x, y = 29.539102, -104.298925
            x2, y2 = 31.933306, -102.942300
        elif rand_case == 9:
            x, y = 29.874066, -102.940009
            x2, y2 =  31.912309, -95.107447
        elif rand_case == 10:
            x, y = 28.226720, -100.222951
            x2, y2 = 29.875951, -94.955104
        elif rand_case == 11:
            x, y = 29.568903, -95.103820
            x2, y2 = 48.465761, -93.107331
        elif rand_case == 12:
            x, y = 29.564781, -93.074473
            x2, y2 = 48.096707, -91.080924
        elif rand_case == 13:
            x, y = 29.067681, -91.045620
            x2, y2 = 47.917422, -89.035700
        elif rand_case == 14:
            x, y = 30.186678, -88.987678
            x2, y2 = 47.460429, -87.014051
        elif rand_case == 15:
            x, y = 30.388431, -86.983783
            x2, y2 = 46.691742, -85.014478
        elif rand_case == 16:
            x, y = 29.630667, -84.978182
            x2, y2 = 45.199525, -83.163791
        elif rand_case == 17:
            x, y = 29.198211, -83.152060
            x2, y2 =  41.687286, -81.338139
        elif rand_case == 18:
            x, y = 25.224336, -82.746151
            x2, y2 = 29.186356, -80.139326
        elif rand_case == 19:
            x, y = 31.964060, -81.331289
            x2, y2 = 42.013672, -79.295851
        elif rand_case == 20:
            x, y = 33.572730, -79.264305
            x2, y2 = 42.621677, -77.221550
        elif rand_case == 21:
            x, y = 34.617459, -77.172740
            x2, y2 = 43.585003, -75.096591
        elif rand_case == 22:
            x, y = 39.002902, -75.116361
            x2, y2 = 44.901484, -73.200074
        elif rand_case == 23:
            x, y = 39.002902, -75.116361
            x2, y2 = 40.631862, -73.151272
        elif rand_case == 24:
            x, y = 60.458010, -149.901176
            x2, y2 = 70.017836, -142.942029
        elif rand_case == 25:
            x, y = 18.645801, -160.286210
            x2, y2 =  22.341667, -154.597792
    else: # World mode
        x, y = -90, -180
        x2, y2 = 90, 180
        x_center, y_center = 0, 0
        zoom = 1
        rand_case = random.randint(1, 30); 
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
        # North America
        elif rand_case == 16:
            x, y = 13.834853, -97.789355
            x2, y2 = 21.448042, -87.189081
        elif rand_case == 17:
            x, y = 16.799699, -104.668923
            x2, y2 = 34.444475, -97.790154
        elif rand_case == 18:
            x, y = 22.418745, -115.999144
            x2, y2 = 55.062914, -104.732497
        elif rand_case == 19:
            x, y = 30.897817, -124.318517
            x2, y2 = 63.003453, -116.009337
        elif rand_case == 20:
            x, y = 49.677100, -134.373729
            x2, y2 = 69.598913, -124.441785
        elif rand_case == 21:
            x, y = 59.686963, -162.778099
            x2, y2 = 69.571087, -134.614924
        elif rand_case == 22:
            x, y = 16.580835, -71.566493
            x2, y2 = 19.737945, -60.163992
        elif rand_case == 23:
            x, y = 45.013016, -104.696011
            x2, y2 = 54.201269, -52.647464
        elif rand_case == 24:
            x, y = 40.303447, -104.686628
            x2, y2 = 44.924055, -62.530040
        elif rand_case == 25:
            x, y = 34.476446, -104.674850
            x2, y2 = 40.239656, -73.919229
        elif rand_case == 26:
            x, y = 28.631966, -97.790223
            x2, y2 = 34.420591, -77.849619
        elif rand_case == 27:
            x, y = 24.201249, -83.148786
            x2, y2 = 28.593611, -79.955611
        # Greenland
        elif rand_case == 28: 
            x, y = 62.758256, -51.236426
            x2, y2 = 68.753873, -50.524927
        elif rand_case == 29: 
            x, y = 65.534729, -38.249562
            x2, y2 = 66.373432, -35.220591
        elif rand_case == 30: 
            x, y = 72.099301, -24.622787
            x2, y2 = 73.034822, -21.955264


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
