#!/usr/bin/python3

import secrets
import PIL.Image
import numpy as np

def load_img(fn):
    img = PIL.Image.open(fn)
    arr = np.array(img)

    # Make it black and white
    mask = arr > 128
    arr[mask] = 1
    arr[np.logical_not(mask)] = 0
    return arr

def randarray(shape):
    return np.random.randint(0, 2, shape, dtype.np.uint8)

PIXSHAPE = (2,2)

def set_pix(dest, subpix, x, y):
    dest[x*PIXSHAPE[0]:(x+1)*PIXSHAPE[0], y*PIXSHAPE[1]:(y+1)*PIXSHAPE[1]] = subpix

BASIC_PIX0 = np.array(((1,0),(0,1)), dtype=np.uint8)
BASIC_PIX1 = 1-BASIC_PIX0
BASIC_PIXES = [BASIC_PIX0, BASIC_PIX1]

def make_mask(width, height, out):
    arr = np.zeros((width, height), dtype=np.uint8)
    for i in range(width):
        for j in range(height):
            arr[i][j] = 255*secrets.randbits(1)
    PIL.Image.fromarray(arr).save(out)

def basic_expand(source):
    shape = source.shape

    bigshape = (shape[0]*PIXSHAPE[0], shape[1]*PIXSHAPE[1])
    left = np.zeros(bigshape, dtype=np.uint8)
    right = np.zeros(bigshape, dtype=np.uint8)

    for i in range(shape[0]):
        for j in range(shape[1]):
            val = source[i,j] == 0
            set_pix(left, BASIC_PIXES[val], i, j)
            set_pix(right, BASIC_PIXES[val ^ 1], i, j)

    return (left, right)

def encrypt(source):
    shape = source.shape

    bigshape = (shape[0]*PIXSHAPE[0], shape[1]*PIXSHAPE[1])
    left = np.zeros(bigshape, dtype=np.uint8)
    right = np.zeros(bigshape, dtype=np.uint8)

    for i in range(shape[0]):
        for j in range(shape[1]):
            r = secrets.randbits(1)
            set_pix(left, BASIC_PIXES[r], i, j)
            set_pix(right, BASIC_PIXES[r ^ source[i,j] ^ 1], i, j)

    return (left, right)

def make_cut_mask(arr, filename):
    import svgwrite

    cell_size = 0.125
    shape = arr.shape
    scale = cell_size

    z = 0.15

    vertstrokes = []
    horzstrokes = []

    dwg = svgwrite.Drawing(filename=filename,
                           size=(shape[0] * cell_size * svgwrite.inch,
                                 shape[1] * cell_size * svgwrite.inch))
    dwg.viewbox(width=shape[0], height=shape[1])

    rects = True

    for i in range(shape[0]):
        for j in range(shape[1]):
            if arr[i,j] != 0:
                if rects:
                    dwg.add(dwg.rect((i+z, j+z), (1-2*z, 1-2*z), stroke='black', fill='none', stroke_width=0.1))
                else:
                    vertstrokes.append(((i+z, j+z), (i+z, j+1-z)))
                    vertstrokes.append(((i+1-z, j+z), (i+1-z, j+1-z)))
                    horzstrokes.append(((i+z, j+z), (i+1-z, j+z)))
                    horzstrokes.append(((i+z, j+1-z), (i+1-z, j+1-z)))

    vertstrokes.sort(key=lambda s: s[0])
    horzstrokes.sort(key=lambda s: (s[0][1], s[0][0]))

    for s in vertstrokes:
        dwg.add(dwg.line((s[0][0], s[0][1]),
                         (s[1][0], s[1][1]),
                         stroke='blue', fill='none', stroke_width=0.1))

    for s in horzstrokes:
        dwg.add(dwg.line((s[0][0], s[0][1]),
                         (s[1][0], s[1][1]),
                         stroke='red', fill='none', stroke_width=0.1))

    dwg.save()

def main(cmd, *args):
    if cmd == 'make_cut_mask':
        arr = load_img(args[0])
        (left,right) = basic_expand(arr)
        make_cut_mask(left, '%s_positive.svg' % args[1])
        make_cut_mask(right, '%s_negative.svg' % args[1])
        return 0
    elif cmd == 'make_png_mask':
        arr = load_img(args[0])
        (left,right) = basic_expand(arr)
        PIL.Image.fromarray(left*255).save('%s_positive.png' % args[1])
        PIL.Image.fromarray(right*255).save('%s_negative.png' % args[1])
        return 0
    elif cmd == 'make_mask':
        make_mask(int(args[0]), int(args[1]), args[2])
        return 0
    else:
        print('Bad command %s' % cmd)
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main(*sys.argv[1:]))
