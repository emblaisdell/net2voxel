# Eben Blaisdell 2020

from solid import *

def scadFromBoxes(boxes):
    obj = union()([ translate(box.corner.tuple())(cube(box.size.tuple())) for box in boxes])

    return obj

def texturedModel(boxes, voxelBoundaries, depthFunc):
    positives = []
    negatives = []

    for boundary in voxelBoundaries:
        value = depthFunc(boundary.color)
        if(value < 0):
            negatives.append(
                translate((boundary.voxel.point + ((1.0 + value) * boundary.normal)).tuple())(
                    cube(1)
                )
            )
        if(value > 0):
            positives.append(
                translate((boundary.voxel.point + (value * boundary.normal)).tuple())(
                    cube(1)
                )
            )

    return scadFromBoxes(boxes) + union()(positives) - union()(negatives)