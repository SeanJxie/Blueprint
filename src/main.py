import pygame as pg
import sys

import util

"""

A shape constructor

TODO: Navigation
      Hide grid

"""


# Initialize systems
pg.init()
pg.font.init()


# --- Start constants ---
DISPLAY_SIZE  = util.get_display_size()
WIN_NAME      = "Blueprint"  # Program operates in fullscreen so...

MAINSURFACE    = pg.display.set_mode((0, 0), pg.FULLSCREEN)
DEFAULT_FONT   = pg.font.SysFont("ariel", 50)
MAX_FRAME_RATE = 60

# A cell size of 1 or 2 would make the computer not happy :(
MIN_CELL_SIZE   = 3
# All levels of zoom are such that the grid evenly divides the display. Therefore, all cell sizes are
# common multiples of DISPLAY_SIZE dimensions.
GRID_ZOOM_CYCLE = util.get_all_cd(MIN_CELL_SIZE, *DISPLAY_SIZE)

BLUEPRINT_BLUE = (0  , 20 , 132)
WHITE          = (255, 255, 255)
GRAY           = (100, 100, 100)
RED            = (255, 0  , 0  )
GREEN          = (0  , 255, 0  )
BLACK          = (0  , 0  , 0  )

CURSOR_RAD          = 10
CURSOR_WIDTH        = 2
CURSOR_POS_ROUND_TO = 2

DRAW_LINE_WIDTH   = 2
DRAW_CIRCLE_WIDTH = 2

E_TYPE_LINE   = 0
E_TYPE_CIRCLE = 1
# --- End constants ---


# --- Start functions ---
def draw_base_grid(cell_size):
    for x in range(cell_size, DISPLAY_SIZE[0], cell_size):
        pg.draw.line(MAINSURFACE, GRAY, (x, 0), (x, DISPLAY_SIZE[1]), 1)

    for y in range(cell_size, DISPLAY_SIZE[1], cell_size):
        pg.draw.line(MAINSURFACE, GRAY, (0, y), (DISPLAY_SIZE[0], y), 1)


def draw_cursor(mPos):
    pg.draw.circle(MAINSURFACE, RED, mPos, CURSOR_RAD, CURSOR_WIDTH)


def snap_to_grid(cell_size, mPos):
    return cell_size * round(mPos[0] / cell_size), cell_size * round(mPos[1] / cell_size)


def draw_all_shapes(lst):
    for shape in lst:
        shape_type = shape[2]
        if shape_type == E_TYPE_LINE:
            pg.draw.line(MAINSURFACE, WHITE, shape[0], shape[1], DRAW_LINE_WIDTH)
        elif shape_type == E_TYPE_CIRCLE:
            pg.draw.circle(MAINSURFACE, WHITE, shape[0], shape[1], DRAW_CIRCLE_WIDTH)


def draw_line_preview(start, mPos):
     pg.draw.line(MAINSURFACE, GREEN, start, mPos, DRAW_LINE_WIDTH)

     len_gui = DEFAULT_FONT.render(f"len={round(util.distance(start, mPos), CURSOR_POS_ROUND_TO)}", True, WHITE)
     MAINSURFACE.blit(len_gui, (mPos[0] + CURSOR_RAD, mPos[1]))


def draw_circle_preview(center, r, mPos):
    pg.draw.circle(MAINSURFACE, GREEN, center, r, DRAW_CIRCLE_WIDTH)

    radius_gui = DEFAULT_FONT.render(f"r: {round(r, CURSOR_POS_ROUND_TO)}", True, WHITE)
    MAINSURFACE.blit(radius_gui, (mPos[0] + CURSOR_RAD, mPos[1]))


def gui(draw_mode, mPos):
    if draw_mode == E_TYPE_LINE:
        draw_mode_gui = DEFAULT_FONT.render("DRAW MODE: LINE"              , True, BLACK, WHITE)
    elif draw_mode == E_TYPE_CIRCLE:
        draw_mode_gui = DEFAULT_FONT.render("DRAW MODE: CIRCLE"            , True, BLACK, WHITE)
    switch_line_gui   = DEFAULT_FONT.render('LINE: "L"'                    , True, BLACK, WHITE)
    switch_circle_gui = DEFAULT_FONT.render('CIRCLE: "C"'                  , True, BLACK, WHITE)
    hide_gui_gui      = DEFAULT_FONT.render('HIDE GUI: "H"'                , True, BLACK, WHITE)
    cell_size_gui     = DEFAULT_FONT.render('CHANGE CELL SIZE: "UP"/"DOWN"', True, BLACK, WHITE)
    undo_mode_gui     = DEFAULT_FONT.render('UNDO: "RIGHT MOUSE BUTTON"'   , True, BLACK, WHITE)
    clear_gui         = DEFAULT_FONT.render('CLEAR: "MIDDLE MOUSE BUTTON"' , True, BLACK, WHITE)
    exit_gui          = DEFAULT_FONT.render('EXIT: "ESC"'                  , True, BLACK, WHITE)
    mouse_pos_gui     = DEFAULT_FONT.render(f'CURSOR POS: {mPos}'          , True, BLACK, WHITE)

    # TODO Positions are hard-coded
    MAINSURFACE.blit(draw_mode_gui    , (0, 0  ))
    MAINSURFACE.blit(switch_line_gui  , (0, 100))
    MAINSURFACE.blit(switch_circle_gui, (0, 200))
    MAINSURFACE.blit(hide_gui_gui     , (0, 300))
    MAINSURFACE.blit(cell_size_gui    , (0, 400))
    MAINSURFACE.blit(undo_mode_gui    , (0, 500))
    MAINSURFACE.blit(clear_gui        , (0, 600))
    MAINSURFACE.blit(exit_gui         , (0, 700))
    MAINSURFACE.blit(mouse_pos_gui    , (0, 800))
# --- End functions ---


# Main program loop
def main():
    pg.display.set_caption(WIN_NAME)

    mousePos = [0, 0]
    preview = False
    show_gui = True

    # Stores all shape data in the form (v1, v2, draw_type)
    draw_list = []

    # Stores a drawable element in the form (v1, v2, draw_type)
    element = []

    # Default draw mode is line mode
    draw_mode = E_TYPE_LINE

    # Start index of zoom cycle
    grid_zoom_idx = -1

    clock = pg.time.Clock()
    
    while 1:
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                # User exit
                if event.key == pg.K_ESCAPE:
                    pg.display.quit()
                    sys.exit(0)

                # Toggle gui
                elif event.key == pg.K_h:
                    show_gui = not show_gui

                # Increase and decrease cell size
                elif event.key == pg.K_UP:
                    grid_zoom_idx = (grid_zoom_idx + 1) % len(GRID_ZOOM_CYCLE)

                elif event.key == pg.K_DOWN:
                    grid_zoom_idx = (grid_zoom_idx - 1) % len(GRID_ZOOM_CYCLE)


                # Only allow draw mode changes if not in preview mode. Otherwise, stuff messes up.
                else: 
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

        # Get modified mouse position
        mousePos = snap_to_grid(GRID_ZOOM_CYCLE[grid_zoom_idx], pg.mouse.get_pos())

         # --- Start draw functions ---
        MAINSURFACE.fill(BLUEPRINT_BLUE)
        draw_base_grid(GRID_ZOOM_CYCLE[grid_zoom_idx])
        draw_all_shapes(draw_list)
        if preview:
            if draw_mode == E_TYPE_LINE:
                draw_line_preview(element[0], mousePos)
            elif draw_mode == E_TYPE_CIRCLE:
                draw_circle_preview(element[0], util.distance(mousePos, element[0]), mousePos)
        if show_gui:
            gui(draw_mode, mousePos)
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


