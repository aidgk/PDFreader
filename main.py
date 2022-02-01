import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename

print("Loading Modules.....")
print("Tkinter Version:", tk.TkVersion)
from g_canvas import ScrollableCanvas as sc  # this is a frame
from g_pdf import PDF

zoom_levels = ["25", "50", "75", "100", "125", "150", "200"]
# im_reference = None

STARTING_FRAME_WIDTH = 1200  # this is how wide we want to start the app
ALLOW_ZOOM = False
file_opened = False


def get_tkinter_widget_attributes(widget):
    widg = widget
    keys = widg.keys()
    for key in keys:
        print("Attribute: {:<20}".format(key), end=' ')
        value = widg[key]
        vtype = type(value)
        print('Type: {:<30} Value: {}'.format(str(vtype), value))


def select_chars_by_bbox(pdf_x0, pdf_y0, pdf_x1, pdf_y1, ):
    found_one = False
    bbox = [10000000, 10000000, -10000000, -1000000]  # pdf units
    new_line = str()
    for char in pdf.textlist_custom:
        if pdf_x0 < char["origin"][0] < pdf_x1 and pdf_y0 < char["origin"][1] < pdf_y1:
            found_one = True
            new_line += char["c"]
            # print(char["origin"])
            # print(char["c"])
            # create a bounding box around all of the chars
            # print(char)
            if char["bbox"][0] < bbox[0]:
                bbox[0] = char["bbox"][0]
            if char["bbox"][1] < bbox[1]:
                bbox[1] = char["bbox"][1]
            if char["bbox"][2] > bbox[2]:
                bbox[2] = char["bbox"][2]
            if char["bbox"][3] > bbox[3]:
                bbox[3] = char["bbox"][3]
    if found_one:
        # print("pdf coords", bbox)
        bbox = pdf_block_to_canvas_units_conversion(bbox)
        # print("canvas coords", bbox)
        fr_container.create_trans_rectangle(bbox, fill='blue', alpha=0.3)
        listbox.insert("end", new_line)
        listbox.yview("end")


def select_block_by_point(pdf_x, pdf_y):
    for block in pdf.blocklist:
        if block[0] < pdf_x < block[2] and block[1] < pdf_y < block[3]:
            new_line = block[4].replace("\n", " ")
            listbox.insert("end", new_line)
            listbox.yview("end")
            print("pdf coords", block)
            # convert pdf units to canvas units
            bbox = pdf_block_to_canvas_units_conversion(block)
            print("canvas coords", bbox)
            fr_container.create_trans_rectangle(bbox, fill='yellow', alpha=0.3)


def onButton1(event):
    # event contains mouse coordinates.
    # print(event.state)
    global file_opened
    if file_opened:
        if event.state == 8:  # No modifer
            pdf_x, pdf_y = scale_mouse_to_pdf(event.x, event.y)
            # add to listbox and highlight text
            select_block_by_point(pdf_x, pdf_y)


def find_words_similar_to(match_string):
    for word in pdf.wordlist:
        # if word[4].startswith(match_string):
        #    print(word[4])
        if match_string in word[4]:
            print(word[4])


def scale_canvas_to_pdf(canvas_x, canvas_y):
    pdf_x = round((canvas_x - fr_container.sr[0]) / pdf.img_scale_factor)
    pdf_y = round((canvas_y - fr_container.sr[1]) / pdf.img_scale_factor)
    return pdf_x, pdf_y


def pdf_block_to_canvas_units_conversion(block):
    c_list = [round(int(block[0]) * pdf.img_scale_factor + fr_container.sr[0]),
              round(int(block[1]) * pdf.img_scale_factor + fr_container.sr[1]),
              round(int(block[2]) * pdf.img_scale_factor + fr_container.sr[0]),
              round(int(block[3]) * pdf.img_scale_factor + fr_container.sr[1])]
    return c_list


def scale_mouse_to_pdf(mouse_x, mouse_y):
    # rescale to get actual pdf point location.
    # TODO: this will get more complicated when window has scrolls.
    # TODO: but  I think I have all of the information I need here.
    pdf_x = int(mouse_x / pdf.img_scale_factor)
    pdf_y = int(mouse_y / pdf.img_scale_factor)

    show = False
    if show:
        print("")
        print("PDF original size:", pdf.org_page_width, pdf.org_page_height)
        print("Current Img_Scale_Factor %.3f" % pdf.img_scale_factor)
        print("Mouse Pointer:", mouse_x, mouse_y)
        print("PDF Coords:", pdf_x, pdf_y)
        print("Canvas width and height(1):", fr_container.canv["width"], fr_container.canv["height"])
        print("Scrollregion", fr_container.canv["scrollregion"])
        print("hScroll data:", fr_container.hScroll.get(), "vScroll data:", fr_container.vScroll.get())

    return pdf_x, pdf_y


def next_page():
    new_pno = int(txt_pno["text"]) + 1
    if new_pno > pdf.page_count:
        new_pno = 1
    txt_pno["text"] = new_pno

    pdf.set_page_number(int(txt_pno["text"]) - 1)  # set the page number!
    pdf.render_current_page(int(txt_zoom_level["text"]))  # creates a scaled image
    fr_container.show_new_image(pdf.get_current_page_scaled_image_PhotoImage())


def prev_page():
    new_pno = int(txt_pno["text"]) - 1
    if new_pno < 1:
        new_pno = pdf.page_count
    txt_pno["text"] = new_pno

    pdf.set_page_number(int(txt_pno["text"]) - 1)  # set the page number!
    pdf.render_current_page(int(txt_zoom_level["text"]))  # creates a scaled image
    fr_container.show_new_image(pdf.get_current_page_scaled_image_PhotoImage())


def open_file():
    # since its a new file we should "maybe" reset some settings?
    filepath = askopenfilename(
        filetypes=[("PDF Files", "*.pdf")]
    )
    if not filepath:
        print("User did not select a file?")
        return
    """
    0. open the pdf document file with fitz (PyMuPDF)
    1. Process a page to get its text content 
    2. render the page to an image at a certain zoom (returns an image)
    3. calculate the required canvas size, and windows size
    4. clea/show image on the canvas 
    5. reset the main window size. RETHINK THIS APPROACH 
    6. set cursor (crosshair etc)
    """

    pdf.open_pdf(filepath)
    txt_pno["text"] = "1"  # always open from page 1 I suppose.
    # set the page number! this will also cause the page to be read for text.
    pdf.set_page_number(int(txt_pno["text"]) - 1)
    pdf.render_current_page(int(txt_zoom_level["text"]))  # creates a scaled image
    fr_container.show_new_image(pdf.get_current_page_scaled_image_PhotoImage())
    # TODO allow window to be resized.
    # lock the window size for now.
    window.update_idletasks()  # make sure window has a chance to update its size
    window.minsize(width=window.winfo_width(), height=window.winfo_height())
    window.maxsize(width=window.winfo_width(), height=window.winfo_height())

    btn_next["state"] = tk.NORMAL
    btn_prev["state"] = tk.NORMAL
    search_box["state"] = tk.NORMAL
    if ALLOW_ZOOM:  # for POC we may not allow zooming
        btn_zoom_in["state"] = tk.NORMAL
        btn_zoom_out["state"] = tk.NORMAL

    # set cursor
    fr_container.set_crosshair(True)
    global file_opened
    file_opened = True


def zoom_in():
    max_zoom_index = len(zoom_levels) - 1
    new_zoom_index = zoom_levels.index(txt_zoom_level["text"]) + 1
    if new_zoom_index > max_zoom_index:
        new_zoom_index = max_zoom_index
    txt_zoom_level["text"] = zoom_levels[new_zoom_index]
    render_page(0, 0)


def zoom_out():
    min_zoom_index = 0
    new_zoom_index = zoom_levels.index(txt_zoom_level["text"]) - 1
    if new_zoom_index < min_zoom_index:
        new_zoom_index = min_zoom_index
    txt_zoom_level["text"] = zoom_levels[new_zoom_index]
    render_page(0, 0)


def clear_listbox():
    listbox.delete(0, "end")


def clear_selection():
    itemslist = listbox.curselection()
    for index in itemslist[::-1]:
        listbox.delete(index)


def test():
    print("")
    # print("PDF original size:", pdf.org_page_width, pdf.org_page_height)
    # print("Current Img_Scale_Factor", pdf.img_scale_factor)
    # print("Mouse Pointer:", mouse_x, mouse_y)
    print("Canvas width and height(1):", fr_container.canv["width"], fr_container.canv["height"])
    print("Scrollregion", fr_container.canv["scrollregion"])
    print("hScroll data:", fr_container.hScroll.get())
    print("vScroll data:", fr_container.vScroll.get())
    # print("PDF Coords:", pdf_x, pdf_y)

    get_tkinter_widget_attributes(tk.Canvas())


def callback_search_var(*args):
    # find_words_similar_to(search_var.get())
    # print(search_var.get())
    return


def callback_search_enter(event):
    for word in pdf.blocklist:
        # if word[4].startswith(match_string):
        #    print(word[4])
        if search_var.get() in word[4]:
            print(word)
            bbox = pdf_block_to_canvas_units_conversion(word)
            fr_container.create_trans_rectangle(bbox, fill='red', alpha=0.3)

    for word in pdf.wordlist:
        # if word[4].startswith(match_string):
        #    print(word[4])
        if search_var.get() in word[4]:
            print(word)
            bbox = pdf_block_to_canvas_units_conversion(word)
            fr_container.create_trans_rectangle(bbox, fill='blue', alpha=0.3)


def on_marquee_drag_end(start, end, state_code):
    # state_code is 268-CTRL, 265-Shift
    # start and end are in Canvas units!
    global file_opened
    if file_opened:
        if state_code == 268:  # select all text in the box
            # print("select text in box")
            # print(start, end)
            pdf_x0, pdf_y0 = scale_canvas_to_pdf(start[0], start[1])
            pdf_x1, pdf_y1 = scale_canvas_to_pdf(end[0], end[1])
            # print(pdf_x0, pdf_y0, pdf_x1, pdf_y1)
            # find all of the text that is in this box
            select_chars_by_bbox(pdf_x0, pdf_y0, pdf_x1, pdf_y1)
            # listbox.insert("end", new_line)
            # listbox.yview("end")

        elif state_code == 265:
            print("create a snapshot")


if __name__ == '__main__':
    window = tk.Tk()
    window.title("GENOA DESIGN INTERNATIONAL     PDF REVIEW")
    window.rowconfigure(0, minsize=300, weight=1)  # make the single row stretch
    window.columnconfigure(1, minsize=300, weight=1)  # make the third column stretch

    fr_buttons = tk.Frame(window, relief=tk.RAISED, bd=2)
    fr_buttons.grid(row=0, column=0, sticky="ns")

    fr_text = tk.Frame(window, relief=tk.RAISED, bd=2)
    fr_text.grid(row=0, column=2, sticky="nsew")

    fr_container = sc(window, borderwidth=2,
                      marquee_callback=on_marquee_drag_end)  # make an instance of ScrollableContainer
    fr_container.canv.bind("<Button-1>", onButton1)
    fr_container.grid(row=0, column=1, sticky="nsew")

    btn_open = tk.Button(fr_buttons, text="Open", command=open_file)
    btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
    btn_next = tk.Button(fr_buttons, text="Next", command=next_page)
    btn_next.grid(row=1, column=0, sticky="ew", padx=5, pady=1)
    btn_next["state"] = tk.DISABLED
    btn_prev = tk.Button(fr_buttons, text="Prev", command=prev_page)
    btn_prev.grid(row=2, column=0, sticky="ew", padx=5, pady=1)
    btn_prev["state"] = tk.DISABLED
    txt_pno = tk.Label(fr_buttons, text="1", borderwidth=2, relief=tk.RIDGE)
    txt_pno.grid(row=3, column=0, sticky="ew", padx=5, pady=1)
    sep0 = ttk.Separator(fr_buttons, orient="horizontal")
    sep0.grid(row=4, column=0, sticky="ew", padx=5, pady=8)
    btn_zoom_in = tk.Button(fr_buttons, text="Zoom In", command=zoom_in)
    btn_zoom_in.grid(row=6, column=0, sticky="ew", padx=5, pady=1)
    btn_zoom_in["state"] = tk.DISABLED
    btn_zoom_out = tk.Button(fr_buttons, text="Zoom Out", command=zoom_out)
    btn_zoom_out.grid(row=7, column=0, sticky="ew", padx=5, pady=1)
    btn_zoom_out["state"] = tk.DISABLED
    txt_zoom_level = tk.Label(fr_buttons, text="100", borderwidth=2, relief=tk.RIDGE)
    txt_zoom_level.grid(row=8, column=0, sticky="ew", padx=5, pady=1)

    sep1 = ttk.Separator(fr_buttons, orient="horizontal")
    sep1.grid(row=10, column=0, sticky="ew", padx=5, pady=8)
    btn_test = tk.Button(fr_buttons, text="test", command=test)
    btn_test.grid(row=11, column=0, sticky="ew", padx=5, pady=1)
    btn_clear_all = tk.Button(fr_buttons, text="CLEAR ALL",
                              command=clear_listbox,
                              font=("Arial", 8))
    btn_clear_all.grid(row=12, column=0, sticky="ew", padx=5, pady=1)
    btn_clear_selection = tk.Button(fr_buttons, text="CLEAR SELECTED",
                                    font=("Arial", 7),
                                    command=clear_selection)
    btn_clear_selection.grid(row=13, column=0, sticky="ew", padx=5, pady=1)

    search_var = tk.StringVar()
    search_var.trace("w", callback_search_var)
    search_box = tk.Entry(fr_buttons, textvariable=search_var)
    search_box["state"] = tk.DISABLED
    search_box.grid(row=14, column=0, sticky="ew", padx=5, pady=1)
    search_box.bind("<Return>", callback_search_enter)

    # btn_check = tk.Button(fr_text, text="check", command=test)
    # btn_check.grid(row=0, column=0, sticky="ew", padx=5, pady=1)

    listbox = tk.Listbox(fr_text, selectmode=tk.EXTENDED, width=20, font=("Arial", 8))
    vScrollbar = tk.Scrollbar(fr_text, orient=tk.VERTICAL)
    vScrollbar.config(command=listbox.yview)
    hScrollbar = tk.Scrollbar(fr_text, orient=tk.HORIZONTAL)
    hScrollbar.config(command=listbox.xview)
    listbox.config(xscrollcommand=hScrollbar.set, yscrollcommand=vScrollbar.set)
    hScrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH)
    vScrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    pdf = PDF()  # create a pdf worker object.
    pdf.starting_frame_width = STARTING_FRAME_WIDTH
    img = pdf.open_png("logo.png")  # get the pdf class to return a pyImage of the logo
    fr_container.show_new_image(img)  # now render it in the canvas
    # window.resizable(False, False)

    window.mainloop()
