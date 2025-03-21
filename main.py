
import sys
import argparse
from argparse import ArgumentParser

from src.spacial.geo_coord_sys import GeoBoundingBox
from src.spacial.table_dimention import Table_Dimention

from src.geography_to_gcode import convert_geography_to_gcode


class Arguments(argparse.Namespace):
    lat_0: str
    lon_0: str
    lat_1: str
    lon_1: str
    table_dim: tuple[int, int]
    rotation: int
    topography: str
    output: str
    num_contours: int
    debug_dir: str
    

def parse_table_dimentions(dimention: str) -> tuple[int, int]:
    items = dimention.split("x")
    assert len(items) == 2
    return (int(items[0]), int(items[1]))


def main(argsv):
    parser = ArgumentParser(prog='geograph_to_gcode')
    parser.add_argument('lat_0', type=float, help='First latitude bounding edge')
    parser.add_argument('lon_0', type=float, help='First longitude bounding edge')
    parser.add_argument('lat_1', type=float, help='Second latitude bounding edge')
    parser.add_argument('lon_1', type=float, help='Second longitude bounding edge')
    parser.add_argument('table_dim', type=parse_table_dimentions, help='table dimentions specified in millimteres WIDTHxHEIGHT')
    parser.add_argument('-t', '--topography', type=str, help='Input topography data files')
    parser.add_argument('-o', '--output', type=str, default="output", help='Name of the output gcode file. Will append ".gcode" if not specifed. Will use name for other files')
    parser.add_argument('-r', '--rotation', type=int, choices=[0, 90, 180, 270], default=0, help='How to rotate the map in degress counter-clockwise')
    parser.add_argument('-d', '--debug-dir', type=str, default=None, help='A directory to write debug file to')
    parser.add_argument('-n', '--num-contours', type=int, default=30, help='The number of elevation contours to use')
    args: Arguments = parser.parse_args(argsv)
    
    # Moosilauke
    bbox = GeoBoundingBox(
        args.lat_0, args.lon_0, args.lat_1, args.lon_1
    )
    
    table_dim = Table_Dimention(*args.table_dim)
    
    convert_geography_to_gcode(bbox, table_dim, args.rotation, args.topography, args.output, num_contours=args.num_contours, debug_file_dir=args.debug_dir)
    


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))