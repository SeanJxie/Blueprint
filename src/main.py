import pygame as pg
import sys
import math

import util

# Initialize systems
pg.init()
pg.font.init()

# --- Start constants ---
DISPLAY_SIZE  = util.get_display_size()
GRID_GAP_SIZE = math.gcd(*DISPLAY_SIZE) // 4 # math.gcd(*DISPLAY_SIZE) returns largest cell size
WIN_NAME      = "Blueprint"  # Program operates in fullscreen so...

MAINSURFACE    = pg.display.set_mode((0, 0), pg.FULLSCREEN)
DEFAULT_FONT   = pg.font.SysFont("ariel", 30)
MAX_FRAME_RATE = 60

BLUEPRINT_BLUE = (0,   20 , 132)
WHITE          = (255, 255, 255)
GRAY           = (100, 100, 100)
RED            = (255, 0  , 0  )
GREEN          = (0,   255, 0  )
BLACK          = (0  , 0  , 0  )

CURSOR_RAD        = 10
DRAW_LINE_WIDTH   = 2
DRAW_CIRCLE_WIDTH = 2

E_TYPE_LINE   = 0
E_TYPE_CIRCLE = 1

# --- End constants ---

# --- Start functions ---
def draw_base_grid(gap_size):
    for x in range(gap_size, DISPLAY_SIZE[0], gap_size):
        pg.draw.line(MAINSURFACE, GRAY, (x, 0), (x, DISPLAY_SIZE[1]), 1)
    for y in range(gap_size, DISPLAY_SIZE[1], gap_size):
        pg.draw.line(MAINSURFACE, GRAY, (0, y), (DISPLAY_SIZE[0], y), 1)


def draw_cursor(mPos):
    pg.draw.circle(MAINSURFACE, RED, mPos, 10)


def snap_to_grid(mPos):
    return GRID_GAP_SIZE * round(mPos[0] / GRID_GAP_SIZE), GRID_GAP_SIZE * round(mPos[1] / GRID_GAP_SIZE)


def distance(p1, p2):
    return ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5


def draw_all_shapes(lst):
    for shape in lst:
        shape_type = shape[2]
        if shape_type == E_TYPE_LINE:
            pg.draw.line(MAINSURFACE, WHITE, shape[0], shape[1], DRAW_LINE_WIDTH)
        elif shape_type == E_TYPE_CIRCLE:
            pg.draw.circle(MAINSURFACE, WHITE, shape[0], shape[1], DRAW_CIRCLE_WIDTH)


def draw_line_preview(start, mPos):
     pg.draw.line(MAINSURFACE, GREEN, start, mPos, DRAW_LINE_WIDTH)


def draw_circle_preview(center, r):
    pg.draw.circle(MAINSURFACE, GREEN, center, r, DRAW_CIRCLE_WIDTH)


def gui(draw_mode):
    if draw_mode == E_TYPE_LINE:
        draw_mode_gui =      DEFAULT_FONT.render(f"DRAW MODE: LINE"       , True, BLACK, WHITE)
    elif draw_mode == E_TYPE_CIRCLE:
        draw_mode_gui =      DEFAULT_FONT.render(f"DRAW MODE: CIRCLE"     , True, BLACK, WHITE)
    switch_line_gui   = DEFAULT_FONT.render('LINE: "L"'                   , True, BLACK, WHITE)
    switch_circle_gui = DEFAULT_FONT.render('CIRCLE: "C"'                 , True, BLACK, WHITE)
    undo_mode_gui     = DEFAULT_FONT.render('UNDO: "RIGHT MOUSE BUTTON"'  , True, WHITE, BLACK)
    clear_gui         = DEFAULT_FONT.render('CLEAR: "MIDDLE MOUSE BUTTON"', True, WHITE, BLACK)

    # TODO Positions are hard-coded
    MAINSURFACE.blit(draw_mode_gui    , (0, 0 ))
    MAINSURFACE.blit(switch_line_gui  , (0, 20))
    MAINSURFACE.blit(switch_circle_gui, (0, 40))
    MAINSURFACE.blit(undo_mode_gui    , (0, 60))
    MAINSURFACE.blit(clear_gui        , (0, 80))
# --- End functions ---


# Main program loop
def main():
    pg.display.set_caption(WIN_NAME)

    mousePos = [0, 0]
    preview = False

    # Stores all shape data in the form (v1, v2, draw_type)
    draw_list = []

    # Stores a drawable element in the form (v1, v2, draw_type)
    element = []

    # Default draw mode is line mode
    draw_mode = E_TYPE_LINE

    clock = pg.time.Clock()
    
    while 1:
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                # User exit
                if event.key == pg.K_ESCAPE:
                    pg.display.quit()
                    sys.exit(0)

                # Only allow draw mode changes if not in preview mode. Otherwise, stuff messes up.
                if not preview: 
                    if event.key == pg.K_l:
                        draw_mode = E_TYPE_LINE
                    elif event.key == pg.K_c:
                        draw_mode = E_TYPE_CIRCLE
                

            # User presses mouse button
            elif event.type == pg.MOUSEBUTTONDOWN:
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
                            element.append(E_TYPE_LINE) # Add element type
                            draw_list.append(element)      # Add element to draw list
                            preview = False                # Exit preview
                            element = []                   # Reset element


                    elif draw_mode == E_TYPE_CIRCLE:

                        # User defines center. Activate preview.
                        if len(element) == 0:
                            element.append(mousePos)
                            preview = True

                        # Similar process to line. Except second data value is a radius.
                        elif len(element) == 1:
                            element.append(distance(mousePos, element[0]))
                            element.append(E_TYPE_CIRCLE)
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

        # Get modified mouse position
        mousePos = snap_to_grid(pg.mouse.get_pos())

         # --- Start draw functions ---
        MAINSURFACE.fill(BLUEPRINT_BLUE)
        draw_base_grid(GRID_GAP_SIZE)
        draw_all_shapes(draw_list)
        if preview:
            if draw_mode == E_TYPE_LINE:
                draw_line_preview(element[0], mousePos)
            elif draw_mode == E_TYPE_CIRCLE:
                draw_circle_preview(element[0], distance(mousePos, element[0]))
        gui(draw_mode)
        draw_cursor(mousePos)
        # --- End draw functions ---

        # Update display
        pg.display.update()

        # No mouse
        pg.mouse.set_visible(False)

        # Tick
        clock.tick(MAX_FRAME_RATE)


# Run
if __name__ == "__main__":
    main()


