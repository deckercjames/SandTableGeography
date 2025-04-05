
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
    table_dim: str
    rotation: int
    topography: str
    output: str
    num_contours: int
    debug_dir: str
    

def parse_table_dimentions(dimention: str) -> Table_Dimention:
    items = dimention.split("x")
    int_items = []
    for item in items:
        try:
            int_items.append(int(item))
        except ValueError:
            raise argparse.ArgumentTypeError("Invalid integer value. Must take the form WIDTHxHIEGHT or DIAMETER")
        
    if len(int_items) == 1:
        return Table_Dimention.create_circular_table(int_items[0])
    
    if len(int_items) == 2:
        return Table_Dimention.create_rect_table(int_items[0], int_items[1])
    
    raise argparse.ArgumentTypeError("Incorrect number of dimentions. Must take the form WIDTHxHIEGHT or DIAMETER")


def main(argsv):
    parser = ArgumentParser(prog='geograph_to_gcode')
    parser.add_argument('lat_0', type=float, help='First latitude bounding edge')
    parser.add_argument('lon_0', type=float, help='First longitude bounding edge')
    parser.add_argument('lat_1', type=float, help='Second latitude bounding edge')
    parser.add_argument('lon_1', type=float, help='Second longitude bounding edge')
    parser.add_argument('table_dim', type=parse_table_dimentions, help='table dimentions specified in millimteres [WIDTHxHEIGHT or DIAMETER]')
    parser.add_argument('-t', '--topography', type=str, default="./input_data/", help='Input topography data files')
    parser.add_argument('-o', '--output', type=str, default="output.gcode", help='Name of the output gcode file. Will append ".gcode" if not specifed. Will use name for other files')
    parser.add_argument('-r', '--rotation', type=int, choices=[0, 90, 180, 270], default=0, help='How to rotate the map in degress counter-clockwise')
    parser.add_argument('-d', '--debug-dir', type=str, default=None, help='A directory to write debug file to')
    parser.add_argument('-n', '--num-contours', type=int, default=30, help='The number of elevation contours to use')
    args: Arguments = parser.parse_args(argsv)
    
    bbox = GeoBoundingBox(
        args.lat_0, args.lon_0, args.lat_1, args.lon_1
    )

    convert_geography_to_gcode(bbox, args.table_dim, args.rotation, args.topography, args.output, num_contours=args.num_contours, debug_file_dir=args.debug_dir)
    
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
