#!/usr/bin/python
# TODO: add victory condition
# victory condition is that number of explored cells + number of placed flags
# is
# TODO: streamline drawing of cells
import datetime
import random
import time

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject

class MinesweeperSquare(object):
    def __init__(self):
        self.explored = False
        self.bomb = False
        self.flag = False
        self.neighboring_bombs = 0

class Minesweeper_model(object):
    def __init__(self, icols, irows, ibombs):
        self.cols = max(1, icols)
        self.rows = max(1, irows)
        self.num_bombs = max(0, min(ibombs, (self.cols * self.rows) - 1))
        self.placed_flags = 0
        self.explored_squares = 0
        self.data = [
            [MinesweeperSquare() for _i in range(self.cols)]
            for _j in range(self.rows)
        ]
        rand = random.SystemRandom()
        placed_bombs = 0
        place_col = 0
        place_row = 0
        while placed_bombs < self.num_bombs:
            place_col = rand.randint(0, self.cols - 1)
            place_row = rand.randint(0, self.rows - 1)
            if self.data[place_row][place_col].bomb:
                continue  # loop back to the while
            self.data[place_row][place_col].bomb = True
            placed_bombs = placed_bombs + 1
        self.update_neighboring_bombs()

    def check_victory_condition(self):
        """if you explored or flagged everything you win"""
        return self.placed_flags + self.explored_squares == self.cols * self.rows

    def update_neighboring_bombs(self):
        for jcol in xrange(self.cols):
            for irow in xrange(self.rows):
                self.data[irow][jcol].neighboring_bombs = 0
        for jcol in xrange(self.cols):
            for irow in xrange(self.rows):
                if self.data[irow][jcol].bomb:
                    self.increment_neighbors(irow, jcol)

    def increment_neighbors(self, irow, icol):
        for row in range(max(0, irow - 1), min(irow + 1 + 1, self.rows), 1):
            for col in range(max(0, icol - 1), min(icol + 1 + 1, self.cols), 1):
                self.data[row][col].neighboring_bombs = self.data[row][col].neighboring_bombs + 1


class MinesweeperWindow(Gtk.Window, Minesweeper_model):
    def __init__(self, my_model):
        Gtk.Window.__init__(self, title="Yet Another Minesweeper")
        self.model = my_model
        self.timeout_id = GObject.timeout_add(300, self.on_timeout)
        self.set_default_size(self.model.cols * 50, self.model.rows * 50)
        self.set_default_size(0, 0)
        self.set_resizable(False)
        self.set_border_width(5)
        vbox = Gtk.VBox(False, 10)
        hbox = Gtk.HBox(True, 5)
        valign = Gtk.Alignment()
        halign = Gtk.Alignment()
        halign.add(hbox)
        vbox.pack_start(valign, False, False, 0)
        vbox.pack_start(halign, False, False, 0)
        self.flag_counter = Gtk.Label("Flag Counter")
        hbox.pack_start(self.flag_counter, False, False, 0)
        self.update_flag_counter()
        self.smiley = Gtk.Button()
        self.smiley.set_image(Gtk.Image.new_from_file("icons/smiley.png"))
        self.smiley.set_label("")
        self.smiley.connect('button-release-event', self.game_reset)
        hbox.pack_start(self.smiley, False, False, 0)
        self.timer = Gtk.Label("Timer")
        hbox.pack_start(self.timer, False, False, 0)
        self.grid = Gtk.Grid()
        vbox.pack_start(self.grid, False, False, 0)
        self.add(vbox)
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
        self.last_right_click = datetime.datetime.now()
        self.last_left_click = datetime.datetime.now()
        self.last_unclick = datetime.datetime.now()
        self.game_start = datetime.datetime.now()
        self.game_active = True
        for jcol in xrange(self.model.cols):
            for irow in xrange(self.model.rows):
                content = ""
                button = Gtk.Button(label=content)
                button.set_image(Gtk.Image.new_from_file("icons/empty.png"))
                button.connect('button-press-event', self.on_click, irow, jcol)
                button.connect('button-release-event', self.on_unclick, irow, jcol)
                button.connect('enter-notify-event', self.null_action)
                button.connect('style-set', self.style_set_action)
                button.connect('style-updated', self.style_update_action, 1)
                button.set_property("can-focus", False)
                button.set_property("has-focus", False)
                self.grid.attach(button, jcol - 1, irow - 1, 1, 1)

    def game_reset(self, widget, event):
        self.model = Minesweeper_model(self.model.rows, self.model.cols, self.model.num_bombs)
        self.smiley.set_image(Gtk.Image.new_from_file("icons/smiley.png"))
        self.game_active = True
        self.game_start = datetime.datetime.now()
        for jcol in xrange(self.model.cols):
            for irow in xrange(self.model.rows):
                button = self.grid.get_child_at(jcol - 1, irow - 1)
                button.set_relief(Gtk.ReliefStyle.NORMAL)
                button.set_label("")
                button.set_image(Gtk.Image.new_from_file("icons/empty.png"))

    def game_win(self):
        print "Winnage"
        self.smiley.set_image(Gtk.Image.new_from_file("icons/win.png"))
        self.game_active = False

    def on_timeout(self):
        if not self.game_active:
            return True
        game_time = datetime.datetime.now() - self.game_start
        self.timer.set_label("Time: " + repr(game_time.seconds))
        return True

    def update_flag_counter(self):
        self.flag_counter.set_label("Flags: " + repr(self.model.num_bombs - self.model.placed_flags))

    def null_action(self, widget, event):
        return

    def style_set_action(self, widget, event):
        return

    def style_update_action(self, widget, event):
        return

    def on_click(self, widget, event, row, col):
        if event.button == 1:
            self.last_left_click = datetime.datetime.now()
        elif event.button == 3:
            self.last_right_click = datetime.datetime.now()

    def on_unclick(self, widget, event, row, col):
        if not self.game_active:
            return
        difference = datetime.datetime.now() - self.last_unclick
        self.last_unclick = datetime.datetime.now()
        if difference.seconds * (10**6) + difference.microseconds < 250000:
            return  # there are 2 unclick events per simul-click event, only "act" on the first
        difference = max(self.last_left_click, self.last_right_click)
        difference = difference - min(self.last_left_click, self.last_right_click)
        if event.button == 1:
            if difference.seconds * (10**6) + difference.microseconds < 250000:
                self.simul_click_action(row, col)
            else:
                self.left_click_action(row, col)
        elif event.button == 2:
            print "middle click action"
        elif event.button == 3:
            if difference.seconds * (10**6) + difference.microseconds < 250000:
                self.simul_click_action(row, col)
            else:
                self.right_click_action(row, col)

    def left_click_action(self, row, col):
        """explore a position"""
        if(row < 0 or
           row >= self.model.rows or
           col < 0 or
           col >= self.model.cols or
           self.model.data[row][col].explored or
           self.model.data[row][col].flag):
            return
        elif self.model.data[row][col].bomb:
            print "boom"
            self.game_active = False
            bomb = Gtk.Image.new_from_file("icons/dead_bomb.png")
            self.grid.get_child_at(col - 1, row - 1).set_image(bomb)
            self.smiley.set_image(Gtk.Image.new_from_file("icons/dead.png"))
            self.smiley.set_label("")
            # need to make the game lose here...
        else:
            self.model.data[row][col].explored = True
            self.model.explored_squares = self.model.explored_squares + 1
            image = Gtk.Image()
            label = ""
            if 0 == self.model.data[row][col].neighboring_bombs:
                image = Gtk.Image.new_from_file("icons/empty.png")
            else:
                label = repr(self.model.data[row][col].neighboring_bombs)
            button = self.grid.get_child_at(col - 1, row - 1)
            button.set_image(image)
            button.set_label(label)
            button.set_relief(Gtk.ReliefStyle.NONE)
            if self.model.check_victory_condition():
                self.game_win()
            if 0 == self.model.data[row][col].neighboring_bombs:
                self.simul_click_action(row, col)

    def draw_button(self, row, col):
        label = ""
        button_img = Gtk.Image()
        button = self.grid.get_child_at(col - 1, row - 1)
        if self.model.data[row][col].flag:
            button.set_label("")
            button.set_image(Gtk.Image.new_from_file("icons/flag.png"))
        elif not self.model.data[row][col].explored:
            button.set_label("")
            button.set_image(Gtk.Image())
        elif self.model.data[row][col].bomb:
            button.set_label("")
            button.set_image(Gtk.Image.new_from_file("icons/bomb.png"))
    # this is roughly to flag or unflag a position

    def right_click_action(self, row, col):
        if self.model.data[row][col].explored:
            return  # can't flag explored tiles
        if self.model.data[row][col].flag:  # is flagged, unflag
            self.model.data[row][col].flag = False
            self.model.placed_flags = self.model.placed_flags - 1
        elif (self.model.num_bombs - self.model.placed_flags) > 0:
            self.model.data[row][col].flag = True
            self.model.placed_flags = self.model.placed_flags + 1
        if self.model.data[row][col].flag:
            self.grid.get_child_at(col - 1, row - 1).set_label("")
            flag = Gtk.Image.new_from_file("icons/flag.png")
            self.grid.get_child_at(col - 1, row - 1).set_image(flag)
            if self.model.check_victory_condition():
                self.game_win()
        else:
            empty = Gtk.Image()
            label = ""
            if(self.model.data[row][col].explored and self.model.data[row][col].neighboring_bombs > 0):
                label = repr(self.model.data[row][col].neighboring_bombs)
            self.grid.get_child_at(col - 1, row - 1).set_label(label)
            self.grid.get_child_at(col - 1, row - 1).set_image(empty)
        self.update_flag_counter()


    def simul_click_action(self, irow, icol):
        """this is the same as left clicking on all surrounding non-flagged squares"""
        neighboring_flags = 0
        for row in range(max(0, irow - 1), min(irow + 1 + 1, self.model.rows), 1):
            for col in range(max(0, icol - 1), min(icol + 1 + 1, self.model.cols), 1):
                if self.model.data[row][col].flag:
                    neighboring_flags = neighboring_flags + 1
        if neighboring_flags < self.model.data[irow][icol].neighboring_bombs:
            return
        for row in range(max(0, irow - 1), min(irow + 1 + 1, self.model.rows), 1):
            for col in range(max(0, icol - 1), min(icol + 1 + 1, self.model.cols), 1):
                if not self.model.data[row][col].explored:
                    self.left_click_action(row, col)


def main():
    css_provider = Gtk.CssProvider()
    css_provider.load_from_path('gtk-widgets3.css')
    screen = Gdk.Screen.get_default()
    context = Gtk.StyleContext()
    context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
    my_model = Minesweeper_model(10, 10, 11)
    win = MinesweeperWindow(my_model)
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
    Gtk.main_quit()


if "__main__" == __name__:
    main()
