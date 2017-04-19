'''import time
from SimpleCV.ImageClass import Carame

cam = Camera()
time.sleep(0,1) 
img = cam.getImage()
img.save("AAA.jpg")
print "OKKK" '''


import pygame
import pygame.camera
import pygame.image
import sys
import os
from pygame.locals import *


pygame.camera.init()
cameras = pygame.camera.list_cameras()
print "success"
#print "Camera %s ..." % cameras[0]

webcam = pygame.camera.Camera("/dev/video0",(640,480)) 
webcam.start()
img = webcam.get_image()
filename = "output.png"
pygame.image.save(img, filename)
print "image was been saved"
