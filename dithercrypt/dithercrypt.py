#!/usr/bin/python3

import secrets
import PIL.Image
import numpy as np

def randfloat():
    return secrets.randbits(32) / (1<<32)

def load_img(fn):
    """Totally incorrect but kind of good enough."""
    img = PIL.Image.open(fn).convert('L')
    arr = np.array(img)
    arr = arr.astype(float) / 255
    return arr

def save_img(img, fn):
    PIL.Image.fromarray(img).save(fn)

def encrypt2(img):
    shape = img.shape
    
    out1 = np.zeros(shape, dtype=np.uint8)
    out2 = np.zeros(shape, dtype=np.uint8)

    for i in range(shape[0]):
        for j in range(shape[1]):
            o1 = secrets.randbits(1)
            if randfloat() < img[i,j]:
                o2 = o1
            else:
                o2 = 1 - o1

            out1[i,j] = o1 * 255
            out2[i,j] = o2 * 255

    return (out1, out2)

def steg2(clear1, clear2, secret):
    shape = clear1.shape
    if shape != clear2.shape or shape != secret.shape:
        raise TypeError('all three images must have the same shape')
    
    out1 = np.zeros(shape, dtype=np.uint8)
    out2 = np.zeros(shape, dtype=np.uint8)

    for i in range(shape[0]):
        for j in range(shape[1]):
            x = secret[i,j] * 0.25
            a = clear1[i,j] * 0.25 + 0.25
            b = clear2[i,j] * 0.25 + 0.25
            p11 = x
            p01 = b-x
            p10 = a-x
            p00 = 1 - p11 - p01 - p10
            assert p00 > -0.0001 and p00 < 1.0001

            r = randfloat()
            if r < p00:
                o1, o2 = 0, 0
            elif r - p00 < p01:
                o1, o2 = 0, 1
            elif r - p00 - p01 < p10:
                o1, o2 = 1, 0
            else:
                o1, o2 = 1, 1

            out1[i,j] = o1 * 255
            out2[i,j] = o2 * 255

    return (out1, out2)

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