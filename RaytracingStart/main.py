""" 
To run this program do the following:

First, install the pip pacakages by running the following
python -m pip install -r requirements.txt

Then run this main file by running the following
python main.py

Note that this program is built to run in python 3

If you machine defaults to running python 2 when you run python
from your shell/command line, it won't work

You may need to run
python3 main.py to get the program to run


Written by B. Ricks, @bricksphd, 

Professor at unomaha.edu

MIT License, 2020

"""


import png
import math
import random
from datetime import datetime

from Frame import Frame
from Vector import Vector
from Point3D import Point3D
from Ray import Ray
from AreaLight import AreaLight
from Camera import Camera
from DirectionalLight import DirectionalLight
from Light import Light
from Material import Material
from OrthographicCamera import OrthographicCamera
from PerspectiveCamera import PerspectiveCamera
from PointLight import PointLight
from SceneObject import SceneObject
from Sphere import Sphere
from SpotLight import SpotLight
from Triangle import Triangle





print("Starting our ray tracer")
start = datetime.now()

# Grab the enivornment image
background = png.Reader(filename="field.png")

# Grab the pixels in an array
# It's sligthly tricky because color png images may be packid as 3-byte pixels or 4-byte pixels (w/transparency)
# https://stackoverflow.com/questions/138250/how-to-read-the-rgb-value-of-a-given-pixel-in-python/50894365
backgroundWidth, backgroundHeight, backgroundRows, backgroundMeta =  background.read_flat()
backgroundPixelByteWidth = 4 if backgroundMeta['alpha'] else 3



# Minimum for a ray tracer
# A frame to render to
# A camera
# A light
# An object to render


frame = Frame(256, 256)

cameraOrigin = Point3D(0, 0, 1)
origin = Point3D(0, 0, 0)
cameraLookAt = Point3D(0, 0, 0)
cameraUp = Vector(0, 1, 0)
cameraBackgroundColor = Vector(0, 0, 0)
# convert 45 degrees to radians. Should result in pi/4 ~= .785
fov = 45 / 360 * math.pi * 2
raysPerPixel = 1
focusPoint = 0

camera = PerspectiveCamera(cameraOrigin, cameraLookAt, cameraUp,
                           cameraBackgroundColor, raysPerPixel, focusPoint, fov)

lightDirection = Vector(0, -1, 0)
lightColor = Vector(255, 255, 255)

light = DirectionalLight(lightColor, 1, lightDirection)
light2 = DirectionalLight(Vector(0, 0, 255), 1, Vector(1, 0, 0))
light3 = DirectionalLight(Vector(0, 255, 0), 1, Vector(0, 0, 1))
sphereCenter = Point3D(0,0,-.2)
sphereRadius = .5
sphereMaterialColor = Vector(255, 0, 0)
sphereMaterialSpecularColor = Vector(255, 255, 255)
sphereMaterialSpecularStrength = 1

sphereMaterial = Material(
    sphereMaterialColor, sphereMaterialSpecularColor, sphereMaterialSpecularStrength,.2)

sphereMaterial2 = Material(
    Vector(255, 255, 255), sphereMaterialSpecularColor, sphereMaterialSpecularStrength, .5)

sphereMaterial3 = Material(
    Vector(0, 255, 0), sphereMaterialSpecularColor, sphereMaterialSpecularStrength, 0)

triangleMaterial = Material(
    sphereMaterialColor, 0, 0,.2)

sphere = Sphere(sphereMaterial, sphereCenter, sphereRadius)
sphere2 = Sphere(sphereMaterial2, Point3D(.2, .2, .5), .1)
sphere3 = Sphere(sphereMaterial2, Point3D(-.2, -.1, .5), .1)
sphere4 = Sphere(sphereMaterial3, Point3D(0, -.1, .5), .1)

triangle = Triangle(triangleMaterial, Point3D(.2, .2, .5), Point3D(-.2, -.1, .5), Point3D(.6, -.1, .5))
lights = [light]
#objects = [sphere, sphere2, sphere3, sphere4]
objects =[triangle, sphere3]
#Now loop over every pixel in our frame

#For every pixel
#Figure out where in camera space that pixel is
#Then figure out where in world space that pixel is
#Then shoot a ray from the world space origin of the camera to that world space location
#Then loop over each object in the scene
#For ever object that ray collides with
#Find out which one has the closest collission
#That's our hit
#If we don't have a hit, return the background color
#Then calculate the color based on the direction to the right

# Ray - Ray we're sending out
# orgin object - Object we don't want to self-intersect with
def hitDistance(ray, originObject):
    closestHit = float("inf")
    closestObjectIndex = -1
    for object in objects:
        if object != originObject:
            #print(type(object))
            t = object.intersect(ray)
            if t >= 0 and t < closestHit:
                closestHit = t
                closestObjectIndex = objects.index(object)
    return [closestHit, closestObjectIndex]

def getColor(ray, originObject, recursionLimit):
    if recursionLimit <= 0:
        return Vector(0,0,0)

    [t, collisionObjectIndex] = hitDistance(ray, originObject)
    if collisionObjectIndex != -1:
        object = objects[collisionObjectIndex]
        collisionPoint = Point3D.fromVector(ray.direction.toScaled(t).plus(camera.origin.vector))
        normalDirection = collisionPoint.minus(object.center)
        normal = normalDirection.toNormalized()

        ambient = Vector(30, 30, 30)
        diffuse = Vector(0,0,0)

        for light in lights:
            toLight = light.direction.toScaled(-1)
            [t2, shadowObjectIndex] = hitDistance(Ray(collisionPoint, toLight), object)
            if shadowObjectIndex == -1:
                lightDiffuse = Vector(0,0,0)
                product = toLight.dot(normal)
                if product < 0:
                    product = 0
                lightDiffuse = light.color.toScaled(product)
                lightDiffuse = lightDiffuse.simpleMultiply(object.material.diffuseColor)
                lightDiffuse = lightDiffuse.toScaled(1/255)
                diffuse = diffuse.plus(lightDiffuse)  


            # Needs:
            # Normal
            # Incoming direction (ray.direction)
            # Want reflective direction
            reflectiveDirection = ray.direction.toScaled(-1).reflectAbout(normal)          
            reflectionRay = Ray(collisionPoint, reflectiveDirection)
            reflectionColor = getColor(reflectionRay, object, recursionLimit - 1)

        color = ambient.plus(diffuse.toScaled(1 - object.material.reflectivity)).plus(reflectionColor.toScaled(object.material.reflectivity))                   
        
        return color
    else:
        return sampleBackground(ray.direction)

def sampleBackground(direction):
   a1 = math.atan2(direction.z, direction.x)
   b1 = math.atan2(-direction.y, direction.z)
   a = (a1 + math.pi)/(2*math.pi)
   b = (b1 + math.pi)/(2*math.pi)
   i = math.floor(a*backgroundWidth)
   j = math.floor(b*backgroundHeight)
   pixelPosition = i + j * backgroundWidth
   backgroundColor = backgroundRows[pixelPosition * backgroundPixelByteWidth:(pixelPosition+1)*backgroundPixelByteWidth]
   return Vector(backgroundColor[0], backgroundColor[1], backgroundColor[2])
    


for y in range(frame.height):
    for x in range(frame.width):
        if x == 123 and y == 159:
            print("debug")
        #Convert from screen space to camera space
        #Then from frame camera space to world space
        yPercent = -1 * (y / frame.height * 2 - 1) #-1 because images have y down
        xPercent = x / frame.width * 2 -1
        #yPercent and xPercent are now in [-1,1]
        #Now we multiply by the camera width and height at the lookAt point
        #To do that we first get the distance from the camera origin and the camera destination
        #This becomes the hyponetus for our triangle calculations

        toLookAt = camera.lookAt.minus(camera.origin)
        #toLookAt is a vector from the origin to the look at point.
        #We need this to calculate the camera right vector

        distance = toLookAt.length()
        toLookAtNormalized = toLookAt.toNormalized()
        width = math.cos(camera.fov) * distance
        height = math.cos(camera.fov) * distance
        #width and height should be the same unless we set different fovs for width and height

        # TODO: This should be toLookAtNormalize
        cameraRight = toLookAtNormalized.cross(camera.up)
        rightWorld = cameraRight.toScaled(width * xPercent)
        upWorld =  camera.up.toScaled(height * yPercent)
        pixelLookAt = Point3D.fromVector(upWorld.plus(rightWorld))
        #We now have our world look at points
        #We need to generate our look at ray and NORMALIZE IT!!!
        ray = Ray(camera.origin, pixelLookAt.minus(camera.origin).toNormalized())

        # jitter the ray

        r = 0
        g = 0
        b = 0
        samples = 5
        for i in range(samples):
            ray2 = Ray(Point3D.fromVector(ray.origin.vector.clone()), ray.direction.clone())
            ray2.direction.x += (random.random() - .5)*2*width/frame.width
            ray2.direction.y += (random.random() - .5)*2*height/frame.height
            ray2.direction = ray2.direction.toNormalized()
            color = getColor(ray2, None, 4)
            r += color.x
            g += color.y
            b += color.z
        r /= samples
        g /= samples
        b /= samples


        frame.set(x,y, Vector(r,g,b))

        

##Write the buffer out to a file

#Open the output file in binary mode
f = open('./saved.png', 'wb')

#Create a write object
w = png.Writer(frame.width, frame.height, greyscale=False)

#Write to the open file
w.write_array(f, frame.buffer)

#Close the file
f.close()

print("Finished rendering the file")
end = datetime.now()

print("Run time: " + str(end - start))