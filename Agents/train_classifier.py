
import cv2
import numpy as np
from sklearn.linear_model import SGDClassifier
from sklearn.neural_network import MLPClassifier
from sklearn import tree
import csv
video_height = 240
video_width = 432

def train_classifier():
    #creates an np array to store all the features for each fram collected from the oracle
    filename = "D:\\CS175Dataset\\images\\"
    count = 0
    lr =  tree.DecisionTreeClassifier()
    #populates the x_train np array with edge detection data for each frame collected
    with open('D:\\CS175Dataset\\actions.csv', 'rb') as f:
        reader = csv.reader(f)
        y_train = np.array([])
        img = cv2.imread(filename + str(0) + ".png")
        edges = cv2.Canny(img, 200, 300)
        edges = edges[80:160,72:360]
        print edges.shape
        x_train = edges.flatten()
        for rows in reader:
            print "adding " + str(count)
            y_data = list(rows)
            size = len(y_data)
            new_y_train = np.array(y_data)
            y_train = np.append(y_train,new_y_train)
            for i in range(count*(size),size*(count+1)):
                if i != 0:
                    img = cv2.imread(filename+str(i)+".png")
                    edges = cv2.Canny(img, 200, 300)
                    edges = edges[80:160,72:360]
                    x_train = np.vstack((x_train,edges.flatten()))
            count = count + 1
    lr.fit(x_train, y_train)
    f.close()
    return lr



