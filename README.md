# Dithercrypt

Dithercrypt is an approach to visual cryptography that works by jointly
dithering several images so that the images are revealed when the
output is printed on transparency film and overlaid.  The
[dithercrypt program](dithercrypt/dithercrypt.py) supports
four variants:

* "encrypt2" encrypts single image into two output grids.  Taken
  individually, the grids are random noise.  If overlaid, the image is
  revealed.  Black areas of the secret image will appear entirely black;
  white areas will be half black and half white; and gray areas will
  be more than half black and less than half white.

* "encrypt3" encrypts three images into three output grids.  Taken
  individually, the grids are random noise.  If two grids are
  overlaid, one of the three input images will be revealed.  Black
  areas of the secret image will appear entirely black; white areas
  will appear 1/6 white and 5/6 black; and gray areas will be in
  between.  be more than half black and less than half white.

* "encrypt4" is like "encrypt3" except with six inputs and four outputs.
  White areas are 1/12 white and 11/12 black.

* "steg2" encrypts three images and produces two outputs.  Each output,
  by itself, looks like one of the first two inputs.  Black areas are
  25% white and 75% black; white areas are 50% white and 50% black;
  and gray areas are in between.  When overlaid, the secret image
  is revealed.  Black areas are black; white areas are 25% white;
  and gray areas are in between.  The 25% cutoff is tunable, but the
  50% is fixed by the statistics of the process.

The dithercrypt program will work if given grayscale input, but the
results will be incorrect, as it does not currently correct for
gamma.

To print the results, you'll need to use a program that will give
pixelated output instead of trying to interpolate.

Example usage:
```
python /path/to/dithercrypt.py encrypt2 /path/to/inputimage.jpg output1.jpg output2.jpg
```

# Visual cryptography workshop

This is a placeholder.  It's very awkward to use right now.

# License

MIT
