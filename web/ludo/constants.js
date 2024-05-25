export const COORDINATES_MAP = {
    0: [6, 13],
    1: [6, 12],
    2: [6, 11],
    3: [6, 10],
    4: [6, 9],
    5: [5, 8],
    6: [4, 8],
    7: [3, 8],
    8: [2, 8],
    9: [1, 8],
    10: [0, 8],
    11: [0, 7],
    12: [0, 6],
    13: [1, 6],
    14: [2, 6],
    15: [3, 6],
    16: [4, 6],
    17: [5, 6],
    18: [6, 5],
    19: [6, 4],
    20: [6, 3],
    21: [6, 2],
    22: [6, 1],
    23: [6, 0],
    24: [7, 0],
    25: [8, 0],
    26: [8, 1],
    27: [8, 2],
    28: [8, 3],
    29: [8, 4],
    30: [8, 5],
    31: [9, 6],
    32: [10, 6],
    33: [11, 6],
    34: [12, 6],
    35: [13, 6],
    36: [14, 6],
    37: [14, 7],
    38: [14, 8],
    39: [13, 8],
    40: [12, 8],
    41: [11, 8],
    42: [10, 8],
    43: [9, 8],
    44: [8, 9],
    45: [8, 10],
    46: [8, 11],
    47: [8, 12],
    48: [8, 13],
    49: [8, 14],
    50: [7, 14],
    51: [6, 14],

    // HOME ENTRANCE

    // P1
    100: [7, 13],
    101: [7, 12],
    102: [7, 11],
    103: [7, 10],
    104: [7, 9],
    105: [7, 8],

    // P3
    200: [7, 1],
    201: [7, 2],
    202: [7, 3],
    203: [7, 4],
    204: [7, 5],
    205: [7, 6],

    // P4
    300: [13,7], 
    301: [12, 7],
    302: [11, 7],
    303: [10, 7],
    304: [9, 7],
    305: [8, 7],

    //P2
    400: [1, 7],
    401: [2, 7],
    402: [3, 7],
    403: [4, 7],
    404: [5, 7],
    405: [6, 7],


    // BASE POSITIONS

    // P1
    500: [1.5, 10.58], 
    501: [3.57, 10.58],
    502: [1.5, 12.43],
    503: [3.57, 12.43],

    // P2
    800: [1.5, 1.58],
    801: [3.57, 1.58],
    802: [1.5, 3.45],
    803: [3.57, 3.45],


    // P3
    600: [10.5, 1.58],
    601: [12.54, 1.58],
    602: [10.5, 3.45],
    603: [12.54, 3.45],

    // P4
    700: [10.5, 10.58], 
    701: [12.54, 10.58],
    702: [10.5, 12.43],
    703: [12.54, 12.43],
};

export const STEP_LENGTH = 6.66;

// export const PLAYERS = ['P1', 'P2', 'P3', 'P4'];

export const BASE_POSITIONS = {
    P1: [500, 501, 502, 503],
    P2: [800, 801, 802, 803],
    P3: [600, 601, 602, 603],
    P4: [700, 701, 702, 703],
}

export const START_POSITIONS = {
    P1: 0,
    P2: 13,
    P3: 26,
    P4: 39,
}

export const HOME_ENTRANCE = {
    P1: [100, 101, 102, 103, 104],
    P2: [400, 401, 402, 403, 404],
    P3: [200, 201, 202, 203, 204],
    P4: [300, 301, 302, 303, 304],
}

export const HOME_POSITIONS = {
    P1: 105,
    P2: 405,
    P3: 205,
    P4: 305
}

export const TURNING_POINTS = {
    P1: 50,
    P2: 11,
    P3: 24,
    P4: 37,
}

export const SAFE_POSITIONS = [0, 8, 13, 21, 26, 34, 39, 47];

export const STATE = {
    DICE_NOT_ROLLED: 'DICE_NOT_ROLLED',
    DICE_ROLLED: 'DICE_ROLLED',
}