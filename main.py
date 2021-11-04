from tkinter import *

# TODO: add periodic boundary conditions


# a subclass of Canvas for dealing with resizing of windows
# https://stackoverflow.com/a/22837522/15484665
class ResizingCanvas(Canvas):
    def __init__(self, parent, **kwargs):
        Canvas.__init__(self,parent,**kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    def on_resize(self, event):
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width) / self.width
        hscale = float(event.height) / self.height
        self.width = event.width
        self.height = event.height
        # resize the canvas
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        self.scale("all", 0, 0, wscale, hscale)


class GameOfLife:
    # TODO: move this into init func
    # TODO: pick WIDTH and HEIGHT based on the size of the screen
    WIDTH = 750
    HEIGHT = 750

    WIDTH_COUNT = 20
    HEIGHT_COUNT = 20

    HORIZONTAL_SIZE = WIDTH / WIDTH_COUNT
    VERTICAL_SIZE = HEIGHT / HEIGHT_COUNT

    BACKGROUND_COLOR = 'white'
    RUNNING_COLOR = 'black'
    DRAWING_COLOR = '#545454'
    OUTLINE_COLOR = 'black'

    DRAWING_DELAY = 1

    def __init__(self):
        self.save_alive_cells = set()
        self.alive_cells = set()
        self.canvas_cells = []

        self.root = Tk()
        self.root.resizable(0, 0)
        self.frame = Frame(self.root)
        self.frame.pack(fill=BOTH, expand=YES)
        self.canvas = ResizingCanvas(self.frame, width=self.WIDTH, height=self.HEIGHT,
                                     bg=self.BACKGROUND_COLOR, highlightthickness=0)
        self.canvas.pack(fill=BOTH, expand=YES)

        self.canvas.bind("<Key>", self.key_pressed)
        self.canvas.focus_set()
        self.canvas.bind("<Button-1>", self.mouse_clicked)
        self.canvas.bind("<B1-Motion>", self.mouse_moved)
        self.canvas.bind("<ButtonRelease-1>", self.mouse_released)
        self.canvas.bind("<MouseWheel>", self.mouse_wheel_callback)

        self.init_cells()

        self.running = False
        self.alive_cell_selected = None

        # Number of frames per second
        # TODO: move to init (double check the value > 0)
        self.fps = 120
        self.running_delay = int(1000 / self.fps)

    def run(self):
        """Begins the simulation"""
        self.save_alive_cells = self.alive_cells.copy()
        self.running = True

    def stop(self):
        """Ends the simulation"""
        self.alive_cells.clear()
        self.running = False

    def reset(self):
        """Restores the state before the beginning of the simulation"""
        self.alive_cells = self.save_alive_cells
        self.running = False

    def init_cells(self):
        """Initializes internal structure for storing GUI cells"""
        for i in range(self.HEIGHT_COUNT):
            temp_list = []
            for j in range(self.WIDTH_COUNT):
                temp_list.append(self.canvas.create_rectangle(self.HORIZONTAL_SIZE * j, self.VERTICAL_SIZE * i,
                                 self.HORIZONTAL_SIZE * (j + 1), self.VERTICAL_SIZE * (i + 1),
                                 fill=self.BACKGROUND_COLOR, outline=self.OUTLINE_COLOR))
            self.canvas_cells.append(temp_list)

    def mainloop(self):
        self.refresh()
        self.root.mainloop()

    def key_pressed(self, event):
        if event.char == ' ':
            if self.running:
                self.reset()
            else:
                self.run()
        # Backspace is pressed
        elif event.char == '\x7f':
            self.stop()

    def mouse_clicked(self, event):
        if self.running:
            return

        coords = self.cell_coord(event.y, event.x)
        self.alive_cell_selected = coords in self.alive_cells

        if coords in self.alive_cells:
            self.alive_cells.remove(coords)
        else:
            self.alive_cells.add(coords)

    def mouse_moved(self, event):
        if self.running:
            return

        coords = self.cell_coord(event.y, event.x)
        if self.alive_cell_selected:
            if coords in self.alive_cells:
                self.alive_cells.remove(coords)
        else:
            self.alive_cells.add(coords)

    def mouse_released(self, _event):
        self.alive_cell_selected = None

    def mouse_wheel_callback(self, event):
        print(event.delta)

    def cell_coord(self, y, x):
        """
        Given coordinates (x, y) in the window, return the coordinates of the cell this point is in. Assume that,
        in returned coordinates, (HORIZONTAL_SIZE, 0) and (0, VERTICAL_SIZE) are basis vectors.
        """
        return int(y / self.VERTICAL_SIZE), int(x / self.HORIZONTAL_SIZE)

    def count_neighbours(self, i, j):
        possible_neighbours = self.get_neighbours(i, j)
        return len(possible_neighbours & self.alive_cells)

    @staticmethod
    def get_neighbours(i, j):
        return {(i, j - 1), (i, j + 1), (i - 1, j - 1), (i + 1, j - 1), (i - 1, j + 1), (i + 1, j + 1), (i + 1, j),
                (i - 1, j)}

    def is_dead(self, i, j):
        return (i, j) not in self.alive_cells

    def survives_check(self, i, j):
        return self.count_neighbours(i, j) in (2, 3)

    def reproduction_check(self, i, j):
        return self.count_neighbours(i, j) == 3

    def tick(self):
        to_add = set()
        to_remove = set()
        for i, j in self.alive_cells:
            if not self.survives_check(i, j):
                to_remove.add((i, j))
            for ni, nj in self.get_neighbours(i, j):
                if self.is_dead(ni, nj) & self.reproduction_check(ni, nj):
                    to_add.add((ni, nj))
        self.alive_cells = self.alive_cells.union(to_add)
        self.alive_cells = self.alive_cells.symmetric_difference(to_remove)

    def clear(self):
        for i in self.canvas_cells:
            for j in i:
                self.canvas.itemconfig(j, fill=self.BACKGROUND_COLOR)

# TODO: add start/stop buttons and speed control.
# TODO: add scrolling feature

    def refresh(self):
        self.clear()

        color = self.DRAWING_COLOR
        delay = self.DRAWING_DELAY
        if self.running:
            color = self.RUNNING_COLOR
            delay = self.running_delay
            self.tick()
            if len(self.alive_cells) == 0:
                self.reset()

        for i, j in self.alive_cells:
            if (not (0 <= i < self.HEIGHT_COUNT)) or (not (0 <= j < self.WIDTH_COUNT)):
                continue
            self.canvas.itemconfig(self.canvas_cells[i][j], fill=color)

        self.root.after(delay, self.refresh)


def main():
    game = GameOfLife()
    game.mainloop()


if __name__ == '__main__':
    main()
