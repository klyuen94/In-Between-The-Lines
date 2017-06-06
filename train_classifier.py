
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
    filename = "C:/Users/hrvega1510/Desktop/CS175Dataset/images/"
    count = 0
    lr =  tree.DecisionTreeClassifier()
    #populates the x_train np array with edge detection data for each frame collected
    with open('C:/Users/hrvega1510/Desktop/CS175Dataset/actions.csv', 'rb') as f:
        reader = csv.reader(f)
        y_train = np.array([])
        img = cv2.imread(filename + str(0) + ".png")
        edges = cv2.Canny(img, 200, 300)
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
                    edges = cv2.Canny(img, 200, 300).flatten()
                    x_train = np.vstack((x_train,edges))
            count = count + 1
    print x_train.shape
    print y_train.shape
    lr.fit(x_train, y_train)
    f.close()
    return lr



