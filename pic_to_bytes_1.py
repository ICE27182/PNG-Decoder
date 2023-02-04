

def chunk_len(b):
    return b[0]*256**3+b[1]*256**2+b[2]*256+b[3] # len(b)==4

def pic_to_bytes(
                filename,
                filepath="E:\\Desktop\\P&C\\Python\\png_decoder\\pics\\",
                output="E:\\Desktop\\P&C\\Python\\png_decoder\\output.txt",
                trans = True,
                other = True,
                ):
    
    filename = str(filename)
    if len(filename) > 4 and filename[-4:] == ".png":
        file = f"{filepath}{filename}"
    if other and len(filename) > 4 and filename[-4] == ".":
        file = f"{filepath}{filename}"
    else: 
        file = f"{filepath}{filename}.png"
    
    with open(file,"rb") as img:
        b = img.read(-1)
    
    s = "\n"
    if trans == True:
        s = bytes_to_formate_string(b)
        
    if type(output) == str:
        with open(output,"w") as txt:
            txt.write(f"{file}\n{str(b)}\n{s}")
    elif output in (True,"print","p",None):
        print(f"{file}\n{b}\n{s}")
    else:
        raise Exception(f"Unknow parameter\noutput: {output}")

def bytes_to_formate_string(bin):

    '''
    bin = str(bin)[2:-1]
    if bin[0:37] != "\\x89PNG\\r\\n\\x1a\\n\\x00\\x00\\x00\\rIHDR\\x":
        raise Exception("I don't know what's happening.\n" +
                        "The file should begin with" +
                        "\"\\x89PNG\\r\\n\\x1a\\n\\x00\\x00\\x00\\rIHDR\\x\", " +
                        f"while it begins with \"{bin[0:37]}\"")
    IHDR_i = 31
    width = bin[IHDR_i+4:IHDR_i+20]                 # [IHDR_i+4:IHDR_i+4+16]
    height = bin[IHDR_i+20:IHDR_i+36]               # [IHDR_i+4+16:IHDR_i+4+16+16]
    bit_depth = bin[IHDR_i+36:IHDR_i+40]            # [IHDR_i+4+16+16:IHDR_i+4+16+16+4]
    color_type = bin[IHDR_i+40:IHDR_i+44]           # [IHDR_i+4+16+16+4:IHDR_i+4+16+16+4+4]
    compression_method = bin[IHDR_i+44:IHDR_i+48]   # [IHDR_i+4+16+16+4+4:IHDR_i+4+16+16+4+4+4]
    filter_method = bin[IHDR_i+48:IHDR_i+52]        # [IHDR_i+4+16+16+4+4+4:IHDR_i+4+16+16+4+4+4+4]
    interlace_method = bin[IHDR_i+52:IHDR_i+56]     # [IHDR_i+4+16+16+4+4+4+4:IHDR_i+4+16+16+4+4+4+4+4]
    IDAT_i = bin.find("IDAT")
    IEND_i = bin.find("IEND")
    bin = f"""
    {bin[0:IHDR_i]}
    {bin[IHDR_i:IHDR_i+4]}
    \t{width}
    \t{height}
    \t{bit_depth}
    \t{color_type}
    \t{compression_method}
    \t{filter_method}
    \t{interlace_method}
    \t{bin[IHDR_i+56:IDAT_i]}
    {bin[IDAT_i:IDAT_i+4]}
    \t{bin[IDAT_i+4:IEND_i]}
    {bin[IEND_i:IEND_i+4]}
    \t{bin[IEND_i+4:]}
    """
    bin = str(bin)[2:-1]
    '''
    
    if bin[0:8] != b'\x89PNG\r\n\x1a\n':
        raise Exception("It's not a png file.\n" +
                        "Png files should begin with" +
                        "b'\\x89PNG\\r\\n\\x1a\\n'\n" +
                        f"Its header: {bin[0:37]}")
    if b"PLTE" in bin:
        raise Exception("There're PLTE(which contains the palette: a list of colors) in the picture" +
                        "and I'm too foolish to figure it out.")
    
    # width = bin[16:20]
    # height = bin[20:24]
    # bit_depth = bin[24:25]
    # color_type = bin[25:26]
    # compression_method = bin[26:27]
    # filter_method = bin[27:28]
    # interlace_method = bin[28:29]
    IDAT_i = bin.find(b'IDAT')
    IEND_i = bin.find(b'IEND')
    
    bin = f"""
{bin[0:8]}    ----PNG----

{bin[8:12]}
{bin[12:16]}    ----IHDR----
\t{bin[16:20]}    ----width----
\t{bin[20:24]}    ----height----
\t{bin[24:25]}    ----bit_depth----
\t{bin[25:26]}    ----color_type----
\t{bin[26:27]}    ----compression_method----
\t{bin[27:28]}    ----filter_method----
\t{bin[28:29]}    ----interlace_method----
{bin[29:33]}    ----CRC----

{ancillary_chunks(bin)}

{bin[IDAT_i-4:IDAT_i]} ----Length_correct: {chunk_len(bin[IDAT_i-4:IDAT_i]) == len(bin[IDAT_i+4:IEND_i-8])}----
{bin[IDAT_i:IDAT_i+4]}    ----IDAT----
\t{bin[IDAT_i+4:IEND_i-8]}
\t{process_idat(bin)}
{bin[IEND_i-8:IEND_i-4]}    ----CRC----

{bin[IEND_i-4:IEND_i]}
{bin[IEND_i:IEND_i+4]}    ----IEDN----
{bin[IEND_i+4:]}    ----CRC----
    """
    
    # bin = "  ".join(bin.split("\\x"))
    return "\n\n" + bin

def ancillary_chunks(bin):
    bin = bin[33:bin.find(b'IDAT')-4]
    if (ac_len := len(bin)) == 0:
        return b''
    
    chunks = []
    while ac_len != 0:
        l = chunk_len(bin[0:4])
        chunks.append("\n".join(
            (
            str(bin[0:4])[2:-1],
            str(bin[4:8])[2:-1],
            str(bin[8:8+l])[2:-1],
            str(bin[8+l:12+l])[2:-1],
             )
            ))
        ac_len -= (l+12)
        bin = bin[l+12:]
    return "\n\n".join(chunks)

def process_idat(bin):
    IDAT_i = bin.find(b'IDAT')
    IEND_i = bin.find(b'IEND')
    if bin.count(b'IDAT') == 1:
        idat = bin[IDAT_i+4:IEND_i-8]
    else:
        raise Exception("This version of the decoder can only decode png file with a single IDAT chunk.")
    width = int.from_bytes(bin[16:20])
    color_type = bin[25:26]

    idat = decompress(idat)
    string = ""
    i=0

    if color_type == b'\x02':
        channels = 3
    elif color_type == b'\x06':
        channels = 4

    for index,byte in enumerate(idat):
        # byte = hex(byte[0])[2:].upper()
        byte = hex(byte)[2:]
        if len(byte) == 1:
            byte = f"0{byte}"

        if index % (width*channels+1) == 0:
            string += f"\n{byte}\n"
            if byte != "00":
                print("\033[F"*500)
                print("\n\n\n\033[1;31mWarning:\n"+
                      "\tThe file has one or more rows that use filtering, "+
                      "which this version of decoder is unable to handle.\n"+
                      "What it will show will be Wrong.\033[0m")
        else:
            string += byte + " "
            i += 1
            if i == channels:
                i = 0
                string += "\n"
    return string


if __name__ == "__main__":
    from zlib import decompress
    names=[
    "grass_block_snow",     # 0
    "crafting_table_front", # 1
    "crafting_table_side",  # 2
    "crafting_table_top",]  # 3
    pic_to_bytes(
                505,
                # "ice27182",
                # names[0],
                # names[2],
                # "i",
                # output=None,
                # trans=False,
                other=False
                 )
    