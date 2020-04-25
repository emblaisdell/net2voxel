# Eben Blaisdell 2020

from PIL import Image

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

    def __init__(self, point):
        self.point = point


class VoxelBoundary:
    # voxel
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
                print("Processing Component")
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

    netImage.show()