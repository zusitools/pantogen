from . import vector
import math

# Taken from the GeoSolver package

def tol_lt(a, b):
    return b-a > 1e-6

def tol_gt(a, b):
    return a-b > 1e-6

def tol_eq(a, b):
    return abs(a-b) <= 1e-6

def cc_int(p1, r1, p2, r2):
    """
    Intersect circle (p1,r1) circle (p2,r2)
    where p1 and p2 are 2-vectors and r1 and r2 are scalars
    Returns a list of zero, one or two solution points.
    """
    d = vector.norm(p2-p1)
    if not tol_gt(d, 0):
        return []
    u = ((r1*r1 - r2*r2)/d + d)/2
    if tol_lt(r1*r1, u*u):
        return []
    elif r1*r1 < u*u:
        v = 0.0
    else:
        v = math.sqrt(r1*r1 - u*u)
    s = (p2-p1) * u / d
    if tol_eq(vector.norm(s),0):
        p3a = p1+vector.vector([p2[1]-p1[1],p1[0]-p2[0]])*r1/d
        if tol_eq(r1/d,0):
            return [p3a]
        else:
            p3b = p1+vector.vector([p1[1]-p2[1],p2[0]-p1[0]])*r1/d
            return [p3a,p3b]
    else:
        p3a = p1 + s + vector.vector([s[1], -s[0]]) * v / vector.norm(s) 
        if tol_eq(v / vector.norm(s),0):
            return [p3a]
        else:
            p3b = p1 + s + vector.vector([-s[1], s[0]]) * v / vector.norm(s)
            return [p3a,p3b]

def is_counterclockwise(p1,p2,p3):
    """ returns True iff triangle p1,p2,p3 is counterclockwise oriented"""
    assert len(p1)==2
    assert len(p1)==len(p2)
    assert len(p2)==len(p3)
    u = p2 - p1
    v = p3 - p2;
    perp_u = vector.vector([-u[1], u[0]])
    return tol_gt(vector.dot(perp_u,v), 0)

def angle_3p(p1, p2, p3):
    """Returns the angle, in radians, rotating vector p2p1 to vector p2p3.
       arg keywords:
          p1 - a vector
          p2 - a vector
          p3 - a vector
       returns: a number
       In 2D, the angle is a signed angle, range [-pi,pi], corresponding
       to a clockwise rotation. If p1-p2-p3 is clockwise, then angle > 0.
       In 3D, the angle is unsigned, range [0,pi]
    """
    d21 = vector.norm(p2-p1)
    d23 = vector.norm(p3-p2)
    if tol_eq(d21,0) or tol_eq(d23,0):
        # degenerate, indeterminate angle
        return None
    v21 = (p1-p2) / d21
    v23 = (p3-p2) / d23
    t = vector.dot(v21,v23) # / (d21 * d23)
    if t > 1.0:             # check for floating point error
        t = 1.0
    elif t < -1.0:
        t = -1.0
    angle = math.acos(t)
    if len(p1) == 2:        # 2D case
        if is_counterclockwise(p1,p2,p3):
            angle = -angle
    return angle

