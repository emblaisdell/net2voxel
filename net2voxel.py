# Eben Blaisdell 2020

from collections import defaultdict
import copy

class Vector:
    # x, y, z

    def __init__(self, x, y, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Vector(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z
        )

    def __sub__(self, other):
        return self + (-other)

    def __neg__(self):
        return Vector(
            -self.x,
            -self.y,
            -self.z
        )

    def __rmul__(self, scalar):
        return Vector(
            scalar * self.x,
            scalar * self.y,
            scalar * self.z
        )

    def __eq__(self, other):
        return self.x == other.x and \
            self.y == other.y and \
            self.z == other.z

    def __repr__(self):
        return "Vector(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ")"

    @staticmethod
    def cross(v1, v2):
        return Vector(
            v1.y * v2.z - v1.z * v2.y,
            v1.z * v2.x - v1.x * v2.z,
            v1.x * v2.y - v1.y * v2.x
        )

    def rotatedAround(self, axis):
        """ Rotation of the vector about the axis by an angle of 90 degrees"""
        return Vector.cross(axis, self)

    def tuple(self):
        return (self.x, self.y, self.z)

Vector.CARD_DIRECTIONS = [
    Vector(1,0,0),
    Vector(-1,0,0),
    Vector(0,1,0),
    Vector(0,-1,0),
    Vector(0,0,1),
    Vector(0,0,-1)
]


class Color:
    # r, g, b

    def __init__(self, r, g, b, a):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def isSolid(self):
        return self.a >= 250

    def isTransparent(self):
        return self.a <= 5

    def isTranslucent(self):
        return (not self.isSolid()) and (not self.isTransparent())

    def rgbaTuple(self):
        return (self.r, self.g, self.b, self.a)

    def rgbTuple(self):
        return (self.r, self.g, self.b)

    def normedRgbTuple(self):
        return (self.r / 255, self.g / 255, self.b / 255)

class Voxel:
    # point
    # boundaries

    def __init__(self, point, boundaries=[]):
        self.point = point
        self.boundaries = boundaries


class VoxelBoundary:
    # voxel XXX: circular references?
    # normal
    # color XXX: maybe refactor to texture?

    def __init__(self, voxel, normal, color):
        self.voxel = voxel
        self.normal = normal
        self.color = color

class NetPixel:
    # color
    # processed
    def __init__(self, color, processed = False):
        self.color = color
        self.processed = processed


class Box:
    # corner (with minimal x,y,z coordinates), size as (l,w,h) vector
    def __init__(self, corner, size):
        self.corner = corner
        self.size = size

    def __contains__(self, vec):
        minCorner = self.corner
        maxCorner = self.corner + self.size

        return vec.x in range(minCorner.x, maxCorner.x) and \
            vec.y in range(minCorner.y, maxCorner.y) and \
            vec.z in range(minCorner.z, maxCorner.z)

def numRotationsByColor(color):
    maxChannel = max(color.r,color.g,color.b)
    if maxChannel == color.r:
        return -1
    if maxChannel == color.g:
        return 0
    if maxChannel == color.b:
        return 1
    return 0

class VoxelBoundaryProcessingJob:
    def __init__(self,
                 planarPosition,
                 planarForward=Vector(1, 0),
                 position=Vector(0, 0, 0),
                 normal=Vector(0, 0, 1),
                 forward=Vector(1, 0, 0)
            ):
        self.planarPosition = planarPosition
        self.planarForward = planarForward
        self.position = position
        self.normal = normal
        self.forward = forward

def voxelBoundariesFromNetImage(netImage):
    """ Take in PIL image and return array of colored voxel boundaries """

    netWidth = netImage.width
    netHeight = netImage.height

    loadedImage = netImage.load()

    netPixels = [[NetPixel(Color(*loadedImage[i,j])) for j in range(netHeight)] for i in range(netWidth)]
    voxelBoundaries = []

    jobQueue = []

    # process all pixels
    for i in range(netWidth):
        for j in range(netHeight):
            if netPixels[i][j].color.isSolid() and not netPixels[i][j].processed:
                print("Processing Voxel Boundary Component")
                jobQueue.append(VoxelBoundaryProcessingJob(Vector(i, j)))
                netPixels[i][j].processed = True

                while len(jobQueue) > 0:
                    # get new job
                    job = jobQueue.pop()
                    # print("num left = ", len(jobQueue))

                    # get current pixel
                    netPixel = netPixels[job.planarPosition.x][job.planarPosition.y]

                    # add new 3d voxel boundary
                    voxelBoundaries.append(
                        VoxelBoundary(
                            Voxel(job.position),
                            job.normal,
                            netPixel.color
                        )
                    )

                    searchDirection = job.planarForward
                    moveDirection = job.forward
                    for directionIndex in range(4):
                        totalRotation = 0
                        searchPoint = job.planarPosition + searchDirection
                        foundUnprocessed = False

                        while True:
                            if not (searchPoint.x in range(len(netPixels)) and searchPoint.y in range(
                                    len(netPixels[0]))):
                                break

                            searchPixel = netPixels[searchPoint.x][searchPoint.y]

                            if searchPixel.color.isSolid():
                                foundUnprocessed = not searchPixel.processed
                                break

                            if searchPixel.color.isTransparent():
                                break

                            if searchPixel.color.isTranslucent():
                                totalRotation += numRotationsByColor(searchPixel.color)

                            searchPoint = searchPoint + searchDirection

                        if foundUnprocessed:
                            totalRotation = totalRotation % 4

                            if totalRotation == 0:  # go straight
                                newPosition = job.position + moveDirection
                                newNormal = job.normal
                                newForward = moveDirection

                            if totalRotation == 1:  # turn up
                                newPosition = job.position + moveDirection + job.normal
                                newNormal = -moveDirection
                                newForward = job.normal

                            if totalRotation == 2:  # turn back on yourself
                                newPosition = job.position + job.normal
                                newNormal = -job.normal
                                newForward = -moveDirection

                            if totalRotation == 3:  # turn down
                                newPosition = job.position
                                newNormal = moveDirection
                                newForward = -job.normal

                            jobQueue.append(VoxelBoundaryProcessingJob(
                                searchPoint,
                                searchDirection,
                                newPosition,
                                newNormal,
                                newForward
                            ))
                            netPixels[searchPoint.x][searchPoint.y].processed = True

                        searchDirection = searchDirection.rotatedAround(Vector(0, 0, 1))
                        moveDirection = moveDirection.rotatedAround(job.normal)

    return voxelBoundaries


def voxelBoundaryBoundingBox(voxelBoundaries):
    """ Take in array of voxel boundaries and return the bounding box of """

    minCorner = copy.copy(voxelBoundaries[0].voxel.point)
    maxCorner = copy.copy(voxelBoundaries[0].voxel.point)

    for voxelBoundary in voxelBoundaries:
        if voxelBoundary.voxel.point.x < minCorner.x:
            minCorner.x = voxelBoundary.voxel.point.x
        if voxelBoundary.voxel.point.x >= maxCorner.x:
            maxCorner.x = voxelBoundary.voxel.point.x + 1
        if voxelBoundary.voxel.point.y < minCorner.y:
            minCorner.y = voxelBoundary.voxel.point.y
        if voxelBoundary.voxel.point.y >= maxCorner.y:
            maxCorner.y = voxelBoundary.voxel.point.y + 1
        if voxelBoundary.voxel.point.z < minCorner.z:
            minCorner.z = voxelBoundary.voxel.point.z
        if voxelBoundary.voxel.point.z >= maxCorner.z:
            maxCorner.z = voxelBoundary.voxel.point.z + 1

    return Box(minCorner, maxCorner - minCorner)


def voxelsFromVoxelBoundaries(voxelBoundaries):
    """ Take in the boundary of a voxel model, as an array of voxel boundaries
        and return the voxel model as an array of voxels """

    voxels = []

    bbox = voxelBoundaryBoundingBox(voxelBoundaries)

    print("Bounding Box", bbox.corner, bbox.size)

    size = bbox.size

    hasBeenProcessed = [[[False for z in range(size.z)] for y in range(size.y)] for x in range(size.x)]

    voxelBoundariesByLocation = defaultdict(lambda:[])
    for voxelBoundary in voxelBoundaries:
        voxelBoundariesByLocation[voxelBoundary.voxel.point.tuple()].append(voxelBoundary)

    positionQueue = []

    for voxelBoundary in voxelBoundaries:
        point = voxelBoundary.voxel.point
        if not hasBeenProcessed[point.x][point.y][point.z]:
            print("Processing Voxel Component")
            hasBeenProcessed[point.x][point.y][point.z] = True
            positionQueue.append(point)

            while len(positionQueue) > 0:
                jobPoint = positionQueue.pop()

                boundaries = voxelBoundariesByLocation[jobPoint.tuple()]

                newVoxel = Voxel(jobPoint, boundaries)
                for boundary in boundaries:
                    boundary.voxel = newVoxel
                voxels.append(newVoxel)

                for direction in Vector.CARD_DIRECTIONS:
                    isBoundaryDirection = False
                    for boundary in boundaries:
                        if boundary.normal == direction:
                            isBoundaryDirection = True
                            break

                    if not isBoundaryDirection:
                        newPoint = jobPoint + direction
                        if not (newPoint in bbox):
                            raise Exception("Voxel Boundaries are not manifold!")
                        if not hasBeenProcessed[newPoint.x][newPoint.y][newPoint.z]:
                            hasBeenProcessed[newPoint.x][newPoint.y][newPoint.z] = True
                            positionQueue.append(newPoint)

    return voxels

