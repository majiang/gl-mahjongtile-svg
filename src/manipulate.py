import dataclasses
import logging
import os
import re

import svgpathtools

logger = logging.getLogger(__name__)

def calculate_bounding_box(path):
    paths, attrs = svgpathtools.svg2paths(path)
    logger.debug(paths)
    logger.debug(attrs)
    min_x, max_x, min_y, max_y = float('inf'), float('-inf'), float('inf'), float('-inf')
    for path in paths:
        logger.debug(path)
        for segment in path:
            logger.debug(segment)
            min_x = min(min_x, segment.start.real, segment.end.real)
            min_y = min(min_y, segment.start.imag, segment.end.imag)
            max_x = max(max_x, segment.start.real, segment.end.real)
            max_y = max(max_y, segment.start.imag, segment.end.imag)
    return min_x, min_y, max_x - min_x, max_y - min_y

def calculate_view_box(path, shrink):
    min_x, min_y, width, height = calculate_bounding_box(path)
    assert min_x == int(min_x)
    assert min_y == int(min_y)
    assert width == int(width)
    assert height == int(height)
    return f'{int(min_x)+shrink} {int(min_y)+shrink} {int(width)-shrink*2} {int(height)-shrink*2}'

@dataclasses.dataclass
class PathModification:
    from_path_d_path: str
    to_path_d_path: str
    shrink: int

def main(
        input_folder: str,
        output_folder: str,
        path_modification: PathModification|None=None
        ):
    shrink = 0
    if path_modification:
        from_path_d = open(path_modification.from_path_d_path).read().strip()
        to_path_d = ' '.join(line.strip() for line in open(path_modification.to_path_d_path))
        shrink = path_modification.shrink

    ret = {}
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if not filename.endswith('.svg'):
            continue
        if filename.endswith('.vert.svg'):
            continue
        if not filename.startswith('u1F'):
            continue
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        logger.info(filename)
        if 'space' in filename or 'uni3000' in filename:
            continue
        view_box = calculate_view_box(input_path, shrink)
        logger.info(view_box)

        if view_box not in ret:
            ret[view_box] = []
        ret[view_box].append(filename.replace('.svg', ''))

        with open(input_path, 'r') as file:
            svg_content = file.read()

        if 'viewBox' in svg_content:
            raise ValueError(f'viewBox already exists: {filename}')

        svg_content = svg_content.replace('<svg', f'<svg viewBox="{view_box}"')
        svg_content = svg_content.replace("><", ">\n<")
        if path_modification:
            svg_content = svg_content.replace(from_path_d, to_path_d)

        with open(output_path, 'w') as file:
            file.write(svg_content)

    logger.info("\n" + "\n".join(
        vb + ": " + ", ".join(fns)
        for (vb, fns) in ret.items()
    ))

logging.basicConfig(level=logging.INFO, format="%(lineno)d\t%(message)s")
for shrink in (10, 20):
    main(
        "original/woff-svg",
        f"svg/from-woff/frame-{30-shrink}",
        PathModification(
        from_path_d_path="value/frame.original-30.path-d",
        to_path_d_path=f"value/frame.{30-shrink}.path-d",
        shrink=shrink))

main("original/woff-svg", "svg/from-woff/original")
