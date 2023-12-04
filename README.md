# PNG Decoder
It's a png decoder full written in python.  
Only using python standard library, you shall have no troble runing it
with just python.  
It also support displaying the decoded image in terminal, with ANSI text.  

# Brief Guide
```
import png_decoder
img = png_decoder.Png(filename)
```
Use `print(img)` to print some basic information of the image
Use `img.display()` to print the image in the terminal
In the `img.pixels` stores every pixel in the image

