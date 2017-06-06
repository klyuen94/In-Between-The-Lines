
import cv2
import numpy as np
from sklearn.linear_model import SGDClassifier
from sklearn.neural_network import MLPClassifier
import csv
video_height = 240
video_width = 432

def train_classifier():
    #creates an np array to store all the features for each fram collected from the oracle
    filename = "C:/Users/hrvega1510/Desktop/CS175Dataset/images/"
    count = 0
    lr =  MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(5, 2), random_state=1)
    #populates the x_train np array with edge detection data for each frame collected
    with open('actions.csv', 'rb') as f:
        reader = csv.reader(f)
        for rows in reader:
            y_data = list(rows)
            print y_data
            size = len(y_data)
            y_train = np.array(y_data)
            img = cv2.imread(filename + str(0) + ".png")
            edges = cv2.Canny(img, 200, 300)
            x_train = edges.flatten()
            for i in range(count*(size),size*(count+1)-1):
                img = cv2.imread(filename+str(i)+".png")
                edges = cv2.Canny(img, 200, 300).flatten()
                x_train = np.vstack((x_train,edges))
            count = count + 1
            print "training " + str(count)
            lr.fit(x_train, y_train)
    f.close()
    return lr



