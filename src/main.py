import pygame as pg
from pygame import gfxdraw  # For antialias functions and more precise draw functions overall.
import sys, os
import math

import util

"""

A shape constructor

"""

# Initialize systems
pg.init()
pg.font.init()


# --- Start constants ---
DISPLAY_SIZE  = util.get_display_size()
WIN_NAME      = "Blueprint"  # Program operates in fullscreen so...

# This is one way to do it...
ASSET_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "menu_img.PNG")

MAINSURFACE     = pg.display.set_mode((0, 0), pg.FULLSCREEN)
ACTIVE_GUI_FONT = pg.font.SysFont("monospace", 50)
MAX_FRAME_RATE  = 60

# All levels of zoom are such that the grid evenly divides the display. Therefore, all cell sizes are
# common multiples of DISPLAY_SIZE dimensions.
GRID_ZOOM_CYCLE = util.get_zoom_cycle(*DISPLAY_SIZE)

BLUEPRINT_BLUE = (0  , 20 , 132)
WHITE          = (255, 255, 255)
GRAY           = (100, 100, 100)
RED            = (255, 0  , 0  )
GREEN          = (0  , 255, 0  )
BLACK          = (0  , 0  , 0  )

CURSOR_RAD          = 10
CURSOR_WIDTH        = 2
CURSOR_POS_ROUND_TO = 4

DRAW_LINE_WIDTH   = 2
DRAW_CIRCLE_WIDTH = 2

E_TYPE_LINE   = 0
E_TYPE_CIRCLE = 1
E_TYPE_ARC    = 2
# --- End constants ---


# --- Start functions ---
def draw_base_grid(cell_size):
    for x in range(cell_size, DISPLAY_SIZE[0], cell_size):
        pg.draw.line(MAINSURFACE, GRAY, (x, 0), (x, DISPLAY_SIZE[1]), 1)

    for y in range(cell_size, DISPLAY_SIZE[1], cell_size):
        pg.draw.line(MAINSURFACE, GRAY, (0, y), (DISPLAY_SIZE[0], y), 1)


def draw_cursor(mPos):
    pg.gfxdraw.aacircle(MAINSURFACE, *mPos, CURSOR_RAD, RED)


def snap_to_grid(cell_size, mPos):
    return cell_size * round(mPos[0] / cell_size), cell_size * round(mPos[1] / cell_size)


def draw_all_shapes(lst):
    for shape in lst:
        shape_type = shape[2]
        if shape_type == E_TYPE_LINE:
            pg.gfxdraw.line(MAINSURFACE, *shape[0], *shape[1], WHITE)
        elif shape_type == E_TYPE_CIRCLE:
            pg.gfxdraw.aacircle(MAINSURFACE, *shape[0], shape[1], WHITE)


def draw_line_preview(start, mPos):
     pg.gfxdraw.line(MAINSURFACE, *start, *mPos, GREEN)

     len_gui = ACTIVE_GUI_FONT.render(f"len={round(util.distance(start, mPos), CURSOR_POS_ROUND_TO)}", True, WHITE)
     MAINSURFACE.blit(len_gui, (mPos[0] + CURSOR_RAD, mPos[1]))


def draw_circle_preview(center, r, mPos):
    pg.gfxdraw.aacircle(MAINSURFACE, *center, r, GREEN)

    radius_gui = ACTIVE_GUI_FONT.render(f"r={round(r, CURSOR_POS_ROUND_TO)}", True, WHITE)
    MAINSURFACE.blit(radius_gui, (mPos[0] + CURSOR_RAD, mPos[1]))


def draw_arc_preview(center, r, sDeg, mPos):
    pass


def menu_gui():
    print(ASSET_PATH)
    menu_img = pg.image.load(ASSET_PATH)
    menu_img = pg.transform.scale(menu_img, DISPLAY_SIZE)
    MAINSURFACE.fill(WHITE)
    MAINSURFACE.blit(menu_img, (0, 0))


def active_gui(draw_mode, mPos):
    if draw_mode == E_TYPE_LINE:
        draw_mode_gui = ACTIVE_GUI_FONT.render("DRAW MODE: LINE"  , True, RED, WHITE)
    elif draw_mode == E_TYPE_CIRCLE:
        draw_mode_gui = ACTIVE_GUI_FONT.render("DRAW MODE: CIRCLE", True, RED, WHITE)

    mouse_pos_gui     = ACTIVE_GUI_FONT.render(f"{mPos}"          , True, BLACK, WHITE)

    # TODO Positions are hard-coded
    MAINSURFACE.blit(draw_mode_gui, (0, 0 ))
    MAINSURFACE.blit(mouse_pos_gui, (0, 50))
# --- End functions ---


# Main program loop
def main():
    pg.display.set_caption(WIN_NAME)

    mousePos = [0, 0]

    # GUI vars
    preview     = False
    show_menu   = True # This statement is scattered around. Defines menu state and active program state.
    show_gui    = True
    show_grid   = True

    # Stores all shape data in the form (v1, v2, draw_type)
    draw_list = []

    # Stores a drawable element in the form (v1, v2, draw_type)
    element = []

    # ACTIVE_GUI draw mode is line mode
    draw_mode = E_TYPE_LINE

    # Start index of zoom cycle
    grid_zoom_idx = 0

    clock = pg.time.Clock()
    
    while 1:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.display.quit()
                sys.exit(0)

            if event.type == pg.KEYDOWN:
                # User exit
                if event.key == pg.K_ESCAPE:
                    pg.display.quit()
                    sys.exit(0)

                # Toggle gui
                elif event.key == pg.K_m:
                    show_menu = not show_menu
                    # Mouse visibility depends on show_menu
                    pg.mouse.set_visible(show_menu)

                if not show_menu:
                    # Increase and decrease cell size
                    if event.key == pg.K_UP:
                        grid_zoom_idx = (grid_zoom_idx - 1) % len(GRID_ZOOM_CYCLE)

                    elif event.key == pg.K_DOWN:
                        grid_zoom_idx = (grid_zoom_idx + 1) % len(GRID_ZOOM_CYCLE)
                    
                    elif event.key == pg.K_f:
                        show_gui = not show_gui

                    elif event.key == pg.K_l:
                        draw_mode = E_TYPE_LINE
                        
                    elif event.key == pg.K_c:
                        draw_mode = E_TYPE_CIRCLE

                    elif event.key == pg.K_g:
                        show_grid = not show_grid
    

            # User presses mouse button
            elif event.type == pg.MOUSEBUTTONDOWN:
                if not show_menu:
                    button = pg.mouse.get_pressed() # Returns (middle, right, left) boolean tuple

                    # User places point at cursor
                    if button[0]: # Left

                        if draw_mode == E_TYPE_LINE:

                            # User defines start. Activate preview
                            if len(element) == 0:
                                element.append(mousePos)
                                preview = True

                            elif len(element) == 1:            # User has placed second point
                                element.append(mousePos)       # Add point to element
                                element.append(E_TYPE_LINE)    # Add element type

                                # Check if element already exists.
                                if element not in draw_list:
                                    draw_list.append(element)  # Add element to draw list

                                preview = False                # Exit preview
                                element = []                   # Reset element


                        elif draw_mode == E_TYPE_CIRCLE:

                            # User defines center. Activate preview.
                            if len(element) == 0:
                                element.append(mousePos)
                                preview = True

                            # Similar process to line. Except second data value is a radius.
                            elif len(element) == 1:
                                element.append(util.distance(mousePos, element[0]))
                                element.append(E_TYPE_CIRCLE)
                                if element not in draw_list:
                                    draw_list.append(element)
                                preview = False
                                element = []
                            

                    elif button[2]: # Right
                        if preview:          # If in preview mode
                            preview = False  # Exit preview
                            element = []     # Reset element

                        elif draw_list:       # If not in preview mode and line is not empty
                            draw_list.pop(-1) # Remove latest element

                    elif button[1]: # Middle 
                        draw_list = [] # Clear 

        if not show_menu:
            # Get modified mouse position
            mousePos = snap_to_grid(GRID_ZOOM_CYCLE[grid_zoom_idx], pg.mouse.get_pos())

            # --- Start draw functions ---
            MAINSURFACE.fill(BLUEPRINT_BLUE)
            if show_grid:
                draw_base_grid(GRID_ZOOM_CYCLE[grid_zoom_idx])

            draw_all_shapes(draw_list)

            if preview:
                if draw_mode == E_TYPE_LINE:
                    draw_line_preview(element[0], mousePos)

                elif draw_mode == E_TYPE_CIRCLE:
                    draw_circle_preview(element[0], util.distance(mousePos, element[0]), mousePos)

            if show_gui:
                active_gui(draw_mode, mousePos)

            draw_cursor(mousePos)

        else:
            menu_gui()
        # --- End draw functions ---

        # Update display
        pg.display.update()

        

        # Tick
        clock.tick(MAX_FRAME_RATE)


# Run
if __name__ == "__main__":
    main()


