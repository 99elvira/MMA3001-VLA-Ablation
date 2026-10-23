"""Explicit-path wrist-camera XML editor; defaults to printing a dry run."""
import argparse
import shutil
from pathlib import Path
import xml.etree.ElementTree as ET


def main(argv=None):
    """Inspect or edit one eye_in_hand camera and retain a nominal backup.

    Args:
        argv: CLI arguments: XML path, three --pos numbers, four --quat numbers,
            and optional --apply. Coordinates are absolute local pose values,
            not offsets; use the documented nominal pose when calculating them.

    Raises:
        ValueError: The XML does not contain exactly one eye_in_hand camera.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('xml', type=Path)
    parser.add_argument('--pos', nargs=3, type=float, required=True)
    parser.add_argument('--quat', nargs=4, type=float, required=True)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args(argv)
    tree = ET.parse(args.xml)
    cameras = [c for c in tree.iter('camera') if c.get('name') == 'eye_in_hand']
    if len(cameras) != 1: raise ValueError('Expected exactly one eye_in_hand camera')
    print('Before:', cameras[0].attrib)
    cameras[0].set('pos', ' '.join(map(str,args.pos)))
    cameras[0].set('quat', ' '.join(map(str,args.quat)))
    print('After:', cameras[0].attrib)
    if args.apply:
        backup = args.xml.with_suffix(args.xml.suffix + '.bak')
        if not backup.exists(): shutil.copy2(args.xml, backup)
        tree.write(args.xml, encoding='utf-8', xml_declaration=True)
        print('Saved; backup:', backup)


if __name__ == '__main__':
    main()
