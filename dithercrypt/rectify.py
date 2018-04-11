#!/usr/bin/python3

import PIL.Image
import numpy as np
import svgwrite

def load_img_binary(fn):
    img = PIL.Image.open(fn)
    arr = np.array(img)

    # Make it black and white
    mask = arr > 128
    arr[mask] = 1
    arr[np.logical_not(mask)] = 0
    return arr

def make_svg(arr, filename):
    arr = np.transpose(arr)
    cell_size = 0.125
    shape = arr.shape
    scale = cell_size

    z = 0.0  # kerf correction
    offset = 4

    dwg = svgwrite.Drawing(filename=filename,
                           size=((shape[0] + 2*offset) * cell_size * svgwrite.inch,
                                 (shape[1] + 2*offset) * cell_size * svgwrite.inch))
    dwg.viewbox(width=shape[0] + 2*offset, height=shape[1] + 2*offset)

    for i in range(shape[0]):
        for j in range(shape[1]):
            if arr[i,j] == 0:
                dwg.add(dwg.rect((i+z+offset, j+z+offset), (1-2*z + 0.01, 1-2*z + 0.01), stroke='none', fill='black'))

    reg_marks = [
            (0, offset, offset, offset),
            (offset, 0, offset, offset),
    ]
    reg_marks.extend([((shape[0] + 2*offset)-x1,y1,(shape[0] + 2*offset)-x2,y2) for x1,y1,x2,y2 in reg_marks])
    reg_marks.extend([(x1,(shape[1] + 2*offset)-y1,x2,(shape[1] + 2*offset)-y2) for x1,y1,x2,y2 in reg_marks])
    
    for x1,y1,x2,y2 in reg_marks:
        dwg.add(dwg.line((x1, y1), (x2, y2), stroke='black', fill='none', stroke_width=0.1))
                
    dwg.save()

def main(infile, outfile):
    arr = load_img_binary(infile)
    make_svg(arr, outfile)

if __name__ == '__main__':
    import sys
    sys.exit(main(*sys.argv[1:]))
