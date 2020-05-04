from SceneObject import SceneObject
from Point3D import Point3D
from Material import Material
from Ray import Ray
from Vector import Vector
import math

class Triangle(SceneObject):
    """ A triangular scene object """
    def __init__(self, material:Material, vertex1:Point3D, vertex2:Point3D, vertex3:Point3D):
        SceneObject.__init__(self, material)
        self.vertex1 = vertex1
        self.vertex2 = vertex2
        self.vertex3 = vertex3
        self.center = Point3D((self.vertex1.vector.x + self.vertex2.vector.x + self.vertex3.vector.x )/3, (self.vertex1.vector.y + self.vertex2.vector.y + self.vertex3.vector.y)/3, (self.vertex1.vector.z + self.vertex2.vector.z + self.vertex3.vector.z)/3)
    
    def intersect(self, ray:Ray):
        # Finding the lines between points
        #U
        ab = Point3D.minus(self.vertex2, self.vertex1)
        
        #V
        ac = Point3D.minus(self.vertex3, self.vertex1)

        #Calc normal
        #n = Point3D(0, 0, 0)
        #a
        #n.x = (ab.y * ac.z) - (ab.z * ac.y)
        #b
        #n.y = (ab.z * ac.x) - (ab.x * ac.z)
        #c
        #n.z = (ab.x * ac.y) - (ab.y * ac.x)

        n = Vector.cross(ab, ac)
        #Calculating the intersection
        d = Vector.dot(n, self.vertex1.vector)
        
        #print(Vector.dot(n.vector, ray.direction))
        if (Vector.dot(n, ray.direction) != 0):
            t = - (Vector.dot(n, ray.origin.vector) + d) / Vector.dot(n, ray.direction)
        else:
            return -999
        
        if t < 0:
            return -999
        else:
            p = Point3D(0,0,0)           
            p.vector.x = ray.origin.vector.x + (t * d)
            p.vector.y = ray.origin.vector.y + (t * d)
            p.vector.z = ray.origin.vector.z + (t * d)
            #Find ABC by taking two of the lines formed from the triangle normalize them and take the cross product
             #Inside-Out
            #Checking left side
            newEdge1 = Point3D.minus(p, self.vertex1)
            E1 = Vector.cross(ab, newEdge1)
            if Vector.dot(n, E1) < 0:
                return -999
            #Checking Right side
            newEdge2 = Point3D.minus(p, self.vertex2)
            E2 = Vector.cross(ac, newEdge2)
            if Vector.dot(n, E2) < 0:
                return -999
            bc = Point3D.minus(self.vertex3, self.vertex2)
            newEdge3 = Point3D.minus(p, self.vertex3)
            E3 = Vector.cross(bc, newEdge3)
            if Vector.dot(n, E3) < 0:
                return -999
            return t