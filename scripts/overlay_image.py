#!/usr/bin/env python3
import argparse
import csv
import json
import os
from io import BytesIO

from desipoint.io import load_image
from desipoint.image import download_image, create_image

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Required arguments
    parser.add_argument("time", help="image time, in ISO-8601 format")

    parser.add_argument("-mw", "--milkyway", help="toggle the milky way", action="store_true")
    parser.add_argument("-ep", "--ecliptic", help="toggle the ecliptic", action="store_true")
    parser.add_argument("-s", "--survey", help="toggle the survey area", action="store_true")
    parser.add_argument("-p", "--pointing", help="toggle the telescope pointing", action="store_true")
    parser.add_argument("-a", "--all", help="toggle everything", action="store_true")

    parser.add_argument("-f", "--file", help="where to load image from", type=str, required=False)

    args = parser.parse_args()

    if args.file:
        loaded_image = load_image(args.file, args.time)
    else:
        loaded_image = None

    if args.all:
        fig, date, dpi = create_image(args.time, loaded_image, True, True, True, True)
    else:
        fig, date, dpi = create_image(args.time, loaded_image, args.milkyway, args.ecliptic, args.survey, args.pointing)

    fig.savefig(f"{date}.png", dpi=dpi)

