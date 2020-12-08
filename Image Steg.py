import shutil
import sys
import struct
from zlib import crc32
import os

# PNG file format signature
pngsig = b'\x89PNG\r\n\x1a\n'

def swap_palette(filename, PLTELen, n):
    # open in read+write mode
    with open(filename, 'r+b') as f:
        f.seek(0)
        if f.read(len(pngsig)) != pngsig:
            raise RuntimeError('not a png file!')
        while True:
            chunkstr = f.read(8)
            if len(chunkstr) != 8:
                break
            # decode the chunk header
            length, chtype = struct.unpack('>L4s', chunkstr)
            # we only care about palette chunks
            if chtype == b'PLTE':
                curpos = f.tell()
                paldata = (b'\x00\x00\x00' * n) + b'\xff\xff\xff' + (b'\x00\x00\x00' * (PLTELen - n - 1))

                # go back and write the modified palette in-place
                f.seek(curpos)
                f.write(paldata)
                f.write(struct.pack('>L', crc32(chtype+paldata)&0xffffffff))
            else:
                # skip over non-palette chunks
                f.seek(length+4, os.SEEK_CUR)
                
def swap_palette2(filename, PLTELen, n, increDecre):
    # open in read+write mode
    with open(filename, 'r+b') as f:
        f.seek(0)
        if f.read(len(pngsig)) != pngsig:
            raise RuntimeError('not a png file!')
        while True:
            colArr = [increDecre] * PLTELen
            for i in range(n):
                colArr[i] = int(not increDecre) #Flips 0 to 1, and vice versa
            chunkstr = f.read(8)
            if len(chunkstr) != 8:
                break
            # decode the chunk header
            length, chtype = struct.unpack('>L4s', chunkstr)
            # we only care about palette chunks
            if chtype == b'PLTE':
                curpos = f.tell()
                paldata = b''
                for i in range(len(colArr)):
                    if colArr[i] == 1 or i == n:
                        paldata = paldata+b'\xff\xff\xff'
                    else:
                        paldata = paldata+b'\x00\x00\x00'

                # go back and write the modified palette in-place
                f.seek(curpos)
                f.write(paldata)
                f.write(struct.pack('>L', crc32(chtype+paldata)&0xffffffff))
            else:
                # skip over non-palette chunks
                f.seek(length+4, os.SEEK_CUR)

if __name__ == "__main__":
    filename = input("Input .png file name (with .png): ")

    #This portion aims to get the number of colors the image has; 
    #The lesser color the image has, the less image it would be required to generate.
    with open(filename, 'r+b') as f:
        f.seek(0)
        # verify that we have a PNG file
        if f.read(len(pngsig)) != pngsig:
            raise RuntimeError('not a png file!')
        while True:
            chunkstr = f.read(8)
            if len(chunkstr) != 8:
                break
            length, chtype = struct.unpack('>L4s', chunkstr)
            if chtype == b'PLTE':
                if length%3!=0:
                    raise RuntimeError('Invalid png file!')
                PLTELen = int(length/3)
                break
            else:
                f.seek(length+4, os.SEEK_CUR)
        f.close()

    #Creates Result Folder
    if not os.path.exists('res'):
        os.makedirs('res')
    confirmation = ""
    while(confirmation != "Y" and confirmation != "N" and confirmation != "y" and confirmation != "n" ):
        confirmation = input("Image has {0} Palette Entries, {0} Images will be generated. Confirm? (Y/N):".format(PLTELen))
    if(confirmation=='N' or confirmation=='n'):
        print("Program terminating...")
        exit()
    #User Input Interface
    choice=0
    while(choice<1 or choice >3):
        print("""Please select option:\n
        1) Expose one Palette Entry at a time.\n
        2) Gradually Expose All Palette Entries.\n
        3) Gradually Remove Palette Entries.\n
        4) Exit.""")
        choice = int(input())
    if choice == 1:
        for i in range(PLTELen):    
            shutil.copyfile(filename, "res/single-color"+str(i)+".png")
            swap_palette("res/single-color"+str(i)+".png", PLTELen, i)
        print("Done, program terminating...")
    elif choice == 2: 
        for i in range(PLTELen):    
            shutil.copyfile(filename, "res/single-color"+str(i)+".png")
            swap_palette2("res/single-color"+str(i)+".png", PLTELen, i, 0) #Last Argument = all palette entries starts with 0x000000
        print("Done, program terminating...")
    elif choice == 3: 
        for i in range(PLTELen):    
            shutil.copyfile(filename, "res/single-color"+str(i)+".png")
            swap_palette2("res/single-color"+str(i)+".png", PLTELen, i, 1) #Last Argument = all palette entries starts with 0xFFFFFFF
        print("Done, program terminating...")
    else:
        print("Program terminating...")
    exit()
                                