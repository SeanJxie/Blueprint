import pygame as pg
from pygame import gfxdraw  # For antialias functions and more precise draw functions overall.
import sys, os
import math

import util

"""

A shape constructor

--- New ---
- Resolution-based font size
- float values for length and radius
- Small font type
- Bezier curves

"""


# Initialize systems
pg.init()
pg.font.init()


# --- Start constants ---
DISPLAY_SIZE  = util.get_display_size()
WIN_NAME      = "Blueprint" 

ASSET_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "menu_img.png")
MENU_TEXTURE = pg.transform.scale(pg.image.load(ASSET_PATH), DISPLAY_SIZE)

MAINSURFACE     = pg.display.set_mode((0, 0), pg.FULLSCREEN)
ACTIVE_GUI_FONT = pg.font.SysFont("monospace", int(DISPLAY_SIZE[1] * 0.035)) # Special number 0.035 is based on what my resolution returns 50
SMALL_GUI_FONT  = pg.font.SysFont("monospace", int(DISPLAY_SIZE[1] * 0.035 / 2))
MAX_FRAME_RATE  = 120

# All levels of zoom are such that the grid evenly divides the display. Therefore, all cell sizes are
# common multiples of DISPLAY_SIZE dimensions.
GRID_ZOOM_CYCLE = util.get_zoom_cycle(*DISPLAY_SIZE)

BLUEPRINT_BLUE = (0  , 20 , 132)
WHITE          = (255, 255, 255)
GRAY           = (100, 100, 100)
RED            = (255, 0  , 0  )
GREEN          = (0  , 255, 0  )
BLACK          = (0  , 0  , 0  )
YELLOW         = (255, 255, 0  )

CURSOR_RAD          = 10
CURSOR_WIDTH        = 2
CURSOR_POS_ROUND_TO = 4

# With the new gfx functions, no width args
#DRAW_LINE_WIDTH    = 2
#DRAW_CIRCLE_WIDTH  = 2
BEZIER_INTERP_STEPS = 10

E_TYPE_LINE   = 0
E_TYPE_CIRCLE = 1
E_TYPE_BEZIER = 2
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
        shape_type = shape[-1]
        if shape_type == E_TYPE_LINE:
            pg.gfxdraw.line(MAINSURFACE, *shape[0], *shape[1], WHITE)
        elif shape_type == E_TYPE_CIRCLE: 
            pg.gfxdraw.aacircle(MAINSURFACE, *shape[0], int(shape[1]), WHITE)
        elif shape_type == E_TYPE_BEZIER:
            # shape[:-1] specifies all points, excluding shape type
            pg.gfxdraw.bezier(MAINSURFACE, shape[:-1], BEZIER_INTERP_STEPS, WHITE)


def draw_line_preview(start, mPos):
     pg.gfxdraw.line(MAINSURFACE, *start, *mPos, GREEN)

     len_gui = ACTIVE_GUI_FONT.render(f"len={round(util.distance(start, mPos), CURSOR_POS_ROUND_TO)}", True, WHITE)
     MAINSURFACE.blit(len_gui, (mPos[0] + CURSOR_RAD, mPos[1]))


def draw_circle_preview(center, r, mPos):
    pg.draw.circle(MAINSURFACE, GREEN, center, int(r), 1)

    radius_gui = ACTIVE_GUI_FONT.render(f"r={round(r, CURSOR_POS_ROUND_TO)}", True, WHITE)
    MAINSURFACE.blit(radius_gui, (mPos[0] + CURSOR_RAD, mPos[1]))


def draw_bezier_preview(pLst, mPos):
    # Draw points
    for i in range(len(pLst)):
        pg.gfxdraw.filled_circle(MAINSURFACE, pLst[i][0], pLst[i][1], CURSOR_RAD, YELLOW)
        p_gui = SMALL_GUI_FONT.render(f"Point #{i + 1} {pLst[i]}", True, YELLOW)
        MAINSURFACE.blit(p_gui, (pLst[i][0] + CURSOR_RAD, pLst[i][1]))
    
    # If greater than or equal to 2 points, draw line.
    if len(pLst) >= 2:
        pg.draw.lines(MAINSURFACE, YELLOW, False, pLst + [mPos])

    # If greater than or equal to 3 points, draw bezier.
    if len(pLst) >= 3:
        pg.gfxdraw.bezier(MAINSURFACE, pLst + [mPos], BEZIER_INTERP_STEPS, GREEN)


def menu_gui():
    MAINSURFACE.blit(MENU_TEXTURE, (0, 0))


def active_gui(draw_mode, mPos):
    if draw_mode == E_TYPE_LINE:
        draw_mode_gui = ACTIVE_GUI_FONT.render("DRAW MODE: LINE"        , True, RED, WHITE)
    elif draw_mode == E_TYPE_CIRCLE:
        draw_mode_gui = ACTIVE_GUI_FONT.render("DRAW MODE: CIRCLE"      , True, RED, WHITE)
    elif draw_mode == E_TYPE_BEZIER:
        draw_mode_gui = ACTIVE_GUI_FONT.render("DRAW MODE: BÉZIER CURVE", True, RED, WHITE)

    mouse_pos_gui     = ACTIVE_GUI_FONT.render(f"{mPos}"                , True, BLACK, WHITE)

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
    show_menu   = True  # This statement is scattered around. Defines menu state and active program state.
    show_gui    = True
    show_grid   = True
    show_cursor = True

    # Stores all shape data
    draw_list = []

    # Stores a drawable element data
    # E_TYPE_LINE:   (start, end, type)
    # E_TYPE_CIRCLE: (center, radius, type)
    # E_TYPE_BEZIER: (*points, type)
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

                # Only toggle that operates both in and out of menu is the menu toggle
                elif event.key == pg.K_m:
                    show_menu = not show_menu

                    # Mouse visibility depends on menu state
                    pg.mouse.set_visible(show_menu)

                # All the controls that do not function in when in menu
                if not show_menu:
                    # Increase and decrease cell size
                    if event.key == pg.K_UP:
                        grid_zoom_idx = (grid_zoom_idx - 1) % len(GRID_ZOOM_CYCLE)

                    elif event.key == pg.K_DOWN:
                        grid_zoom_idx = (grid_zoom_idx + 1) % len(GRID_ZOOM_CYCLE)
                    
                    # Toggle controls
                    elif event.key == pg.K_f:
                        show_gui = not show_gui

                    elif event.key == pg.K_g:
                        show_grid = not show_grid

                    elif event.key == pg.K_x:
                        show_cursor = not show_cursor

                    # Draw mode controls
                    elif event.key == pg.K_l:
                        element = element[:1] # Since 
                        draw_mode = E_TYPE_LINE
                        
                    elif event.key == pg.K_c:
                        element = element[:1]
                        draw_mode = E_TYPE_CIRCLE

                    elif event.key == pg.K_b:
                        draw_mode = E_TYPE_BEZIER
                    

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

                        elif draw_mode == E_TYPE_BEZIER:
                            element.append(mousePos)
                            # We need at least 3 points to draw to curve.
                            if len(element) == 1:
                                preview = True

                            # element[-1] == element[-2] detects double click. If so, curve has been defined.
                            if len(element) >= 3 and element[-1] == element[-2]:
                                draw_list.append(element)
                                element.append(E_TYPE_BEZIER)
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

                elif draw_mode == E_TYPE_BEZIER:
                    draw_bezier_preview(element, mousePos)

            if show_gui:
                active_gui(draw_mode, mousePos)

            if show_cursor:
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


