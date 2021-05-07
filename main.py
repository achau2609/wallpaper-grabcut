
'''
===============================================================================
Wallpaper Grabcut
    This is an application which makes use of the GrabCut algorithm to replace
the wallpaper of a wall in a picture of a room.

README FIRST:
    Two windows will show up, one for input and one for output.
    At first, in input window, draw a rectangle around the object using the
right mouse button. Then press 'z' to segment the object (once or a few times)
For any finer touch-ups, you can press any of the keys below and draw lines on
the areas you want. Then again press 'z' to update the output.
Key 'q' - To select areas of sure background
Key 'w' - To select areas of sure foreground
Key 'z' - To update the segmentation
Key 'm' - To reset the setup
===============================================================================
'''

import cv2 as cv
import numpy as np

class wallpaperCut():
    # Lists for RGB values of a color
    BLUE = [255,0,0]        # rectangle color
    RED = [0,0,255]         # PR BG
    GREEN = [0,255,0]       # PR FG
    BLACK = [0,0,0]         # sure BG
    WHITE = [255,255,255]   # sure FG

    # Dicts to indicate foreground and background on the image
    DRAW_BG = {'color' : BLACK, 'val' : 0}
    DRAW_FG = {'color' : WHITE, 'val' : 1}
    DRAW_PR_BG = {'color' : RED, 'val' : 2}
    DRAW_PR_FG = {'color' : GREEN, 'val' : 3}

    # Some variables for fgdCut
    rect = (0,0,1,1)
    drawing = False         # flag for drawing curves
    rectangle = False       # flag for drawing rect
    rect_over = False       # flag to check if rect drawn
    gc_mode = 100           # flag for selecting rect or mask mode
    value = DRAW_FG         # drawing initialized to FG

    # Import the images required into the script
    room = cv.imread('imgs\sample4.jpg')           # 1: img of room
    wallpaper = cv.imread('imgs\wp_tile.png')     # 2: wallpaper

    temp_mask = np.zeros(room.shape[:2],np.uint8)

    #wallpaper replace var
    ptcount = 0
    ptArray = []
    
    # Function for applying the wallpaper to the selected section of the room according to our wallpaper mask
    def wallpaperReplacement(self):

        #calls function to fit wallpaper to img size
        self.wallpaperSizeFitting()

        # NEW REWRITE: CREATE MASK BASE FOR POLYGON
        mask_poly = np.zeros(self.room.shape[:2],np.uint8)

        # fillConvexPoly to highlight area for wallpaper replacement
        wp_b = np.array(self.ptArray)
        wp_fill = cv.fillConvexPoly(mask_poly,wp_b,255)

        wp_fill[wp_fill == 0] = cv.GC_BGD
        wp_fill[wp_fill == 255] = cv.GC_FGD

        #create clone of pic and bg
        self.bgdOut = self.room.copy()
        self.wp = self.wallpaper.copy()

        #Crop area to apply to img as wallpaper
        self.wp_resized[wp_fill == 0] = [0,0,0]

        #Removes area where wallpaper will be applied
        #wp_in[mask == 1] = [0,0,0]
        self.bgdOut[wp_fill == 1] = [0,0,0]

        #Combine the both
        #background = img_in + wp_in
        self.bgdOut = self.wp_resized + self.bgdOut

    def mousePointFunc(self,event,x,y,flags,param):
        if event == cv.EVENT_LBUTTONDOWN:
            cv.circle(self.input,(x,y),8,(255,0,0),-1)
            point = [x,y]
            self.ptArray.append(point)
            self.ptcount += 1

    def findWpPts(self):

        cv.namedWindow('Input',cv.WINDOW_KEEPRATIO)
        cv.setMouseCallback('Input', self.mousePointFunc)

        print("select 4 pts! start from top left corner, then bottom left corner, after that bottom right corner, finally top right corner. After that, press Esc to get the final product. \n")

        while(1):
            cv.imshow('Input', self.input)
            cv.resizeWindow('Input', 1366, 768)
            k = cv.waitKey(1)

            if k == 27:
                if self.ptcount == 4:
                    break
                else:
                    print("you need to select 4 points! if u selected more than 4, press m to reset and start over again. \n")
            elif k == ord('m'): # reset everything
                print("resetting \n")
                self.ptcount = 0
                self.ptArray = []
                self.input = self.room.copy()

        cv.destroyAllWindows()

    # Resize wallpaper to match img dimensions
    def wallpaperSizeFitting(self):

        self.wp_resized = np.zeros(self.room.shape, np.uint8)

        #crop the wallpaper to fit the dimensions of the image (if it is oversized)
        if self.wallpaper.shape[0] > self.room.shape[0] or self.wallpaper.shape[1] > self.room.shape[1]:
            self.wp_resized = self.wallpaper[0:self.room.shape[0],0:self.room.shape[1]]
        #iterates wallpaper to fill the dimensions of the image (if it is undersized)
        elif self.wallpaper.shape[0] < self.room.shape[0] or self.wallpaper.shape[1] < self.room.shape[1]:
            #another_wpmask = np.zeros((imgs_h,imgs_w),np.uint8)
            x_iter = (self.room.shape[0] // self.wallpaper.shape[0]) + 1
            y_iter = (self.room.shape[1] // self.wallpaper.shape[1]) + 1
            self.wp_resized = cv.repeat(self.wallpaper, x_iter, y_iter)
            self.wp_resized = self.wp_resized[0:self.room.shape[0],0:self.room.shape[1]]
    
    # Function for combining the foreground and the background
    def combine(self):

        self.bgdOut[self.finaloutputmask != 0] = [0,0,0]

        self.final = self.output + self.bgdOut

    # Function for showing final output
    def show(self):
        
        print("Here's the output! Press Esc to close the process, this output will be saved in the same directory as an image. \n")
        cv.namedWindow('Output', cv.WINDOW_KEEPRATIO)
        cv.imshow('Output', self.final)
        cv.resizeWindow('Output', 1366, 768)
        cv.waitKey(0)
        cv.destroyAllWindows()
        cv.imwrite('output.png', self.final)

    # Defines the behaviour when certain mouse keys are pressed and released in the input window
    def mouseDrawFunc(self,event,x,y,flags,param):

        #initial rect area
        if event == cv.EVENT_RBUTTONDOWN:
            self.rectangle = True
            self.ix, self.iy = x,y

        elif event == cv.EVENT_MOUSEMOVE:
            if self.rectangle == True:
                self.input = self.room.copy()
                cv.rectangle(self.input, (self.ix, self.iy), (x, y), self.BLUE, 4)
                self.rect = (min(self.ix, x), min(self.iy, y), abs(self.ix - x), abs(self.iy - y))
                self.rect_or_mask = 0

        elif event == cv.EVENT_RBUTTONUP:
            self.rectangle = False
            self.rect_over = True
            cv.rectangle(self.input, (self.ix, self.iy), (x, y), self.BLUE, 4)
            self.rect = (min(self.ix, x), min(self.iy, y), abs(self.ix - x), abs(self.iy - y))
            self.rect_or_mask = 0
            print("Now press the key 'z' to run GrabCut. \n")

        # draw touchup curves
        if event == cv.EVENT_LBUTTONDOWN:
            if self.rect_over == False:
                print("Please draw a rectangle first. \n")
            else:
                self.drawing = True
                cv.circle(self.input, (x,y), 5, self.value['color'], -1)
                cv.circle(self.mask, (x,y), 5, self.value['val'], -1)

        elif event == cv.EVENT_MOUSEMOVE:
            if self.drawing == True:
                cv.circle(self.input, (x, y), 5, self.value['color'], -1)
                cv.circle(self.mask, (x, y), 5, self.value['val'], -1)

        elif event == cv.EVENT_LBUTTONUP:
            if self.drawing == True:
                self.drawing = False
                cv.circle(self.input, (x, y), 5, self.value['color'], -1)
                cv.circle(self.mask, (x, y), 5, self.value['val'], -1)

    # Foreground(furniture) Cut
    def fgdCut(self):
        print("Here is the final output. \n")
        cv.namedWindow('Input',cv.WINDOW_KEEPRATIO)
        cv.namedWindow('Output',cv.WINDOW_KEEPRATIO)
        cv.setMouseCallback('Input', self.mouseDrawFunc)
        cv.moveWindow('input', self.room.shape[1]+10,90)

        print("Cut out the furniture")

        while(1):

            cv.imshow('Input', self.input)
            cv.resizeWindow('Input', 1366, 768)
            #1366,768
            cv.imshow('Output', self.output)
            cv.resizeWindow('Output', 1366, 768)
            k = cv.waitKey(1)

            if k == 27:         # esc to exit
                break
            elif k == ord('q'): # BG drawing
                print("Mark background regions with left mouse button. \n")
                self.value = self.DRAW_BG
            elif k == ord('w'): # FG drawing
                print("Mark foreground regions with left mouse button. \n")
                self.value = self.DRAW_FG
            elif k == ord('m'): # reset everything
                print("Resetting the canvas... \n")
                self.rect = (0,0,1,1)
                self.drawing = False
                self.rectangle = False
                self.rect_or_mask = 100
                self.rect_over = False
                self.value = self.DRAW_FG
                self.input = self.room.copy()
                self.mask = np.zeros(self.input.shape[:2], dtype = np.uint8) # mask initialized to PR_BG
                self.output = np.zeros(self.input.shape, np.uint8)           # output image to be shown
            elif k == ord('z'): # segmentation
                try:
                    print("Running GrabCut, hold on... \n")
                    bgdModel = np.zeros((1,65),np.float64)
                    fgdModel = np.zeros((1,65),np.float64)
                    #grabcut with rect
                    if (self.rect_or_mask == 0):
                        cv.grabCut(self.room,self.mask,self.rect,bgdModel,fgdModel,1,cv.GC_INIT_WITH_RECT)
                        self.rect_or_mask = 1
                    #grabcut with mask
                    elif (self.rect_or_mask == 1):       
                        cv.grabCut(self.room,self.mask,self.rect,bgdModel,fgdModel,1,cv.GC_INIT_WITH_MASK)
                    print("Done! Press 'z' again if more iterations are needed. Otherwise, press Esc key to move onto the next step. \n")
                except:
                    import traceback
                    traceback.print_exc()

            mask2 = np.where((self.mask==2)|(self.mask==0),0,1).astype('uint8')
            self.output = self.room*mask2[:,:,np.newaxis]

        self.finaloutputmask = mask2

        cv.destroyAllWindows()

    def init(self):

        # Init params
        self.input = self.room.copy()
        self.mask = mask = np.zeros(self.input.shape[:2],np.uint8)
        self.output = np.zeros(self.input.shape, np.uint8)

        #cut foreground(furniture) -> background(wall) -> combine them
        self.fgdCut()                   #gets fgd
        self.input = self.room.copy()   #reset for wallpaper
        self.findWpPts()                #finds bounds for wallpaper
        self.wallpaperReplacement()     #gets bgd
        self.combine()                  #combine fgd and bgd
        self.show()

if __name__ == "__main__":
    print(__doc__)
    wallpaperCut().init()
   
    
