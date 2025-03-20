
from matplotlib.path import Path
from src.geography.contour_calculation.contour_loop import ContourLoop
from src.geography.contour_calculation.loop_closer import merge_loop_fragments
from src.table_dimention import Table_Dimention

def _get_loop_fragmment(verticies, close=False):
    codes = [Path.MOVETO] + [Path.LINETO for _ in verticies[1:]]
    if close:
        verticies.append(verticies[0])
        codes.append(Path.CLOSEPOLY)
    return Path(verticies, codes)


def test_closed_loop():
    test_table_dim = Table_Dimention(400, 300)
    test_loops = [
        _get_loop_fragmment([
            (10, 10),
            (10, 20),
            (20, 20),
            (20, 10),
        ], close=True),
    ]
    recv_loops = merge_loop_fragments(test_loops, test_table_dim)
    exp_loops = [
        ContourLoop([
            (10, 10),
            (10, 20),
            (20, 20),
            (20, 10),
        ]),
    ]
    assert recv_loops == exp_loops


def test_two_closed_loops():
    test_table_dim = Table_Dimention(400, 300)
    test_loops = [
        _get_loop_fragmment([
            (10, 10),
            (10, 20),
            (20, 20),
            (20, 10),
        ], close=True),
        _get_loop_fragmment([
            (30, 10),
            (30, 20),
            (40, 20),
            (40, 10),
        ], close=True),
    ]
    recv_loops = merge_loop_fragments(test_loops, test_table_dim)
    exp_loops = [
        ContourLoop([
            (10, 10),
            (10, 20),
            (20, 20),
            (20, 10),
        ]),
        ContourLoop([
            (30, 10),
            (30, 20),
            (40, 20),
            (40, 10),
        ]),
    ]
    assert recv_loops == exp_loops


def test_open_loop_left_side():
    test_table_dim = Table_Dimention(400, 300)
    test_loops = [
        _get_loop_fragmment([
            ( 0, 20),
            (10, 20),
            (10, 10),
            ( 0, 10),
        ], close=False),
    ]
    recv_loops = merge_loop_fragments(test_loops, test_table_dim)
    exp_loops = [
        ContourLoop(
            [
                ( 0, 20),
                (10, 20),
                (10, 10),
                ( 0, 10),
            ],
            border_indices=[0, 3]
        ),
    ]
    assert recv_loops == exp_loops


def test_open_loop_right_side():
    test_table_dim = Table_Dimention(400, 300)
    test_loops = [
        _get_loop_fragmment([
            (400, 10),
            (390, 10),
            (390, 20),
            (400, 20),
        ], close=False),
    ]
    recv_loops = merge_loop_fragments(test_loops, test_table_dim)
    exp_loops = [
        ContourLoop(
            [
                (400, 10),
                (390, 10),
                (390, 20),
                (400, 20),
            ],
            border_indices=[0, 3]
        ),
    ]
    assert recv_loops == exp_loops


def test_open_loop_top_to_left():
    test_table_dim = Table_Dimention(400, 300)
    test_loops = [
        _get_loop_fragmment([
            (35, 300),
            (40, 220),
            ( 0, 240),
        ], close=False),
    ]
    recv_loops = merge_loop_fragments(test_loops, test_table_dim)
    exp_loops = [
        ContourLoop(
            [
                (35, 300),
                (40, 220),
                ( 0, 240),
                ( 0, 300),
            ],
            border_indices=[0, 2, 3]
        ),
    ]
    assert recv_loops == exp_loops


def test_open_loop_top_to_bottom():
    test_table_dim = Table_Dimention(400, 300)
    test_loops = [
        _get_loop_fragmment([
            (35, 300),
            (40, 220),
            (70,   0),
        ], close=False),
    ]
    recv_loops = merge_loop_fragments(test_loops, test_table_dim)
    exp_loops = [
        ContourLoop(
            [
                (35, 300),
                (40, 220),
                (70,   0),
                ( 0,   0),
                ( 0, 300),
            ],
            border_indices=[0, 2, 3, 4]
        ),
    ]
    assert recv_loops == exp_loops


def test_open_loop_bottom_to_top():
    test_table_dim = Table_Dimention(400, 300)
    test_loops = [
        _get_loop_fragmment([
            (70,   0),
            (40, 220),
            (35, 300),
        ], close=False),
    ]
    recv_loops = merge_loop_fragments(test_loops, test_table_dim)
    exp_loops = [
        ContourLoop(
            [
                ( 70,   0),
                ( 40, 220),
                ( 35, 300),
                (400, 300),
                (400,   0),
            ],
            border_indices=[0, 2, 3, 4]
        ),
    ]
    assert recv_loops == exp_loops


def test_open_loop_left_side_all_around():
    test_table_dim = Table_Dimention(400, 300)
    test_loops = [
        _get_loop_fragmment([
            ( 0, 10),
            (10, 10),
            (10, 20),
            ( 0, 20),
        ], close=False),
    ]
    recv_loops = merge_loop_fragments(test_loops, test_table_dim)
    exp_loops = [
        ContourLoop(
            [
                (  0,  10),
                ( 10,  10),
                ( 10,  20),
                (  0,  20),
                (  0, 300),
                (400, 300),
                (400,   0),
                (  0,   0),
            ],
            border_indices=[0, 3, 4, 5, 6, 7]
        ),
    ]
    assert recv_loops == exp_loops


def test_open_loop_right_top_and_closed_loop():
    test_table_dim = Table_Dimention(400, 300)
    test_loops = [
        _get_loop_fragmment([
            (10, 10),
            (10, 20),
            (20, 20),
            (20, 10),
        ], close=True),
        _get_loop_fragmment([
            (400, 250),
            (360, 250),
            (360, 300),
        ], close=False),
    ]
    recv_loops = merge_loop_fragments(test_loops, test_table_dim)
    exp_loops = [
        ContourLoop(
            [
                (10, 10),
                (10, 20),
                (20, 20),
                (20, 10),
            ],
            border_indices=[]
        ),
        ContourLoop(
            [
                (400, 250),
                (360, 250),
                (360, 300),
                (400, 300),
            ],
            border_indices=[0, 2, 3]
        ),
    ]
    assert recv_loops == exp_loops


def test_join_frags():
    # Frag 1: Bottom --> Top
    # Frag 2: Top --> right
    # Frag 3: Top --> Bottom (left of first 2)
    # Joins frag 1 & 2; Closes frag 3
    test_table_dim = Table_Dimention(400, 300)
    test_loops = [
        _get_loop_fragmment([
            (200,   0),
            (210, 250),
            (200, 300),
        ], close=False),
        _get_loop_fragmment([
            (310, 300),
            (320, 360),
            (400, 350),
        ], close=False),
        _get_loop_fragmment([
            (100, 300),
            (110, 250),
            (100,   0),
        ], close=False),
    ]
    recv_loops = merge_loop_fragments(test_loops, test_table_dim)
    exp_loops = [
        ContourLoop(
            [
                (200,   0),
                (210, 250),
                (200, 300),
                (310, 300),
                (320, 360),
                (400, 350),
                (400,   0),
            ],
            border_indices=[0, 2, 3, 5, 6]
        ),
        ContourLoop(
            [
                (100, 300),
                (110, 250),
                (100,   0),
                (  0,   0),
                (  0, 300),
            ],
            border_indices=[0, 2, 3, 4]
        ),
    ]
    assert recv_loops == exp_loops
