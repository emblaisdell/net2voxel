# Eben Blaisdell 2020

from PIL import Image
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

from net2voxel import Vector, voxelBoundariesFromNetImage

def main():
    net = Image.open("./images/creeper_net.png")

    voxelBoundaries = voxelBoundariesFromNetImage(net)

    print("Found", len(voxelBoundaries), "boundaries")

    printVoxelBoundaries(voxelBoundaries)

def printVoxelBoundaries(voxelBoundaries):
    fig = plt.figure()
    ax = fig.gca(projection='3d')

    X = []
    Y = []
    Z = []

    i = 0
    simplicies = []

    for voxelBoundary in voxelBoundaries:
        position = voxelBoundary.voxel.point
        normal = voxelBoundary.normal
        parallel1 = Vector(normal.y, normal.z, normal. x)
        parallel2 = Vector(normal.z, normal. x, normal.y)

        corner0 = position + 0.5 * ( normal + parallel1 + parallel2)
        corner1 = position + 0.5 * ( normal + parallel1 - parallel2)
        corner2 = position + 0.5 * ( normal - parallel1 - parallel2)
        corner3 = position + 0.5 * ( normal - parallel1 + parallel2)

        # print(pos)

        X += [corner0.x, corner1.x, corner2.x, corner3.x]
        Y += [corner0.y, corner1.y, corner2.y, corner3.y]
        Z += [corner0.z, corner1.z, corner2.z, corner3.z]

        simplicies += [[i+0, i+1, i+2], [i+0, i+3, i+2]]

        i += 4

    ax.plot_trisurf(X, Y, Z, triangles=simplicies, shade=False)

    plt.show()


main()