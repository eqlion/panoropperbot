#!/usr/bin/env python3

__author__ = 'Eqlion'

import sys

from PIL import Image
from os import path


PATH = path.join(path.dirname(__file__), '{}')

class Cropper(object):

    def __init__(self, img):
        self.img = img
        self.w, self.h = self.img.size

    def square_cut(self):
        # Calculating how many pixels to cut from each of the sides
        spare = (self.w % self.h) // 2
        # Croping the image so that we could cut it into even parts
        self.img = self.img.crop((spare, 0, (self.w // self.h)*self.h + spare, self.h))
        w, h = self.img.size

        parts = [self.img.crop((h*i, 0, h*(i+1)-1, h)) for i in range(w // h)]

        return parts

    def square_fill(self):
        # Creating `background` – an image with extra space on both sides
        background = Image.new('RGB', (self.w-(self.w%self.h)+self.h, self.h), 'white')
        # Calculating how many pixels to add to each of the sides
        spare = (background.size[0]-self.w) // 2

        background.paste(self.img, (spare, 0))
        w, h = background.size

        parts = [background.crop((h*i, 0, h*(i+1)-1, h)) for i in range(w // h)]

        return parts

    def auto(self):
        d = {
          'self.square_cut()': self.w % self.h,
          'self.square_fill()': self.h - (self.w % self.h),
        }
        prefered = sorted(d, key=lambda x: d[x])[0]
        return eval(prefered)
