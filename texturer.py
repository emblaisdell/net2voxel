# Eben Blaisdell 2020

from solid import *

def scadFromBox(box):
    return translate(box.corner.tuple())(cube(box.size.tuple()))

def texturedModel(boxes, voxelBoundaries, depthFunc):

    boxModels = []

    for box in boxes:
        positives = []
        negatives = []

        for boundary in voxelBoundaries:
            if boundary.voxel.point in box:
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

        boxModels.append(scadFromBox(box) + union()(positives) - union()(negatives))

    return union()(boxModels)