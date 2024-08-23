from tkinter import *
import mouse
#Running this program will print an (x,y) pair that corresponds to where relative to the dimensions of the screen the mouse is
#If using this with ScratcherAPI: move mouse to specific part of the screen, alt tab and click F5. 
#   If you don't move the mouse, it will give you the right coordinates
#   (think of it like taking an x-ray, lining up the shot, standing still until it gives the result)
def main():
    findCoord()

#Will return the relative coordinate to the location your mouse is on when the program runs
def findCoord():
    tinker = Tk()
    screen_height = tinker.winfo_screenheight()
    screen_width = tinker.winfo_screenwidth()
    mouse_at = mouse.get_position()
    mouse_at = list(mouse_at)
    mouse_at[0] /= screen_width
    mouse_at[1] /= screen_height
    mouse_at = tuple(mouse_at)
    print(mouse_at)
    return mouse_at

if __name__=="__main__":
    main()