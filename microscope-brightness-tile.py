import sys
from PIL import Image
from PIL import ImageStat
from datetime import datetime
import math

#input parameters
firstImageID = 1                             # serial number of the first image - integer value
lastImageID = 600                            # serial number of the first image  - integer value
num_images = lastImageID - firstImageID + 1  # total number of images
stringLength = 4                             # total length of image name, with zeroes appended. If stringLength = 4, we get values such as 0001, 0010, 0100 
imageStringList = []                         # string list in which images numbers will be stored, with zeroes pre-fixed
imgBrightList = []                           # list to store image brightness values
imgBrightCorrList = []                       # list to store image brightness correction values = avg_brightness - image_brightness
input_folder = 'input/'                      # The sub-folder where the input images are stored
output_folder = 'interim_output/' 	         # The sub-folder where INDIVIDUAL brightness-adjusted images are stored. The final image is stored in root folder
finalImgName = 'final_canvas_image'          # Name of final tiledimage
xCoordFile = 'configx.txt'                   # name of text file with x Coordinates; should be in root folder. else preface name with 'subfolder/'
yCoordFile = 'configy.txt'				     # name of text file with y Coordinates; should be in root folder. else preface name with 'subfolder/'
xCoordinates = []                           # array that stores all x Coordinates
yCoordinates = []                           # array that stores all y Coordinates

# read values of image coordinates from a text file, and store them in 2 lists as float datatype
file = open(xCoordFile,'r')
for line in file:
	cleanLine = line.replace("\n","")   # remove newline
	xCoordinates.append(float(cleanLine))
file.close()	

file = open(yCoordFile,'r')
for line in file:
	cleanLine = line.replace("\n","")   # remove newline
	yCoordinates.append(float(cleanLine))
file.close()

# PART I: Generate list of image names; pre-fix zeroes so that string length = stringLength
i = firstImageID
while i < lastImageID + 1:
    imageStringList.append(str(i).rjust(stringLength,'0'))
    i = i + 1
print imageStringList

# PART II: Adjusts brightness of individual images
# -------
# function to return average brightness of an image
# Source: http://stackoverflow.com/questions/3490727/what-are-some-methods-to-analyze-image-brightness-using-python
# the function below assigns weights to the root-mean-square average of r g and b based on how humans perceive different colors

def brightness(im_file):
   im = Image.open(im_file)
   stat = ImageStat.Stat(im)
   r,g,b = stat.mean
   return math.sqrt(0.299*(r**2) + 0.587*(g**2) + 0.114*(b**2))   


for i in range(0, num_images):
   a = imageStringList[i]
   image_name = input_folder + a + '.jpg' 
   imgBrightList.append(brightness(image_name))

avg_brightness = sum(imgBrightList[0:])/num_images

for i in range(0, num_images):
   imgBrightCorrList.append(i)
   imgBrightCorrList[i] = avg_brightness - imgBrightList[i]   # imgBrightCorrList[] is a list of all the correction values
   
# Opens each input file, loads onto pixel map, re-draws pixel-by-pixel with brightness correction
# Finally, saves to output file in output folder
print 'Color correction start', datetime.now()
print 'Image being written',

for k in range(0, num_images):		
   image_name = input_folder + imageStringList[k] + '.jpg'
   img_file = Image.open(image_name)
   img_file = img_file.convert('RGB')     # converts image to RGB format, writes it back to the original image
   pixels = img_file.load()               # creates the pixel map
   for i in range (img_file.size[0]):
      for j in range (img_file.size[1]):
         r, g, b = img_file.getpixel((i,j))  # extracts r g b values for the i x j th pixel
         pixels[i,j] = (r+int(imgBrightCorrList[k]), g+int(imgBrightCorrList[k]), b+int(imgBrightCorrList[k])) # re-creates the image
   new_image_name = output_folder +'image' + imageStringList[k] + '.jpg'      # output stored in output_folder. 
   img_file.save(new_image_name)
   print imageStringList[k],


# Calculate min and max x/y values of all images from their input coordinates
min_x = 0.0
max_x = 0.0
min_y = 0.0
max_y = 0.0

for i in yCoordinates:     
   if min_y > i:
      min_y = i
   if max_y < i:
      max_y = i

for i in xCoordinates:
   if min_x > i:
      min_x = i
   if max_x < i:
      max_x = i

# Calculate pane (canvas) size
y_height = max_y - min_y
x_width = max_x - min_x

# Set image size based on first image
image_name = Image.open(output_folder + 'image' + imageStringList[0] + '.jpg') 
width, height = image_name.size
# print width, height

canvas_width = int(x_width) + width
canvas_height = int(y_height) + height

new_im = Image.new('RGB', (canvas_width, canvas_height))

# initializes starting point of image based on whether travel direction is to the left or the right
init_x = 0
if xCoordinates[1] < 0.0:
    init_x = int(x_width)


print 'tiling start', datetime.now()

for k in range(0,num_images):
    image_name = output_folder + 'image' + imageStringList[k] + '.jpg'
    im = Image.open(image_name) # opens image
    new_im.paste(im, (int(init_x + xCoordinates[k]),int(abs(min_y))+int(yCoordinates[k])))  # pastes image on canvas
	
new_im.save(finalImgName+'.jpg')  # saved in root folder

print 'tiling end', datetime.now()
