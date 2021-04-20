import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

# Import the images required into the script
room = cv.imread('imgs\sofa.jpg')                           # 1. img of room
wallpaper = cv.imread('imgs\space.jpg')                     # 2. wallpaper
mask = cv.imread('imgs\sofa_mask_rgb.png',0)                # 3. mask of furniture position
drawnmask = cv.imread('imgs\sofa_drawnmask.png',0)          # 4. hand drawn mask
wallpaper_mask = cv.imread('imgs\wallpaper_mask.png',0)     # 5. mask of wallpaper area
wp_tile = cv.imread('imgs\wp_tile.png')                     # 6. wallpaper tile

# Function for grabcut, which separates the foreground from the background; in this case, the furniture
def grabcut(img_in,mask_in):

    #mask: initialize mask matrix
    mask = np.zeros(img_in.shape[:2],np.uint8)

    #bgmModel, fgdModel: temp arrays for model
    bgdModel = np.zeros((1,65),np.float64)
    fgdModel = np.zeros((1,65),np.float64)

    #rect: area of possible foreground
    #rect = (500,500,3000,2500)

    #editing mask matrix based on our input mask image
    mask[mask_in == 0] = cv.GC_BGD
    mask[mask_in == 255] = cv.GC_FGD

    #grabcut function
    cv.grabCut(img_in,mask,None,bgdModel,fgdModel,5,cv.GC_INIT_WITH_MASK)

    mask2 = np.where((mask==2)|(mask==0),0,1).astype('uint8')
    foreground = img_in*mask2[:,:,np.newaxis]
    return foreground

# Function for applying the wallpaper to the selected section of the room according to our wallpaper mask
def wallpaperReplacement(img_in,wp_in,mask_in):

    #calls function to fit wallpaper to img size
    wp_in = wallpaperSizeFitting(wp_in,img_in.shape[0],img_in.shape[1])

    #mask: initialize mask matrix
    mask = np.zeros(img_in.shape[:2],np.uint8)

    #editing mask matrix based on our input mask image
    mask[mask_in == 0] = cv.GC_FGD
    mask[mask_in == 255] = cv.GC_BGD

    #Removes area where wallpaper will be applied
    img_in[mask == 0] = [0,0,0]

    #Crop area to apply to img as wallpaper
    wp_in[mask == 1] = [0,0,0]

    #Combine the both
    background = img_in + wp_in
    return background

# Resize wallpaper to match img dimensions
def wallpaperSizeFitting(wp,imgs_h,imgs_w):

    wp_out = wp

    #crop the wallpaper to fit the dimensions of the image (if it is oversized)
    if wp.shape[0] > imgs_h or wp.shape[1] > imgs_w:
        wp_out = wp[0:imgs_h,0:imgs_w]
    #iterates wallpaper to fill the dimensions of the image (if it is undersized)
    elif wp.shape[0] < imgs_h or wp.shape[1] < imgs_w:
        another_wpmask = np.zeros((imgs_h,imgs_w),np.uint8)
        x_iter = imgs_h // wp_tile.shape[0]
        y_iter = imgs_w // wp_tile.shape[1]
        wp_out = cv.repeat(wp_tile, x_iter, y_iter)
    
    return wp_out

# Function for combining the foreground and the background
def combine(fgd,bgd,fgd_mask):
    bgd[fgd_mask != 0] = [0,0,0]
    final = fgd + bgd
    return final

# Function for showing output
def show(img_in):
    cv.namedWindow('Output', cv.WINDOW_KEEPRATIO)
    cv.imshow('Output', img_in)
    cv.resizeWindow('Output', 1366, 768)
    cv.waitKey(0)
    cv.destroyAllWindows()

if __name__ == "__main__":
    output_fgd = grabcut(room,mask)
    output_bgd = wallpaperReplacement(room,wp_tile,wallpaper_mask)
    final = combine(output_fgd,output_bgd,mask)
    show(final)
    
    