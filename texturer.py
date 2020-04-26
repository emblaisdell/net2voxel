# Eben Blaisdell 2020

from solid import *

def scadFromTexturedBoxes(texturedBoxes, outFilename):
    obj = union()([ translate(tBox.box.corner.tuple())(cube(tBox.box.size.tuple())) for tBox in texturedBoxes])

    scad_render_to_file(obj, outFilename)
