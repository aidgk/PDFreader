import hashlib
import fitz  # PyMuPDF 1.19.4
print(fitz.__doc__)
if not list(map(int, fitz.VersionBind.split("."))) >= [1, 19, 4]:
    raise SystemExit("need PyMuPDF v1.19.4 for this script")
import tkinter as tk  # needed to convert the image to a tk image
import pprint

class PDF:

    def __init__(self):
        self.wlist_tab = []
        self.doc = None  # this will reference the fitz document
        self.filename = ""
        self.file_guid = ""
        self.textpage = None
        self.wordlist = None
        self.blocklist = None
        self.textlist_custom = None
        self.page_count = 0
        self.starting_frame_width = 1200    # nominal
        self.org_page_width = None
        self.org_page_height = None
        self._page_number = 0  # zero referenced
        self.img_scale_factor = 1
        self._scaled_PhotoImage = None

    def get_current_page_scaled_image_PhotoImage(self):
        return self._scaled_PhotoImage

    def set_page_number(self, pno):
        self._page_number = pno
        self._process_text_current_page()
        return

    def get_page_number(self):
        return self._page_number

    def render_current_page(self, zoom):
        self.org_page_width = self.doc[self._page_number].rect[2] - \
                              self.doc[self._page_number].rect[0]
        self.org_page_height = self.doc[self._page_number].rect[3] - \
                               self.doc[self._page_number].rect[1]
        # calculate the new img_scale_factor based on requested zoom level
        # and orginal doc width - Zoom is a percent.
        # = (frame_width / org_page_width) * (zoom_level / 100)
        self.img_scale_factor = (self.starting_frame_width / self.org_page_width) * (zoom / 100)
        mat = fitz.Matrix(self.img_scale_factor, self.img_scale_factor)
        pix = self.doc[self._page_number].get_pixmap(dpi=None, matrix=mat, alpha=False)
        self._scaled_PhotoImage = tk.PhotoImage(data=pix.tobytes("ppm"))  # make sure we store a global ref or it will vanish

        print("Original PDF width height:", self.org_page_width, self.org_page_height)
        print("Scale Factor: %.3f" % self.img_scale_factor)
        print("New PDF width height:", int(self.org_page_width * self.img_scale_factor),
              int(self.org_page_height * self.img_scale_factor))
        return

    def _process_text_current_page(self):
        self.textpage = self.doc[self._page_number].get_textpage()
        self.wordlist = self.textpage.extractWORDS()
        self.blocklist = self.textpage.extractBLOCKS()

        # this will locate all of the characters on the page individually.
        # creates a dictionary with the character, bbox, and origin.
        rawdict = self.textpage.extractRAWDICT()
        self.textlist_custom = list()
        for block in rawdict["blocks"]:
            for line in block["lines"]:
                for span in line["spans"]:
                    for char in span["chars"]:
                        # print(char)
                        self.textlist_custom.append(char)

        dump_flag = 0
        if dump_flag:
            dump_flag = 1
            for item in self.textlist_custom:
                print(item)

        dump_flag = 0
        if dump_flag:
            for block in self.blocklist:
                print(block[4].rstrip("\n"))



    def _get_checksum(self):
        # md5 is good enough as UUID
        with open(self.filename, "rb") as f:
            file_hash = hashlib.md5()
            while chunk := f.read(8192):
                file_hash.update(chunk)
        self.file_guid = file_hash.digest()


    def open_png(self, fname):
        png_doc = fitz.open(fname)
        mat = fitz.Matrix(1.5, 2.0)
        pix = png_doc[0].get_pixmap(dpi=None, matrix=mat)
        image = tk.PhotoImage(data=pix.tobytes("ppm"))
        return image



    def open_pdf(self, fname):
        self.filename = fname
        self.doc = fitz.open(fname)  # create a PDF object with PyMuPDF
        self.page_count = self.doc.page_count
        print("Document contains pages:%s" % self.page_count)
        self._get_checksum()  # get an md5 hash of file contents
