# Export Subsampler

The application works to visualize the result of subsampling a polygon-intensive export file, using the visvalingam whyatt algorithm.

The goal of the project is to reduce the export size when required, and also to get insights into various polygonal properties of the project.
Such as how IOU and Lenght change for different subsampling ratios.

### Experiments
Experiments were run to determine the effect of size reduction on information retention. 
The key method used was Polygon Subsampling (which tries to reduce the vertices of any polygon)

Polymore project was used as the standard file for these experiments, containing 563 assets.

The information loss chart - a graph to  compare the average IOUs of the original polygon vs subsampling (simplification) ratio
Size reduction chart - to show how size would reduce as a function of the subsampling ratio.
A scatter plot to compare the size reduction vs the information loss. 

### Produces Visualizations
* The information loss chart - a graph to  compare the average IOUs of the original polygon vs subsampling (simplification) ratio
* Size reduction chart - to show how size would reduce as a function of the subsampling ratio.
* Size reduction vs the information loss plot to determine how much information is retained as size of the file reduces 
* 2 Bar charts Showing how the IOUs and Polygon Sizes vary for different classes for 3 distinct Subsampling / Simplification Ratios for the polygons.
* A set of images, titles by their subsampling rates, showing how polygon complexity increases over time.

### How to Run
* Simply run the command python3 subsample.py to obtain results (may take a few seconds to minutes of processing, depending on export file size).
* To modify parameters simply open the file and change them. Possible changes include: 
STARTING_RATIO (The Subsampling ratio to start with * 10 e.g 4)
RATIO_STEP (The Subsampling ratio to step with * 10 e.g 1)
FILE_NAME (The name if the export file e.g 'Polymore.json') 
IOU_TO_STOP (The minimum IOU to maintian in the final export file e.g 0.9)
VISUALIZE (Boolean to save image visualizations or not, e.g. False)
ASSETS_TO_VISUALIZE (Number of images selected for visualization e.g. 5)
