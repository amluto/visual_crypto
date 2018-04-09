#!/usr/bin/python3

import secrets
import PIL.Image
import numpy as np
import sys

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

    # Scale the images into range
    contrast = 0.25
    secret = secret * contrast
    clear1 = clear1 * (0.5 - contrast) + contrast
    clear2 = clear2 * (0.5 - contrast) + contrast

    for i in range(shape[0]):
        for j in range(shape[1]):
            x = secret[i,j]
            a = clear1[i,j]
            b = clear2[i,j]
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

            # Propagate the errors using the Floyd-Steinberg kernel
            #def prop(mat, di, dj, err):
            #    if i+di < mat.shape[0] and 0 <= j+dj < mat.shape[1]:
            #        mat[i+di][j+dj] += 0.25*err

            #prop(clear1, 0,  1, (a-o1) * (7/16))
            #prop(clear1, 1, -1, (a-o1) * (3/16))
            #prop(clear1, 1,  0, (a-o1) * (5/16))
            #prop(clear1, 1,  1, (a-o1) * (1/16))

    return (out1, out2)

def draw(dist):
    total_p = 0.0
    for prob, _ in dist:
        assert prob > -0.0001 and prob < 1.0001
        total_p += prob
    assert total_p > -0.0001 and total_p < 1.0001

    r = randfloat()

    for prob, outcome in dist:
        if r < prob:
            return outcome
        r -= prob

    # Fallback in case of rounding error
    return dist[-1][1]

def encrypt3(img_ab, img_ac, img_bc):
    shape = img_ab.shape
    if shape != img_ac.shape or shape != img_bc.shape:
        raise TypeError('all three images must have the same shape')

    out_a = np.zeros(shape, dtype=np.uint8)
    out_b = np.zeros(shape, dtype=np.uint8)
    out_c = np.zeros(shape, dtype=np.uint8)

    # Scale the images into range
    contrast = 1/6
    img_ab = img_ab * contrast
    img_ac = img_ac * contrast
    img_bc = img_bc * contrast

    for i in range(shape[0]):
        for j in range(shape[1]):
            ab = img_ab[i,j]
            ac = img_ac[i,j]
            bc = img_bc[i,j]

            o1, o2, o3 = draw([
                (0, (1,1,1)),
                (ab + ac + bc, (0,0,0)),
                (bc, (0,1,1)),
                (ac, (1,0,1)),
                (ab, (1,1,0)),
                (1/3 - ab - ac, (1,0,0)),
                (1/3 - ab - bc, (0,1,0)),
                (1/3 - ac - bc, (0,0,1))
            ])

            out_a[i,j] = o1 * 255
            out_b[i,j] = o2 * 255
            out_c[i,j] = o3 * 255

    return (out_a, out_b, out_c)

def encrypt4(img_ab, img_ac, img_ad, img_bc, img_bd, img_cd):
    shape = img_ab.shape
    if shape != img_ac.shape or shape != img_ad.shape or shape != img_bc.shape or shape != img_bd.shape or shape != img_cd.shape:
        raise TypeError('all six images must have the same shape')

    out_a = np.zeros(shape, dtype=np.uint8)
    out_b = np.zeros(shape, dtype=np.uint8)
    out_c = np.zeros(shape, dtype=np.uint8)
    out_d = np.zeros(shape, dtype=np.uint8)

    # Scale the images into range
    contrast = 1/12
    img_ab = img_ab * contrast
    img_ac = img_ac * contrast
    img_ad = img_ad * contrast
    img_bc = img_bc * contrast
    img_bd = img_bd * contrast
    img_cd = img_cd * contrast

    for i in range(shape[0]):
        for j in range(shape[1]):
            ab = img_ab[i,j]
            ac = img_ac[i,j]
            ad = img_ad[i,j]
            bc = img_bc[i,j]
            bd = img_bd[i,j]
            cd = img_cd[i,j]

            o1, o2, o3, o4 = draw([
                (ab + ac + ad + bc + bd + cd, (0,0,0,0)),
                (ab, (1,1,0,0)),
                (ac, (1,0,1,0)),
                (ad, (1,0,0,1)),
                (bc, (0,1,1,0)),
                (bd, (0,1,0,1)),
                (cd, (0,0,1,1)),
                (1/4 - ab - ac - ad, (1,0,0,0)),
                (1/4 - ab - bc - bd, (0,1,0,0)),
                (1/4 - ac - bc - cd, (0,0,1,0)),
                (1/4 - ad - bd - cd, (0,0,0,1)),
            ])

            out_a[i,j] = o1 * 255
            out_b[i,j] = o2 * 255
            out_c[i,j] = o3 * 255
            out_d[i,j] = o4 * 255

    return (out_a, out_b, out_c, out_d)

commands = [
    ('encrypt2', 2, 2, encrypt2),
    ('steg2', 3, 2, steg2),
    ('encrypt3', 3, 3, encrypt3),
    ('encrypt4', 6, 4, encrypt4),
]

def main(cmd, *args):
    for c, in_arity, out_arity, func in commands:
        if cmd == c:
            break
    else:
        print('Usage: %s [%s] ...' % (sys.argv[0], '|'.join([c for c, _, _, _ in commands])))
        return 1

    if len(args) != in_arity + out_arity:
        print('Usage: %s %s (%d input images) (%d output images)' % (sys.argv[0], cmd, in_arity, out_arity))
        return 1

    in_imgs = [load_img(filename) for filename in args[0:in_arity]]
    out_imgs = func(*in_imgs)

    for img, name in zip(out_imgs, args[in_arity:]):
        save_img(img, name)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(main(None))
    sys.exit(main(*sys.argv[1:]))
