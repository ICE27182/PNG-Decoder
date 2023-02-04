

class PNG:
    version = "v0.1"
    README = f"""
    version: {version}
        It's a PNG decoder based on Python. 
        Written without any third-party library, 
        there'll be no need to download any other libraries to use the decoder.
        
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
    def __init__(self,filepath_rela=None,filepath_abs=None,check=True,readme=False) -> None:
        """filepath_rela is based on the path of the decoder file,
        while filepath_abs is the absolute file path.
        The decoder will take either of them, 
        but one and no more than one must be given.

        (etc. to decode pic.png that is in the same directory as the decoder,
        it should be in 
        (PNG(filepath_rela="pic.png"), PNG(filepath_rela="pic"), 
        PNG("pic.png"), PNG("pic"), 
        PNG(filepath_abs="E:\\Desktop\\decoder\\pic"),
        PNG(filepath_abs="E:\\Desktop\\decoder\\pic.png")"""
        if readme == True:
            PNG.readme()

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
        


    def readme():
        print(PNG.README)
        return PNG.README

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
        if self.bytes.count(b'IDAT') != 1:
            raise Exception(f"""
Decoder Error        version: {PNG.version}
\tThis version of decoder doesn't support png files with multiple IDAT chunks.
            """)
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

        idat_i = self.bytes.find(b'IDAT')
        idat_len = int.from_bytes(self.bytes[idat_i-4:idat_i])
        self.idat = self.bytes[idat_i+4:idat_i+4+idat_len]



    def decode(self,type,info=True):
        """Decode the IDAT field to a list. e.g.[("\n",00),(R,G,B,a),(R,G,B,a),...,("\n",00),(R,G,B,a)...]
        The current version can only decode png files with None filtering correctly."""
        if type not in ("D","d","Decimal","decimal",10,"H","h","Hex","hex",16):
            raise Exception(f"""
Parameter Error
\tThe output type for decoding support only hex or decimal, which can be
\ttyped as ("D","d","Decimal","decimal",10,"H","h","Hex","hex",16)
\tInvalid parameter: {repr(type)}
            """)
        
        if info == True:
            print("Decoding...")

        # Decode the Huffman and LZSS part
        import zlib
        data = zlib.decompress(self.idat)

        data_list= []  # e.g.[("\n",00),(R,G,B,a),(R,G,B,a),...,("\n",00),(R,G,B,a)...]
        period = self.width*self.channels + 1
        t,cach,stat = 0,[],True
        for i,byte in enumerate(data):
            # Get the list of Hex, mainly for to_hex()
            if type in ("H","h","Hex","hex",16):
                byte = hex(byte)[2:].upper()
                if len(byte) == 1:
                    byte = f"0{byte}"
            # Every new row
            if i % period == 0:     
                data_list.append(("\n",byte))
                # Filtering is not None
                if stat == True and byte not in (0,"00"):
                    print(f"""\033[1;31;5m
███---Warning---███\033[0m\033[1;33m
\tThis version of decoder doesn't support filtering except for None, 
\tso problems may occur.
           \033[0m""")
                    stat = False
            # Get the list of Decimal, mainly for display()
            else:
                t += 1
                cach.append(byte)
                if t == self.channels:      # Every pixel
                    data_list.append(tuple(cach))
                    t = 0
                    cach.clear()
        
        if info == True:
            print("Decoding done")

        return data_list


    def display(self,render_mode=1):
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
    

    def to_hex(self, output_rela=None,output_abs=None,decompress=True,orgin=False):
        """Display the Hex code of the picture"""
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

\033[1;37m 1 \t|Signiture:       89 50 4E 47 0D 0A 1A 0A
\033[0;37m 2 \t|
\033[1;37m 3 \t|Length:                      00 00 00 0D          13
\033[0;37m 4 \t|Chunk Type:                  49 48 44 52          IHDR
\033[1;37m 5 \t|Chunk Data:                  {hex_ihdr}
\033[0;37m 6 \t|      width:                 {hex_width}         \
{self.width}
\033[1;37m 7 \t|      height:                {hex_height}         \
{self.height}
\033[0;37m 8 \t|      bit_depth:             {bytes_to_hex(self.bytes[24:25])}\
{" "*18}{self.bytes[24]:2d}
\033[1;37m 9 \t|      color_type:            {bytes_to_hex(self.bytes[25:26])}\
{" "*18}{self.bytes[25]:2d}
\033[0;37m 10\t|      compression_method:    {bytes_to_hex(self.bytes[26:27])}\
{" "*18}{self.bytes[26]:2d}
\033[1;37m 11\t|      filter_method:         {bytes_to_hex(self.bytes[27:28])}\
{" "*18}{self.bytes[27]:2d}
\033[0;37m 12\t|      interlace_method:      {bytes_to_hex(self.bytes[28:29])}\
{" "*18}{self.bytes[28]:2d}
\033[1;37m 13\t|CRC:                         {bytes_to_hex(self.bytes[29:33])}
\033[0;37m 14\t|
\033[1;37m 15\t|Ancillary chunks:"""
            return str

        def process_a_chunks(line_num):
            """List the ancillary chunks of the picture"""
            bytes = self.bytes[33:self.bytes.find(b'IDAT')-4]
            str = ""

            # No acnillary chunk
            if len(bytes) == 0:
                str += f"""
\033[{int((line_num+1) % 2)};37m {line_num+1}\t|There's no ancillary chunks in the picture
\033[{int((line_num+2) % 2)};37m {line_num+2}\t|"""
                line_num += 2
                return str,line_num
            
            while len(bytes) != 0:
                chunk_len = int.from_bytes(bytes[:4])

                str += f"""
\033[{int((line_num+1) % 2)};37m {line_num+1}\t|Length:                      {bytes_to_hex(bytes[0:4])}\
{" "*10}{chunk_len}
\033[{int((line_num+2) % 2)};37m {line_num+2}\t|Chunk Type:                  {bytes_to_hex(bytes[4:8])}\
{" "*10}{chunk_type(bytes[4:8])}
\033[{int((line_num+3) % 2)};37m {line_num+3}\t|Chunk Data:                  {bytes_to_hex(bytes[8:8+chunk_len])}
\033[{int((line_num+4) % 2)};37m {line_num+4}\t|CRC:                         {bytes_to_hex(
bytes[8+chunk_len:12+chunk_len])}
\033[{int((line_num+5) % 2)};37m {line_num+5}\t|"""

                line_num += 5
                # Delete the used chunk and get into next cycle
                bytes = bytes[12+chunk_len:]
            return str,line_num
        
        def idat_d(line_num):
            """Decode the IDAT chunk and list it"""
            # Decode
            data = self.decode(16,False)

            str,row = "\n",0
            # 3 Channels    R G B
            if self.channels == 3:
                for pixel in data:
                    # A new row
                    if pixel[0] == "\n":
                        row += 1
                        line_num += 1
                        str += f"\n\033[{int((line_num) % 2)};37m {line_num}\t|{pixel[1]}{' '*13}row:{row}\n"
                    
                    # Pixels in the same row
                    else:
                        pixel = (pixel[0],pixel[1],pixel[2],
                             int(pixel[0],16),int(pixel[1],16),int(pixel[2],16))
                        color = f"\033[38;2;{pixel[3]};{pixel[4]};{pixel[5]}m██\033[0m"
                        
                        line_num += 1
                        str += f"""\033[{int((line_num) % 2)};37m {line_num}\t|\
{pixel[0]} {pixel[1]} {pixel[2]}\t{pixel[3]},{pixel[4]},{pixel[5]}\t{color}\n"""
            
            # 4 Channels    R G B alpha
            elif self.channels == 4:
                for pixel in data:
                    # A new row
                    if pixel[0] == "\n":
                        row += 1
                        line_num += 1
                        str += f"\033[{int((line_num) % 2)};37m {line_num}\t|{pixel[1]}{' '*13}row:{row}\n"
                    
                    # Pixels in the same row
                    else:
                        pixel = (pixel[0],pixel[1],pixel[2],pixel[3],
                             int(pixel[0],16),int(pixel[1],16),int(pixel[2],16),int(pixel[3],16))
                        color = f"\033[38;2;{pixel[4]};{pixel[5]};{pixel[6]}m██\033[0m"
                        
                        line_num += 1
                        str += f"""\033[{int((line_num) % 2)};37m {line_num}\t|\
{pixel[0]} {pixel[1]} {pixel[2]} {pixel[3]}\t{pixel[4]},{pixel[5]},{pixel[6]},{pixel[7]}\t{color}\n"""

            return str,line_num
        

        def idat(line_num):
            """List the IDAT chunck without decoding"""
            data = bytes_to_hex(self.idat)
            str = ""

            import shutil
            terminal_width = shutil.get_terminal_size()[0]
            # Make sure every row display hex in a nice way
            p = terminal_width//4*3
            i = 0
            while i*p<len(data):
                str += f"\t|{data[i*p:(i*p+p)]}\n"
                i+=1

            str = f"""
\033[{int((line_num+1) % 2)};37m {line_num+1}\t|Compressed IDAT chunk:
\033[{int((line_num+2) % 2)};37m {line_num+2}\t|{str[2:]}\
\033[{int((line_num+3) % 2)};37m {line_num+3}\t|"""
            line_num += 3
            return str,line_num
        
        def iend(line_num):
            str = f"""
\033[{int((line_num+1) % 2)};37m {line_num+1}\t|
\033[{int((line_num+2) % 2)};37m {line_num+2}\t|Length:                      00 00 00 00          0
\033[{int((line_num+3) % 2)};37m {line_num+3}\t|Chunk Type:                  49 45 4E 44          IEND
\033[{int((line_num+4) % 2)};37m {line_num+4}\t|CRC:                         AE 42 60 82          \\xaeB`\\82
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

        if orgin == True:
            string += "\n\n\n" + self.bytes

        # Output the result,
        if output_rela == None and output_abs == None:
            return string
        elif output_rela != None and output_abs == None:
            decoder_directory = "\\".join(__file__.split("\\")[:-1])
            file = decoder_directory + output_rela
        elif output_rela == None and output_abs != None:
            file = output_abs
        else:
            raise Exception(f"""
Parameter Error
\tThe decoder will take either of the filepath_rela or filepath_abs, 
\tIf both are None, it will return the string
\tfilepath_rela: {repr(output_rela)},        filepath_abs: {repr(output_abs)}            
            """)
            
        with open(file,"w") as txt:
            txt.write(string)



if __name__ == "__main__":
    # from time import sleep
    # PNG.readme()
    # sleep(2)
    # PNG("pics\\ice").display(0)
    # print(PNG("pics\\ice").to_hex())
    # sleep(5)
    # i = PNG("pics\\720p_7.png")
    # print(i.to_hex(decompress=False))
    PNG("pics\\grass_block_snow").display()
    PNG("pics\\furnace_front_on").display()
    PNG("pics\\crafting_table_front").display()
    PNG("pics\\crafting_table_top").display()
    PNG("pics\\rgb").display()
    