# An extended Python/tkinter Canvas Window with zoom scale and extended bindings
# on which we can draw points, lines, rectangles, etc.
# See the Python tkinter module, Canvas class, for more usage details

import tkinter as tk
from PIL import Image, ImageTk

print("PIL Version:", Image.__version__)


class RectMarqueeTool:

    def __init__(self, canvas, **opts):
        self.canvas = canvas
        self.canvas.bind("<B1-Motion>", self.__update, '+')  # Ctrl or Shift modifier is used.
        self.canvas.bind("<ButtonRelease-1>", self.__stop, '+')
        self.item = None
        self.start = None
        self._callback = opts.pop('command', lambda *args: None)
        self.rectopts = opts    # options to the create_rectangle function
        self.starting_xy = None
        self.started = False
        self.canvas_sr = None  # this needs to be updated when the canvas is adjusted.

    def __update(self, event):
        #print(event.state)
        if event.state == 268 or event.state == 265:  # test for CTRL or SHIFT"
            # convert mouse to canvas dimensions.
            c_x = event.x + self.canvas_sr[0]
            c_y = event.y + self.canvas_sr[1]
            if not self.started:
                self.started = True
                self.starting_xy = [c_x, c_y]
                return

            # if there is a box drawn, delete it and draw a new one with updated dims.
            if self.item is not None:
                self.canvas.delete(self.item)
            self.item = self.canvas.create_rectangle(self.starting_xy[0],
                                                     self.starting_xy[1],
                                                     c_x,
                                                     c_y,
                                                     **self.rectopts)

    def __stop(self, event):
        # print("final")
        # print(event.state)
        # convert mouse to canvas dimensions.
        if self.started:
            self.started = False
            self.canvas.delete(self.item)
            self.item = None
            c_x = event.x + self.canvas_sr[0]
            c_y = event.y + self.canvas_sr[1]
            # these coordinates are in canvas!
            self._callback(self.starting_xy, (c_x, c_y), event.state)


class ScrollableCanvas(tk.Frame):
    """A scrollable container that can contains a canvas"""
    """ 
    A Note on COORDINATES!
    The mouse pointer places (0,0) in the top left corner of the visible canvas.
    The scrollregion places (0,0) in the center of the region
    Example:  
        when: srollbars are at 100% (not scrolling)  
        when: scrollregion = x0=(-750), y0=(-485), x1=(750), y1=(486) # note that y is inverted from normal
        if mouse top left and reports=(0,0), the canvas units are (-750,-486) for the same point
        if mouse top right and reports=(1500,0), the canvas units are (750,- 486) for the same point
        if mouse bot left and reports=(0,971), the canvas units are (-750,486) for the same point
        if mouse bot right and reports=(1500,971), the canvas units are (750,486) for the same point
        to convert
            canvas_x = mouse_x + scrollregion_x0
            canvas_y = mouse_y + scrollregion_y0       
   
    NOT WHAT HAPPENS YET WHEN THE SCROLLBARS ENGAGE       
    """
    canv = None
    vScroll = None

    def __init__(self, master, **opts):
        m_callback = opts.pop('marquee_callback', lambda *args: None)
        tk.Frame.__init__(self, master, **opts)  # holds canvas & scrollbars
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.canv = tk.Canvas(self, width=300, height=400,
                              bd=0, highlightthickness=2,
                              )

        self.hScroll = tk.Scrollbar(self, orient='horizontal',
                                    command=self.canv.xview)
        self.hScroll.grid(row=1, column=0, sticky='we')
        self.vScroll = tk.Scrollbar(self, orient='vertical',
                                    command=self.canv.yview)
        self.vScroll.grid(row=0, column=1, sticky='ns')
        self.canv.grid(row=0, column=0, sticky='nsew')
        self.canv.configure(xscrollcommand=self.hScroll.set,
                            yscrollcommand=self.vScroll.set)
        self.sr = [0, 0, 0, 0]  # init a list to hold the scrollregion attribute of canv
        # Create the marquee selection tool, and bind to callback.
        self.rmt = RectMarqueeTool(self.canv, fill="", width=1, command=m_callback)
        self.rmt.canvas_sr = self.sr  # pass the Marquee tool a reference to the scrollregion

        self.image_item_id = None  # persist the id of the image when added.
        self._crosshair_h = None
        self._crosshair_v = None
        self._crosshair_bind = None

        self.im_id = list()
        self.rects = list()
        self.on_drag_callback = None  # this is the function to call after a drag
        self._bindings()  # these should NOW BE done in main.py

    def create_trans_rectangle(self, bbox, **options):
        alpha = int(options.pop('alpha') * 255)
        # Use the fill variable to fill the shape with transparent color
        fill = options.pop('fill')
        fill = self.canv.winfo_rgb(fill) + (alpha,)  # add alpha to the tuple
        print("tansparent rectangle size")
        print("width", bbox[2] - bbox[0])
        print("height", bbox[3] - bbox[1])

        self.rects.append(ImageTk.PhotoImage(Image.new('RGBA', (bbox[2] - bbox[0], bbox[3] - bbox[1]), fill)))
        self.im_id.append(self.canv.create_image(bbox[0], bbox[1], image=self.rects[-1], anchor="nw"))
        return

    def show_new_image(self, new_image):
        # show new pdf image and set the scroll area of canvas
        if self.image_item_id is not None:  # delete the old image
            self.canv.delete(self.image_item_id)
        self.image_item_id = self.canv.create_image(0, 0, image=new_image, anchor=tk.CENTER)
        # print("bbox")
        # print(self.canv.bbox('all'))
        # set the scroll region to include everything in the canvas
        # hopefully that should only be a pdf image at this point.
        self.canv.configure(scrollregion=self.canv.bbox(self.image_item_id))
        # reminder, scrollregion[x-left,y-top,x-right,y-bottom]
        # the scrollregion is stored in the canvas widget as text but we need
        # it alot, so convert to ints now
        sregion_text_list = self.canv["scrollregion"].split()
        for index, item in enumerate(sregion_text_list):
            self.sr[index] = int(item)
        # self.canv.yview('moveto','1.0')

        # For now set all of the canvas as visible.
        self.canv.configure(height=(self.sr[3] - self.sr[1]))
        self.canv.configure(width=(self.sr[2] - self.sr[0]))

        # print("canv width", self.canv["width"])

    def set_crosshair(self, flag):
        if flag:
            # the "+" adds a callback!
            self._crosshair_bind = self.canv.bind('<Motion>', self._move_crosshair, '+')
            self._crosshair_bind = self.canv.bind("<B1-Motion>", self._move_crosshair, '+')
        else:
            self.canv.unbind(self._crosshair_bind)
            self._crosshair_bind = None

    def _move_crosshair(self, event):
        # print(event.state)
        self.canv.delete('crosshair')
        # convert to scrollregion dimensions.
        c_x = event.x + self.sr[0]
        c_y = event.y + self.sr[1]
        # print(event.x, c_x, event.y, c_y)
        dashes = [3, 2]
        self._crosshair_h = self.canv.create_line(self.sr[0], c_y, self.sr[2], c_y, dash=dashes, tags='crosshair')
        self._crosshair_v = self.canv.create_line(c_x, self.sr[1], c_x, self.sr[3], dash=dashes, tags='crosshair')

    def _bindings(self):
        # self.canv.bind("<Home>", self.test)
        # self.canv.bind('<Configure>', self.on_configure)

        # self.canv.bind("<Alt-MouseWheel>", self.onAltMouseWheel)
        # self.canv.bind("<Shift-MouseWheel>", self.onShiftMouseWheel)
        # self.canv.bind("f", self.fit_canvas)
        # self.canv.bind("<Home>", self.fit_canvas)

        # self.canv.bind("<Up>", self.onArrowUp)
        self.canv.bind("<Down>", self.on_drag_callback)
        # self.canv.bind("<Left>", self.onArrowLeft)
        # self.canv.bind("<Right>", self.onArrowRight)
        # self.canv.bind("<Prior>", self.onArrowUp)
        # self.canv.bind("<Next>", self.onArrowDown)
        # self.canv.bind("<Shift-Prior>", self.onPrior)
        # self.canv.bind("<Shift-Next>", self.onNext)
        # self.canv.bind("<ButtonRelease-1>", self.onButton1Release)
        # self.canv.bind("<B1-Motion>", self.onB1Motion)
        # self.canv.bind("all", self.eventEcho)

    #    def on_configure(self, event):
    #        w,h = event.width, event.height
    #        natural = self.frm.winfo_reqwidth()
    #        self.canv.itemconfigure('inner', width= w if w>natural else natural)
    #        self.canv.configure(scrollregion=self.canv.bbox('all'))

    # ------------ Key bindings -------------

    def onB1Motion(self, event):
        print("b1 motion")

    def onButton1Release(self, event):
        print("btn1 RELEASE")

    def onCtrlMouseWheel(self, event):
        return
        # event.delta = + 120 for wheel up and -120 for wheel down
        if event.delta > 0:
            self._zoom_in_on_m(event.x, event.y)
        else:
            self._zoom_out_on_m(event.x, event.y)
        return

    def onAltMouseWheel(self, event):
        print("altMouseWheel")
        return
        s = self.scalewidget.get()
        if event.delta > 0:
            s += 5
        else:
            s -= 5
        self.scalewidget.set(s)

    def onMouseWheel(self, event):

        self.on_drag_callback(event)
        # event.delta = + 120 for wheel up and -120 for wheel down
        # amount = -1 * (event.delta / 120)
        # self.canv.yview(tk.SCROLL, int(amount), "units")

    def onArrowUp(self, event):
        print("ArrowUp")
        return

        if event.keysym == "Up":
            self.yview_scroll(-1, "units")
        else:
            self.yview_scroll(-1, "pages")

    def onArrowDown(self, event):
        print("ArrowDown")
        return

        if event.keysym == "Down":
            self.yview_scroll(1, "units")
        else:
            self.yview_scroll(1, "pages")

    def onArrowLeft(self, event):
        print("ArrowLeft")
        return

        self.xview_scroll(-1, "units")

    def onArrowRight(self, event):
        print("ArrowRight")
        return
        # print(event.keysym)
        self.xview_scroll(1, "units")

    def onPrior(self, event):
        self.xview_scroll(1, "pages")

    def onNext(self, event):
        # print(event.keysym)
        self.xview_scroll(-1, "pages")

    def onShiftMouseWheel(self, event):
        print("shitMouseWheel")
        return
        self.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def fit_canvas(self, event):
        print(event.keysym)
        self.scalewidget.set(100)


