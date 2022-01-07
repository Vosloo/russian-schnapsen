<center><h1>Russian schnapsen detection</h1></center>

Project aims to detect events in a game of [Russian schnapsen](https://en.wikipedia.org/wiki/Russian_Schnapsen). The project is based on [OpenCV](https://opencv.org/) and [Python 3.8](https://www.python.org/) as well as YOLOv5 for object detection. 

YOLOv5 is a object detection model trained on a custom dataset. The dataset can be easily created for your set of playing cards by using repository [playing-cards-detection](https://github.com/Vosloo/playing-cards-detection). 

For this project, three scans of the playing cards are used, each containing 8 cards. which are then extracted and merged into one image with a random background photo. The background dataset can be obtained from [here](https://www.robots.ox.ac.uk/~vgg/data/dtd/).

The model is trained on a dataset of 8,000 generated images with a medium-sized model with a batch-size of 16 and 30 epochs. The model was tested on a set of 2,000 images. The scores of the model are shown below.

<h3>Confusion matrix:</h3>

<img src="images/confusion_matrix.png" alt="Confusion matrix" width="700"/>

<h3>Characteristics of the model:</h3>

<img src="images/charts.png" alt="Characteristics" width="700"/>
