import pygame
from random import randint
from time import time
from algs import algorithmsDict
import display as display
import os
import imageio.v3
import gc

# Declared in display.py
# 1. global variables : numBars, delay, do_sorting, paused, timer_space_bar
# 2. widgets : sizeBox, delayBox, algorithmBox, playButton, stopButton


#Todo:
# Add looping option
# Add time estimate
# Make better number of pictures sorter
# Create own git page with reference
# Add log to window, stop using terminal
# Add "speed" adjust eg FPS as option
# Add more file types, eg MP4
# Add option to print numbers in "bars"


#Generating gifs requires placing files in subfolder and then loading them.
#This deletes everything except gif
def deleteTempFiles():
    try:
        myFiles = []
        myDir = []
        for pathnames,dirnames,filenames in os.walk("pictures"):
            myFiles.extend(filenames)
            myDir.extend(dirnames)
        for files in myFiles:
            os.remove("pictures/" + files)
        for directories in myDir:
            os.rmdir("pictures/" + directories)
    except:
        raise EIO("Could not delete files in subfolder!")

def CreateGIF(counter,SCREENSHOT_FILENAME):
    #Idea is that pictures are generated with numbers 0 to some MAX
    print("Trying to generate GIF, this may freeze the program and take a while")
    #Find max
    fileNames = [] #Okay, let's start preparing for GIF
    for i in range(0,counter):
        fileNames.append(SCREENSHOT_FILENAME + str(i) + ".jpg")
    images = []
    #This will start to load in individual pictures into gif engine
    #In theory, an optimization is possible here by streaming the data in smaller batches
    #This would save alot of memory
    newGif = imageio.get_writer('sorting2.gif',format='GIF-PIL',mode='I',fps=100)
    try:
        for (counter,filename) in enumerate(fileNames):
            #images.append(imageio.v2.imread(filename))
            newGif.append_data(imageio.v2.imread(filename))
            if counter % 100 == 0:
                print("Progress:" + str(counter) + "/" + str(len(fileNames)))
    except:
        raise EIO("Tried to create GIF, did not find sample pictures")
    #Output gif
    #imageio.mimsave('sorting.gif', images, format = 'GIF-PIL', fps = 100)
    #Del latest list, this does NOT decrease current RAM usage, 
    #but makes next round use the same memory area instead
    newGif.close()
    del fileNames
    for item in images:
        del item
    del images
    gc.collect()
    print("GIF generated as sorting.gif folder")
    #Delete all files in folder
    deleteTempFiles()
    
    
def getMaxNumber(files):
    currentMax  = -1
    for item in files:
        myNumber = int(item[len(SCREENSHOT_FILENAME):len(item)-4])
        if myNumber > currentMax:
            currentMax = myNumber
    return currentMax

def takePicture(SCREENSHOT_FILENAME,GIF_picture_counter,screenshot):
    pygame.image.save(screenshot, "pictures/screenshot" + str(GIF_picture_counter) + ".jpg")

def createPicturesFolder():
    myDir = []
    for pathnames,dirnames,filenames in os.walk(os.getcwd()):
            myDir.extend(dirnames)
    for directory in myDir:
        if directory == "pictures":
            return -1
    try:
        os.mkdir("pictures")
    except:
        raise Exception("Could not create pictures folder")
    
def main():
    SCREENSHOT_FILENAME = "pictures/screenshot" #+ a counter number + JPG
    GIF_WINDOW_SIZE = (900, 400)
    
    numbers = []
    running = True
    display.algorithmBox.add_options(list(algorithmsDict.keys()))

    current_alg = None
    alg_iterator = None

    timer_delay = time()
    
    #One keeps track of how many files have been created, the other how many total images
    GIF_picture_counter = 0
    GIF_skip_image_counter = 0
    
    #Just to make sure nothing from prev runs is left
    deleteTempFiles()
    
    #Create pictures if it does not exists
    createPicturesFolder()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and display.do_sorting:
                display.paused = not display.paused
                display.timer_space_bar = time()

            display.updateWidgets(event)

        display.delay = (display.delayBox.value-display.delayBox.rect.x-6)/1000 # delay is in ms

        if display.playButton.isActive: # play button clicked
            try:
                if int(display.sizeBox.text) > 1000:
                    # This is limitation because of RAM. size = 100 needs 2GB of RAM, so 120 is for some reason significantly higher
                    print("GIF cannot be created for size > 1000")
                elif int(display.sizeBox.text) > 1000:
                    print("Warning: Creating a GIF for array > 500 will require more than 8GB of memory")
                else:
                    display.do_sorting = True
                    display.playButton.isActive = False
                    current_alg = display.algorithmBox.get_active_option()
                    display.numBars = int(display.sizeBox.text)
                    numbers = [randint(10, 400) for i in range(display.numBars)]  # random list to be sorted
                    alg_iterator = algorithmsDict[current_alg](numbers, 0, display.numBars - 1)  # initialize iterator
                display.playButton.isActive = False
            except:
                raise ValueError("Text in size field is not a number")

        if display.stopButton.isActive: # stop button clicked
            display.stopButton.isActive = False
            display.do_sorting = False
            display.paused = False
            try: # deplete generator to display sorted numbers
                while True:
                    numbers, redBar1, redBar2, blueBar1, blueBar2 = next(alg_iterator)
            except StopIteration:
                pass
            #Check if user wants GIF, then delete temp files. No gif is possible becuase early stop
            if True:
                deleteTempFiles()
                GIF_picture_counter = 0
                GIF_skip_image_counter = 0
                
        #GIF needs it's own thing
        screenshot = pygame.Surface(GIF_WINDOW_SIZE)
        screenshot.blit(display.screen, (0,0))
        
        if display.do_sorting and not display.paused: # sorting animation
            try:
                if time()-timer_delay >= display.delay:
                    numbers, redBar1, redBar2, blueBar1, blueBar2 = next(alg_iterator)
                    display.drawInterface(numbers, redBar1, redBar2, blueBar1, blueBar2)
                    #If GIF is to be output, a picture needs to be generated and saved temporarily
                    if True:
                        #If less then 300, take every size/100 picture
                        #ergo size = 100 => every picture, size = 300 => every third picture
                        if int(display.sizeBox.text) <= 300:
                            ratio = 1
                            if int(display.sizeBox.text) >= 100:
                                ratio = int(int(display.sizeBox.text)/100)
                            if GIF_skip_image_counter % ratio == 0 or int(display.sizeBox.text) < 100:
                                takePicture(SCREENSHOT_FILENAME,GIF_picture_counter,screenshot)
                                GIF_picture_counter +=1
                            GIF_skip_image_counter +=1
                        #If size > 300, then we need to take draastically less pictures
                        else:
                            if int(GIF_skip_image_counter) % int(int(display.sizeBox.text)/20) == 0:
                                takePicture(SCREENSHOT_FILENAME,GIF_picture_counter,screenshot)
                                GIF_picture_counter +=1
                            GIF_skip_image_counter +=1
                    timer_delay = time()
                    
            except StopIteration:
                display.do_sorting = False
                #If program stops because end of sorting, gif needs to be created if selected
                if True: #Check if GIF was requested
                    #Call function for GIF
                    CreateGIF(GIF_picture_counter,SCREENSHOT_FILENAME)
                    #Reset counter
                    GIF_picture_counter = 0
                    GIF_skip_image_counter = 0
                
        elif display.do_sorting and display.paused: # animation paused
            display.drawInterface(numbers, -1, -1, -1, -1)
        else: # no animation
            a_set = set(range(display.numBars))
            display.drawInterface(numbers, -1, -1, -1, -1, greenRows=a_set)

if __name__ == '__main__':
    main()
