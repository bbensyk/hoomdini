import itertools
import numpy as np

"""Basic hexagonal packing function"""

def HexCoords(x1, y1, x2, y2):

    startX = min(x1, x2)
    endX = max(x1, x2)

    startY = min(y1, y2)
    endY = max(y1, y2)
    def flat(x,y):
        return [x,y,0]
    def off(x,y):
        return [x+0.5, y+ np.sqrt(3)/2, 0]
    P1 = [startX,startY,0]
    P2 = [startX+0.5, startY+ np.sqrt(3)/2, 0]
    xv1 = np.arange(startX, endX, step=1)
    xv2 = np.arange(startX+0.5,endX+0.5,step=1)
    xs = []
    yv = [y1] if y1 == y2 else np.arange(startY, endY, step=np.sqrt(3)/2)
    yv1 = [y1] if y1 == y2 else np.arange(startY, endY, step=np.sqrt(3))
    yv2 = [y1] if y1 == y2 else np.arange(startY+np.sqrt(3)/2, endY+np.sqrt(3)/2,step=np.sqrt(3))
    coords1 = list(itertools.product(xv1, yv1))
    coords2 = list(itertools.product(xv2, yv2))
    xyCoords = coords1 + coords2
    x,y = zip(*xyCoords)
    return list(zip(x,y, [0] * len(x)))

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    coordinateList = list(HexCoords(0,0,5,5,0.2))
    print(coordinateList)
    x,y,z = zip(*coordinateList)
    plt.scatter(x, y)