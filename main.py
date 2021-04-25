
'''
===============================================================================
Wallpaper Grabcut
    This is an application which makes use of the GrabCut algorithm to replace
the wallpaper of a wall in a picture of a room.

README FIRST:
    Two windows will show up, one for input and one for output.
    At first, in input window, draw a rectangle around the object using the
right mouse button. Then press 'n' to segment the object (once or a few times)
For any finer touch-ups, you can press any of the keys below and draw lines on
the areas you want. Then again press 'n' to update the output.
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
    #thickness = 3           # brush thickness

    # Import the images required into the script
    room = cv.imread('imgs\sofa.jpg')                           # 1: img of room
    wallpaper = cv.imread('imgs\space.jpg')                     # 2: wallpaper
    #wallpaper = cv.imread('imgs\wp_tile.png')                  # 2.5: wallpaper tile
    #mask = cv.imread('imgs\sofa_mask_rgb.png',0)               # 3: mask of furniture position
    drawnmask = cv.imread('imgs\sofa_drawnmask.png',0)          # 4: hand drawn mask
    wallpaper_mask = cv.imread('imgs\wallpaper_mask.png',0)     # 5: mask of wallpaper area
    
    # Function for applying the wallpaper to the selected section of the room according to our wallpaper mask
    def wallpaperReplacement(self):

        #calls function to fit wallpaper to img size
        self.wallpaperSizeFitting()

        # NEW REWRITE: CREATE MASK BASE FOR POLYGON
        mask_poly = np.zeros(self.room.shape[:2],np.uint8)


        #mask: initialize mask matrix
        mask = np.zeros(self.room.shape[:2],np.uint8)

        #editing mask matrix based on our input mask image
        mask[self.wallpaper_mask == 0] = cv.GC_FGD
        mask[self.wallpaper_mask == 255] = cv.GC_BGD

        #create clone of pic and bg
        self.bgdOut = self.room
        self.wp = self.wallpaper

        #Removes area where wallpaper will be applied
        self.wp_resized[mask == 1] = [0,0,0]

        #Crop area to apply to img as wallpaper
        #wp_in[mask == 1] = [0,0,0]
        self.bgdOut[mask == 0] = [0,0,0]

        #Combine the both
        #background = img_in + wp_in
        self.bgdOut = self.wp_resized + self.bgdOut

    def mousePointFunc(self,event,x,y,flags,param):
        if event == cv.EVENT_LBUTTONDOWN:
            if self.rect_over == False:
                print("first draw rectangle \n")
            else:
                self.drawing = True
                cv.circle(self.input, (x,y), 20, self.value['color'], -1)
                cv.circle(self.mask, (x,y), 20, self.value['val'], -1)
        return

    # Resize wallpaper to match img dimensions
    def wallpaperSizeFitting(self):

        self.wp_resized = np.zeros(self.input.shape, np.uint8)

        #crop the wallpaper to fit the dimensions of the image (if it is oversized)
        if self.wallpaper.shape[0] > self.room.shape[0] or self.wallpaper.shape[1] > self.room.shape[1]:
            self.wp_resized = self.wallpaper[0:self.room.shape[0],0:self.room.shape[1]]
        #iterates wallpaper to fill the dimensions of the image (if it is undersized)
        elif self.wallpaper.shape[0] < self.room.shape[0] or self.wallpaper.shape[1] < self.room.shape[1]:
            #another_wpmask = np.zeros((imgs_h,imgs_w),np.uint8)
            x_iter = self.room.shape[0] // self.wallpaper.shape[0]
            y_iter = self.room.shape[1] // self.wallpaper.shape[1]
            self.wp_resized = cv.repeat(self.wallpaper, x_iter, y_iter)
    
    # Function for combining the foreground and the background
    def combine(self):

        #create mask for fgd2bgd copying
        fgdCutout = np.zeros(self.room.shape[:2],np.uint8)
        fgdCutout[np.where((self.output!=[0,0,0]).all(axis=2))] = cv.GC_FGD
        fgdCutout[np.where((self.output==[0,0,0]).all(axis=2))] = cv.GC_BGD

        #replaces areas of fgd on the bgd with black
        self.bgdOut[fgdCutout != 0] = [0,0,0]

        self.final = self.output + self.bgdOut

    # Function for showing final output
    def show(self):
        cv.namedWindow('Output', cv.WINDOW_KEEPRATIO)
        cv.imshow('Output', self.final)
        cv.resizeWindow('Output', 1366, 768)
        cv.waitKey(0)
        cv.destroyAllWindows()
        cv.imwrite('grabcut_output.png', self.final)

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
            print(" Now press the key 'n' a few times until no further change \n")

        # draw touchup curves
        if event == cv.EVENT_LBUTTONDOWN:
            if self.rect_over == False:
                print("first draw rectangle \n")
            else:
                self.drawing = True
                cv.circle(self.input, (x,y), 20, self.value['color'], -1)
                cv.circle(self.mask, (x,y), 20, self.value['val'], -1)

        elif event == cv.EVENT_MOUSEMOVE:
            if self.drawing == True:
                cv.circle(self.input, (x, y), 20, self.value['color'], -1)
                cv.circle(self.mask, (x, y), 20, self.value['val'], -1)

        elif event == cv.EVENT_LBUTTONUP:
            if self.drawing == True:
                self.drawing = False
                cv.circle(self.input, (x, y), 20, self.value['color'], -1)
                cv.circle(self.mask, (x, y), 20, self.value['val'], -1)

    # Foreground(furniture) Cut
    def fgdCut(self):

        cv.namedWindow('Input',cv.WINDOW_KEEPRATIO)
        cv.namedWindow('Output',cv.WINDOW_KEEPRATIO)
        cv.setMouseCallback('Input', self.mouseDrawFunc)
        cv.moveWindow('input', self.room.shape[1]+10,90)

        print("Cut out the furniture")

        while(1):

            cv.imshow('Input', self.input)
            cv.resizeWindow('Input', 1366, 768)
            cv.imshow('Output', self.output)
            cv.resizeWindow('Output', 1366, 768)
            k = cv.waitKey(1)

            if k == 27:         # esc to exit
                break
            elif k == ord('q'): # BG drawing
                print(" mark background regions with left mouse button \n")
                self.value = self.DRAW_BG
            elif k == ord('w'): # FG drawing
                print(" mark foreground regions with left mouse button \n")
                self.value = self.DRAW_FG
            elif k == ord('m'): # reset everything
                print("resetting \n")
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
                    print("pass")
                    bgdModel = np.zeros((1,65),np.float64)
                    fgdModel = np.zeros((1,65),np.float64)
                    #grabcut with rect
                    if (self.rect_or_mask == 0):
                        cv.grabCut(self.room,self.mask,self.rect,bgdModel,fgdModel,1,cv.GC_INIT_WITH_RECT)
                        self.rect_or_mask = 1
                    #grabcut with mask
                    elif (self.rect_or_mask == 1):       
                        cv.grabCut(self.room,self.mask,self.rect,bgdModel,fgdModel,1,cv.GC_INIT_WITH_MASK)
                    print("done!")
                except:
                    import traceback
                    traceback.print_exc()

            mask2 = np.where((self.mask==2)|(self.mask==0),0,1).astype('uint8')
            self.output = self.room*mask2[:,:,np.newaxis]

        cv.destroyAllWindows()

    def init(self):

        # Init params
        self.input = self.room.copy()
        self.mask = mask = np.zeros(self.input.shape[:2],np.uint8)
        self.output = np.zeros(self.input.shape, np.uint8)

        #cut foreground(furniture) -> background(wall) -> combine them
        self.fgdCut()
        self.wallpaperReplacement()
        self.combine()
        self.show()

if __name__ == "__main__":
    print(__doc__)
    wallpaperCut().init()
   
    
