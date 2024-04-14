import numpy as np
import matplotlib.pyplot as plt

def knot_interval(i_pts, alpha=0.5, closed=False):
    if len(i_pts)<4:
        raise ValueError('CR-curves need at least 4 interpolatory points')
    #i_pts is the list of interpolatory points P[0], P[1], ... P[n]
    if closed:
        i_pts+=[i_pts[0], i_pts[1], i_pts[2]]
    i_pts=np.array(i_pts)
    dist=np.linalg.norm(i_pts[1:, :]-i_pts[:-1,:], axis=1)
    return dist**alpha
 

def ctrl_bezier(P, d):
    #Associate to 4 consecutive interpolatory points and the corresponding three d-values, 
    #the Bezier control points
    if len(P)!=len(d)+1!=4:
        raise ValueError('The list of points and knot intervals have inappropriate len ')
    P=np.array(P)    
    bz=[0]*4
    bz[0]=P[1]
    bz[1]=(d[0]**2*P[2]-d[1]**2*P[0] +(2*d[0]**2+3*d[0]*d[1]+d[1]**2)*P[1])/(3*d[0]*(d[0]+d[1]))
    bz[2]=(d[2]**2*P[1]-d[1]**2*P[3] +(2*d[2]**2+3*d[2]*d[1]+d[1]**2)*P[2])/(3*d[2]*(d[1]+d[2]))
    bz[3]=P[2]
    return bz

def Bezier_curve(bz, nr=100):
    #implements the de Casteljau algorithm to compute nr points on a Bezier curve
    
    t=np.linspace(0,1, nr)
    N=len(bz) 
    points=[]# the list of points to be computed on the Bezier curve
    for i in range(nr):#for each parameter t[i] evaluate a point on the Bezier curve 
                       #via De Casteljau algorithm
        aa=np.copy(bz) 
        for r in range(1,N):
            aa[:N-r,:]=(1-t[i])*aa[:N-r,:]+t[i]*aa[1:N-r+1,:]# convex combination
        points.append(aa[0,:])                                  
    return points 

def Catmull_Rom(i_pts, alpha=0.5,  closed=False):
    #returns the list of points computed on the interpolating CR curve
    #i_pts the list of interpolatory points P[0], P[1], ...P[n]
    curve_pts=[]#the list of all points to be computed on the CR curve
    d=knot_interval(i_pts, alpha=alpha, closed=closed)
    for k in range(len(i_pts)-3):
        cb=ctrl_bezier(i_pts[k:k+4], d[k:k+3])
        curve_pts.extend(Bezier_curve(cb, nr=100))
    
    return np.array(curve_pts)

P=[[-5, -0.3], [-4,0], [1., 0.8], [1.1, 0.5], [8.7, 1.2], [10, 0.27]]

curve0=Catmull_Rom(P, alpha=0, closed=False)
curve1=Catmull_Rom(P, alpha=0.5, closed=False)
curve2=Catmull_Rom(P, alpha=1.0, closed=False)
xp, yp=zip(*P)

fig=plt.figure(figsize=(9,6))
plt.plot(curve0[:,0], curve0[:,1], 'r', xp, yp, 'go' )
plt.plot(curve1[:,0], curve1[:,1], 'g')
plt.plot(curve2[:,0], curve2[:,1], 'b')

plt.show()  # Display the plot