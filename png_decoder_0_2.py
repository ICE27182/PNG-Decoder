# 最后一次编辑
# 3/13/2023
# 缺少对于调色板格式的解码能力
# 图片319.png有未知问题
# 自动缩放未完成
# to_hex()缺少进度条显示
# display应该不只能接受self 储存可以用json(虽然也许pickle更高效?)

class PNG:
    version = "v0.2"
    README = f"""
    version: {version}
        It's a PNG decoder based on Python. 
        Written without any third-party library, 
        there'll be no need to download any other libraries to use the decoder.

        Updates:
        0. Support multiple IDAT chunks Yeah!!!
        0. Support All Filters Yeah!!!
        1. Support automaticly rescaling the picture
        2. Improve the output file format
        3. Optional decoded idat chunk(s) buffer (Default On)
        4. A loading(maybe processing?) bar for decoding


        Bug Fixs:
        1. Delete the PNG.readme()
        2. Fix a bug in to_hex(origin - str+bytes)
        3. Fix a bug in to_hex(output part - decoder_directory + output_rela -> decoder_directory + "\\" + output_rela)
        

        --------v0.1--------
        Features:
            1. No third-party library;
            2. Able to decode some PNG files, not all as it's far from a final version;
            3. Able to trans a PNG file into Hex code and print it on the ternimal or write it in a file;
            4. Able to print a true color picture on the terminal.(For now, the max supported resolution 
                is 940x320 as it seems to be the most text that can be fully dispalied on windows terminal)
        
        FEATURES:
            一、No support for png files using multiple IDAT chunks(which s**ks)
            二、No support for png files using filtering except for the "None Filter"(which alse s**ks)
            三、No support for png files using palettes
            四、No support for png files whose bit depth is 1, 2, 4 or 16. Only 8 bits depth is supported
            五、No support for png files whose color type is 0, 3 or 4. Only 2 and 6 are supported
            六、No support for transparency(terminal)
            七、CRC completely means nothing to the decoder
            八、Displayed in terminal, large picture's can be wrong
            九、Bad performance and ugly codes maybe?

            """
    def __init__(self,filepath_rela=None,filepath_abs=None,check=True,readme=False,
                buffer_decoded_idat = True) -> None:
        """filepath_rela is based on the path of the decoder file,
        while filepath_abs is the absolute file path.
        The decoder will take either of them, 
        but one and no more than one must be given.
        (etc. to decode pic.png that is in the same directory as the decoder,
        it should be in 
        (PNG(filepath_rela="pic.png"), PNG(filepath_rela="pic"), 
        PNG("pic.png"), PNG("pic"), 
        PNG(filepath_abs="E:\\Desktop\\decoder\\pic"),
        PNG(filepath_abs="E:\\Desktop\\decoder\\pic.png")
        
        If check is True, the decoder will check if the file can be decoded and 
        well decoded by the decoder.(Default On)

        If readme is True, the decoder will print the README text when executing __init__ function(Default Off)
        """


        if readme == True:
            print(PNG.README)

        # Process the parameters to get the file location
        if filepath_rela != None and filepath_abs == None:      # Relative Path
            decoder_directory = "\\".join(__file__.split("\\")[:-1])
            file = f"{decoder_directory}\\{filepath_rela}"
        elif filepath_rela == None and filepath_abs != None:    # Absolute Path
            file = filepath_abs
        else:                                                   # Invalid parameters
            raise Exception(f"""
Parameter Error
\tThe decoder will take either of the filepath_rela or filepath_abs, 
\tbut one and no more than one must be given.
\tfilepath_rela: {repr(filepath_rela)},        filepath_abs: {repr(filepath_abs)}
            """)
        
        # In case the .png is not added
        # (also make it impossible to open files whose names indicate they are not png file)
        if file[-4:] != ".png":
            file += ".png"
        self.file = file

        # Obtain all the bytes
        with open(file,"rb") as img:
            self.bytes = img.read(-1)
        if check == True:
            # Check whether the file is a valid png file(At least in some ways)
            self.checks()
            # Check whether the file can be correctly decoded by the if the file itself is alright
            self.other_checks()

        # width height idat channels
        self.get_properties()

        self.buffer_decoded_idat = buffer_decoded_idat
        

    def checks(self):
        """Check whether the file is a valid png file(At least in some ways)"""
        if self.bytes[0:8] != b'\x89PNG\r\n\x1a\n':
            raise Exception(f"""
Signiture Error
\tAccording to its header, the file is not a png file.
\t\tA png file should begin with "89 50 4E 47 0D 0A 1A 0A"(or b'\x89PNG\r\n\x1a\n' in ASCII),
\t\twhile the file begins with {self.bytes[0:8]}
            """)
        if b'IHDR' not in self.bytes or b'IDAT' not in self.bytes or b'IEND' not in self.bytes:
            raise Exception(f"""
File Error
\tCritical chunk(s) is/are missed. The file may be broken.
\tIHDR:{b'IHDR' in self.bytes}    IDAT:{b'IDAT' in self.bytes}    IEND:{b'IEND' in self.bytes}
            """)
           
    def other_checks(self):
        """Check whether the file can be correctly decoded by the if the file itself is alright"""
#         if self.bytes.count(b'IDAT') != 1:
#             raise Exception(f"""
# Decoder Error        version: {PNG.version}
# \tThis version of decoder doesn't support png files with multiple IDAT chunks.
#             """)
        if b'PLTE' in self.bytes:
            raise Exception(f"""
Decoder Error        version: {PNG.version}
\tThis version of decoder doesn't support png files with PLTE chunk.      
            """)
        if self.bytes[24] != 8:     # Bit Depth
            raise Exception(f"""
Decoder Error
\tThis version of decoder only support png files whose bit depth is 8 bits(RGB:0-255).                 
            """)
        if self.bytes[25] not in (2,6):     # Color Type
            raise Exception(f"""
Decoder Error
\tThis version of decoder only support png files whose color type is 2 or 6.
\t\tcolor type 2: Ture color(R,G,B) 3-channels
\t\tcolor type 6: True color with alpha(R,G,B,alpha) 4-channels
            """)
        
        if self.bytes[28] != 0:     # Interlace Mode
            print(f"""\033[1;31;5m
███---Warning---███\033[0m\033[1;33m
\tThe file's interlace mode is Adam7 interlace, while the code is base on "no interlace" mode,
\tso it's likely to meet some problems here.
           \033[0m""")


    def get_properties(self):
        """Get self.width, self.height, self.channels, self.idat"""
        self.width = int.from_bytes(self.bytes[16:20])
        self.height = int.from_bytes(self.bytes[20:24])
        self.channels = 3 if self.bytes[25] == 2 else 4

        idat_list = []
        idats = self.bytes[self.bytes.find(b'IDAT')-4:self.bytes.find(b'IEND')-4]
        for _ in range(self.bytes.count(b'IDAT')):
            idat_list.append(idats[8:8+int.from_bytes(idats[0:4])])
            idats = idats[12+int.from_bytes(idats[0:4]):]
        self.idat = b''.join(idat_list)


    def decode(self,type,info=True,use_cache=True):
        """Decode the IDAT field to a list. e.g.[("\n",00),(R,G,B,a),(R,G,B,a),...,("\n",00),(R,G,B,a)...]
        The current version can only decode png files with None filtering correctly."""
        def int_to_hex(integer,):
            """Turn an integer in the range of [0,255] in to a string of Hex."""
            if integer >= 16:
                return hex(integer)[2:].upper()
            else:
                return "0"+hex(integer)[2:].upper()
        
        def trans_to_hex():
            for index,pixel in enumerate(pixels):
                if pixel[0] != "\n":
                    pixels[index] = tuple(map(int_to_hex,pixel))
            return pixels
    
        def add_to_pixels_and_channels_buffer():
            channels_buffer.append(byte)
            if len(channels_buffer) == self.channels:
                pixels.append(tuple(channels_buffer))
                channels_buffer.clear()
        
        def left():
            if (pixel:=pixels[y*(self.width+1)+(index-1)//self.channels])[0] != "\n":
                return pixel[(index-1)%self.channels]
            else:
                return 0
        
        def up():
            return pixels[(y-1)*(self.width+1)+(index-1)//self.channels+1][(index-1)%self.channels]
        
        def up_left():
            if (pixel:=pixels[y*(self.width+1)+(index-1)//self.channels])[0] != "\n":
                return pixels[(y-1)*(self.width+1)+(index-1)//self.channels][(index-1)%self.channels]
            else:
                return 0
            
        if type not in (10,"D","d","Decimal","decimal",16,"H","h","Hex","hex"):
            raise Exception(f"""
Parameter Error
\tThe output type for decoding support only hex or decimal, which can be
\ttyped as (10,"D","d","Decimal","decimal",16,"H","h","Hex","hex")
\tInvalid parameter: {repr(type)}
            """)
        
        if type in (10,"D","d","Decimal","decimal") and hasattr(self,"decoded_idat_10"):
            return self.decoded_idat_10
        elif hasattr(self,"decoded_idat_16"):
            return self.decoded_idat_16
        
        if info == True:
            import time
            print("Decoding...",end="")
            tm = time.time()

        # Decode the Huffman and LZSS part
        from zlib import decompress
        data = decompress(self.idat)

        # Decide the Filtering
        pixels = [] # Store the pixels to be returned
        channels_buffer = [] # Store a pixel
        row_bytes_len = self.width*self.channels+1

        for y in range(self.height):
            if info == True:
                print(f"""
{y/self.height:.3%}     {'█'*((20*y)//self.height)}\033[2;37m{'█'*((20*(self.height-y))//self.height)}\033[0m"""
                    ,end="\033[F")
            row = data[0:row_bytes_len]
            data = data[row_bytes_len:]
            filter = row[0]
            
            # None
            if filter == 0:
                pixels.append(("\n","0"+str(filter)))
                for byte in row[1:]:
                    add_to_pixels_and_channels_buffer()
            # Sub
            elif filter == 1:
                pixels.append(("\n","0"+str(filter)))
                for index,byte in enumerate(row[1:],1):
                    if index > self.channels:
                        byte = (byte + left()) % 256
                    add_to_pixels_and_channels_buffer()
            # Up
            elif filter == 2:
                # Maybe, just maybe, the index for pixels will be wrong just may be
                # I don't think it will ever happen, but just incase it happens,
                # it's here. Somehow, the first row of the picture uses Up filter.
                # if y < 0:
                #     raise Exception("""Please check. It's the Up filter in PNG.decode.""")
                
                pixels.append(("\n","0"+str(filter)))
                for index,byte in enumerate(row[1:],1):
                    byte = (byte + up()) % 256
                    add_to_pixels_and_channels_buffer()
            # Average
            elif filter == 3:
                pixels.append(("\n","0"+str(filter)))
                for index,byte in enumerate(row[1:],1):
                    avg = int((up() + left())/2)
                    byte = (byte + avg) % 256
                    add_to_pixels_and_channels_buffer()
                    pass
            # Paeth
            elif filter == 4:
                pixels.append(("\n","0"+str(filter)))
                for index,byte in enumerate(row[1:],1):
                    p = up() + left() - up_left()
                    v = min(up() - p, left() - p, up_left() - p)
                    byte = (byte + v) % 256
                    add_to_pixels_and_channels_buffer()           
            # Just keep it. It makes the picture works without one or two less used filters.
            # else:
            #     pixels.extend(["\n"]+[(0,0,0,0)]*self.width)

        if info == True:
            tm = time.time()-tm
            print(f"\nDecoding Done. Time using:{tm:.3f}s{' '*max(0,(15-len(str(int(tm)+3))))}\n")

        if type in (16,"H","h","Hex","hex"):
            pixels = trans_to_hex()

        pixels = tuple(pixels)

        if use_cache == True and type in (16,"H","h","Hex","hex"):
            self.decoded_idat_16 = pixels
        elif use_cache == True and type in (10,"D","d","Decimal","decimal"):
            self.decoded_idat_10 = pixels

        return pixels


    def display(self,render_mode=1,auto_resacle=True):
        """Render mode should be an integer.
                -1 means print a pixel after a pixel(Rather slow Nearly imposible to produce �)
                0 means print all pixels once (Kinda quick Not quite recommended 
                as � may be produced if its a big picture)
                Positive value means how many(Medium speed If the picture is long, � may still be produced)
        """
        def color(clr):
            """Turn the RGB value in to a true-color pixel"""
            return f"\033[38;2;{clr[0]};{clr[1]};{clr[2]}m██\033[0m"
        
        # Obtain the decimal list
        data = self.decode(10)

        # Rescale the picture
        if auto_resacle == True:
            data = PNG.rescale(self,data)

        # Print a pixel after a pixel
        if render_mode == -1:
            for pixel in data:
                if pixel[0]=="\n":
                    print("")
                else:
                    print(color(pixel),end='')
            print("")
        # Print all pixels once
        elif render_mode == 0:
            string = ""
            for pixel in data:
                if pixel[0]=="\n":
                    string += "\n"
                else:
                    string += color(pixel)
            print(string)
        # Print rows of pixels one after another
        elif type(render_mode) == int and render_mode > 0:
            string,i = "",0
            for pixel in data:
                if pixel[0]=="\n":
                    i += 1
                    string += "\n"
                    if i == render_mode:
                        print(string,end="")
                        string,i = "",0
                else:
                    string += color(pixel)
            print(string)
    

    def rescale(self,data):
        def rnd(val):
            return int(round(val,0))
        from math import floor
        # Decide how to rescale
        from shutil import get_terminal_size
        columns,rows = get_terminal_size()
        columns,rows = 626,137
        columns,rows = columns-1,rows-1 # Just in case things go wrong. Not necessary(maybe not useful too)
        rate = min(columns/self.width, rows/self.height)
        # ↓ Or just 1/step. I just think maybe it can reduce the bugs in math?
        step = max(self.width/columns, self.height/rows) 
        rescaled_width,rescaled_height = int(rate*self.width),int(rate*self.height)

        rescaled_data = []
        
        if rate < 1:    # The picture is too big to be well shown
            # Sadly, for loop doesn't support float step
            y = 0
            while round(y,11) < self.height: # Cause x.99999... happens in our dear Python
                x = 0
                rescaled_data.append(tuple("\n"))
                while round(x,11) < self.width: # Same as above
                    pixel = data[rnd(y)*(self.width+1) + rnd(x) + 1]
                    rescaled_data.append(pixel)
                    x += step
                y += step       
                
        elif rate > 1:
            # y = 0
            # while round(y,11) < self.height: # Cause x.99999... happens in our dear Python
            #     x = 0
            #     if floor(y) != floor(round(y-step,11)):
            #         rescaled_data.append(tuple("\n"))
            #         row = list(data[1:self.width+1])
            #         data = data[self.width+1:]
            #         while round(x,11) < self.width: # Same as above
            #             if floor(x) != floor(round(x-step,11)):
            #                 rescaled_data.append(row[0])
            #                 row.pop(0)
            #             else:
            #                 rescaled_data.append(rescaled_data[-1])
            #             x += step
                # else:
                #     rescaled_data += rescaled_data[-rescaled_width-1:]
                # y += step

            pass
        else:
            rescaled_data = data
        
        return tuple(rescaled_data)


# 记得加进度条 大图片会很慢
    def to_hex(self,output_rela=None,output_abs=None,
               decompress=True,origin=False) -> str:
        """Display the Hex code of the picture
        if both output options are None, it'll return a string"""
        def bytes_to_hex(bytes,):
            """Turn a series of bytes in to a string containing Hex codes grouped by 2 
            and connected by spaces"""
            str = ""
            for byte in bytes:
                if byte < 16:
                    str += "0" + hex(byte)[2:].upper() + " "
                else:
                    str += hex(byte)[2:].upper() + " "
            return str
        
        def chunk_type(bytes):
            """Turn 4 bytes into 4 letters using ASCII"""
            str = ""
            for byte in bytes:
                str += chr(byte)
            return str

        def ihdr():
            """List the IHDR chunk of the picture"""
            hex_ihdr = bytes_to_hex(self.bytes[16:29])
            hex_width = bytes_to_hex(self.bytes[16:20])
            hex_height = bytes_to_hex(self.bytes[20:24])
            str = f"""
{self.file}

\033[1;37m 1 \t\t|Signiture:       89 50 4E 47 0D 0A 1A 0A
\033[0;37m 2 \t\t|
\033[1;37m 3 \t\t|Length:                      00 00 00 0D          13
\033[0;37m 4 \t\t|Chunk Type:                  49 48 44 52          IHDR
\033[1;37m 5 \t\t|Chunk Data:                  {hex_ihdr}
\033[0;37m 6 \t\t|      width:                 {hex_width}         \
{self.width}
\033[1;37m 7 \t\t|      height:                {hex_height}         \
{self.height}
\033[0;37m 8 \t\t|      bit_depth:             {bytes_to_hex(self.bytes[24:25])}\
{" "*18}{self.bytes[24]:2d}
\033[1;37m 9 \t\t|      color_type:            {bytes_to_hex(self.bytes[25:26])}\
{" "*18}{self.bytes[25]:2d}
\033[0;37m 10\t\t|      compression_method:    {bytes_to_hex(self.bytes[26:27])}\
{" "*18}{self.bytes[26]:2d}
\033[1;37m 11\t\t|      filter_method:         {bytes_to_hex(self.bytes[27:28])}\
{" "*18}{self.bytes[27]:2d}
\033[0;37m 12\t\t|      interlace_method:      {bytes_to_hex(self.bytes[28:29])}\
{" "*18}{self.bytes[28]:2d}
\033[1;37m 13\t\t|CRC:                         {bytes_to_hex(self.bytes[29:33])}
\033[0;37m 14\t\t|
\033[1;37m 15\t\t|Ancillary chunks:"""
            return str

        def process_a_chunks(line_num):
            """List the ancillary chunks of the picture"""
            bytes = self.bytes[33:self.bytes.find(b'IDAT')-4]
            str = ""

            # No acnillary chunk
            if len(bytes) == 0:
                str += f"""
\033[{int((line_num+1) % 2)};37m {line_num+1} \t|There's no ancillary chunks in the picture
\033[{int((line_num+2) % 2)};37m {line_num+2} \t|"""
                line_num += 2
                return str,line_num
            
            while len(bytes) != 0:
                chunk_len = int.from_bytes(bytes[:4])

                str += f"""
\033[{int((line_num+1) % 2)};37m {line_num+1} \t|Length:                      {bytes_to_hex(bytes[0:4])}\
{" "*10}{chunk_len}
\033[{int((line_num+2) % 2)};37m {line_num+2} \t|Chunk Type:                  {bytes_to_hex(bytes[4:8])}\
{" "*10}{chunk_type(bytes[4:8])}
\033[{int((line_num+3) % 2)};37m {line_num+3} \t|Chunk Data:                  {bytes_to_hex(bytes[8:8+chunk_len])}
\033[{int((line_num+4) % 2)};37m {line_num+4} \t|CRC:                         {bytes_to_hex(
bytes[8+chunk_len:12+chunk_len])}
\033[{int((line_num+5) % 2)};37m {line_num+5} \t|"""

                line_num += 5
                # Delete the used chunk and get into next cycle
                bytes = bytes[12+chunk_len:]
            return str,line_num
        
        def idat_d(line_num):
            """Decode the IDAT chunk and list it"""
            # Decode
            if hasattr(self,"decoded_idat_16"):
                data = self.decoded_idat_16
            else:
                data = self.decode(16,False)

            str,row = "\n",0
            # 3 Channels    R G B
            if self.channels == 3:
                for pixel in data:
                    # A new row
                    if pixel[0] == "\n":
                        row += 1
                        line_num += 1
                        str += f"\n\033[{int((line_num) % 2)};37m {line_num} \t|{pixel[1]}{' '*10}row:{row}\n"
                    
                    # Pixels in the same row
                    else:
                        pixel = (pixel[0],pixel[1],pixel[2],
                             int(pixel[0],16),int(pixel[1],16),int(pixel[2],16))
                        color = f"\033[38;2;{pixel[3]};{pixel[4]};{pixel[5]}m██\033[0m"
                        if output_abs != None or output_rela != None:
                            color = "██"
                        
                        line_num += 1
                        str += f"""\033[{int((line_num) % 2)};37m {line_num} \t|\
{pixel[0]} {pixel[1]} {pixel[2]}\t{pixel[3]},{pixel[4]},{pixel[5]}\t{color}\n"""
            
            # 4 Channels    R G B alpha
            elif self.channels == 4:
                for pixel in data:
                    # A new row
                    if pixel[0] == "\n":
                        row += 1
                        line_num += 1
                        str += f"\033[{int((line_num) % 2)};37m {line_num} \t|{pixel[1]}{' '*13}row:{row}\n"
                    
                    # Pixels in the same row
                    else:
                        pixel = (pixel[0],pixel[1],pixel[2],pixel[3],
                             int(pixel[0],16),int(pixel[1],16),int(pixel[2],16),int(pixel[3],16))
                        color = f"\033[38;2;{pixel[4]};{pixel[5]};{pixel[6]}m██\033[0m"
                        
                        line_num += 1
                        str += f"""\033[{int((line_num) % 2)};37m {line_num} \t|\
{pixel[0]} {pixel[1]} {pixel[2]} {pixel[3]}\t{pixel[4]},{pixel[5]},{pixel[6]},{pixel[7]}\t{color}\n"""

            return str,line_num
        
        def idat(line_num):
            """List the IDAT chunck without decoding"""
            data = bytes_to_hex(self.idat)
            str = ""

            from shutil import get_terminal_size
            terminal_width = get_terminal_size()[0]
            # Make sure every row display hex in a nice way
            p = terminal_width//4*3
            i = 0
            while i*p<len(data):
                str += f"\t\t|{data[i*p:(i*p+p)]}\n"
                i+=1

            str = f"""
\033[{int((line_num+1) % 2)};37m {line_num+1} \t|Compressed IDAT chunk:
\033[{int((line_num+2) % 2)};37m {line_num+2} \t|{str[2:-1]}"""
            line_num += 2
            return str,line_num
        
        def iend(line_num):
            str = f"""
\033[{int((line_num+1) % 2)};37m {line_num+1} \t|
\033[{int((line_num+2) % 2)};37m {line_num+2} \t|Length:                      00 00 00 00          0
\033[{int((line_num+3) % 2)};37m {line_num+3} \t|Chunk Type:                  49 45 4E 44          IEND
\033[{int((line_num+4) % 2)};37m {line_num+4} \t|CRC:                         AE 42 60 82          \\xaeB`\\82
"""
            return str

        string = ""
        # IHDR
        str = ihdr()
        string += str
        # acnillary 
        str,line_num = process_a_chunks(line_num=15)
        string += str
        # IDAT
        if decompress == True:
            str,line_num = idat_d(line_num)
            string += str  
        else:
            str,line_num = idat(line_num)
            string += str
        # IEND
        str = iend(line_num)
        string += str

        if origin == True:
            string += "\n\nOriginal Hex:\n" + bytes_to_hex(self.bytes)

        # Output the result,
        if output_rela == None and output_abs == None:
            return string
        elif output_rela != None and output_abs == None:
            decoder_directory = "\\".join(__file__.split("\\")[:-1])
            file = decoder_directory + "\\" + output_rela
        elif output_rela == None and output_abs != None:
            file = output_abs
        else:
            raise Exception(f"""
Parameter Error
\tThe decoder will take either of the filepath_rela or filepath_abs, 
\tIf both are None, it will return the string
\tfilepath_rela: {repr(output_rela)},        filepath_abs: {repr(output_abs)}            
            """)

        string = string.split("\n")
        revised_string = ""
        for line in string:
            if line[0:2] == "\033[":
                revised_string += line[7:] + "\n"
            else:
                revised_string += line + "\n"

        with open(file,"w") as txt:
            txt.write(revised_string)
        



if __name__ == "__main__":

    # PNG("pics\\rgb").display(auto_resacle=False)
    # PNG("pics\\Cola").display(auto_resacle=False)
    PNG("pics\\319").to_hex(output_rela="decoded_319")
    # PNG("pics\\mutiIDAT_PNG").display()
    # PNG("pics\\Cola").display()
    # PNG("pics\\rgb").display()
    # pic = PNG("pics\\multiIDAT_PNG")
    # pic.rescale(pic.decode(10))
    # PNG("pics\\multiIDAT_rescaled_400x315_web_dog").display()
    # PNG("pics\\multiIDAT_rescaled_392x310_web_starry_night").display()
    # PNG("pics\\multiIDAT_web_starry_night").display()

    # tp = PNG("pics\\furnace_front_on").decode(10)
    # tp = PNG("pics\\multiIDAT_web_starry_night").decode(10)
    # tp = PNG("pics\\rgb").decode(10)
    # import pickle

    # with open("E:\\Desktop\\multiIDAT_web_starry_night","wb") as cache:
    #     pickle.dump(tp, cache)

    # tp = PNG("pics\\multiIDAT_web_starry_night")
    # with open("E:\\Desktop\\multiIDAT_web_starry_night","rb") as cache:
    #     tp.decoded_idat_10 = pickle.load(cache)
    # print("done")
    # tp.display()




    # from time import time
    # import os

    # pic1 = PNG("pics\\multiIDAT_PNG")
    # time_record = []

    # os.system('cls')

    # tm = time()
    # pic1.display()
    # tm = time()-tm
    # time_record.append(tm)

    # os.system('cls')

    # tm = time()
    # pic1.display()
    # tm = time()-tm
    # time_record.append(tm)

    # os.system('cls')
    # print(time_record[0],time_record[1],time_record[0]-time_record[1])

    # PNG("pics\\rgb").display()

    # pic1 = PNG("pics\\mutiIDAT_rescaled_392x310_web_starry_night")
    # PNG("pics\\mutiIDAT_rescaled_392x310_web_starry_night").display()
    # PNG("pics\\mutiIDAT_rescaled_392x310_web_starry_night").display()
    # print(PNG("pics\\mutiIDAT_PNG").to_hex(
    #     decompress=False,origin=True,
    #     ))
    # PNG("pics\\i").to_hex(
    #     # decompress=False,
    #     origin=True,
    #     output_rela="output.txt"
    # )
    # PNG("pics\\i").display()
    # print(PNG("pics\\i").to_hex())
    # print(
    #     PNG("pics\\i").to_hex(
    #     # decompress=False,
    #     origin=True,
    # )
    # )

    pass    