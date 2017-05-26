import cv2
import numpy as np
from sklearn.linear_model import LinearRegression

filename = 'C:/Users/hrvega1510/PycharmProjects/cs_175/Malmo-0.21.0-Windows-64bit/Malmo-0.21.0-Windows-64bit/Python_Examples/test.jpg'
img = cv2.imread(filename)
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

# find Harris corners
gray = np.float32(gray)
dst = cv2.cornerHarris(gray,2,3,0.04)
dst = cv2.dilate(dst,None)
ret, dst = cv2.threshold(dst,0.01*dst.max(),255,0)
dst = np.uint8(dst)

# find centroids
ret, labels, stats, centroids = cv2.connectedComponentsWithStats(dst)

# define the criteria to stop and refine the corners
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
corners = cv2.cornerSubPix(gray,np.float32(centroids),(5,5),(-1,-1),criteria)
print corners
print corners.shape
# Now draw them
res = np.hstack((centroids,corners))
res = np.int0(res)
img[res[:,1],res[:,0]]=[0,0,255]
img[res[:,3],res[:,2]] = [0,255,0]

cv2.imwrite('subpixel5.png',corners)

edges = cv2.Canny(img,200,300)
cv2.imwrite('subpixel4.png',edges)

edges_list = [edges]
y_train_list = [1]

lr = LinearRegression()
for i in range(1000):
    d = np.ones(edges.shape[0])
    d.fill(y_train_list[0])
    lr.fit(edges_list[0], d)

y_hat = lr.predict(edges)






