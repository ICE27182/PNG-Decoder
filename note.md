# png_decoder

## Format
Unchecked boxes do not mean that the image formats are not supported.
They just haven't been tested yet.
### RGB-a 6
- [x] 4 channels 8 bits 4 B/pixel  
- [ ] 4 channels 16 bits 8 B/pixel
### RGB 2
- [x] 3 channels 8 bits 3 B/pixel  
- [x] 3 channels 16 bits 6 B/pixel
### Index 3
- [x] 1 channel 1 bit 0.125B/pixel  
- [ ] 1 channel 2 bits 0.25B/pixel  
- [x] 1 channel 4 bits 0.5B/pixel  
- [x] 1 channel 8 bits 1B/pixel
### Grayscale-a 4
- [ ] 2 channels 8 bits 2B/pixel  
- [x] 2 channels 16 bits 4B/pixel
### Grayscale 0
- [ ] 1 channel 1 bit 0.125B/pixel  
- [ ] 1 channel 2 bits 0.25B/pixel  
- [x] 1 channel 4 bits 0.5B/pixel  
- [ ] 1 channel 8 bits 1B/pixel  
- [x] 1 channel 16 bits 2B/pixel

## Coding
- class Png  
    - \_\_init\_\_  
        - get_image_properties
        - get_palette
    - \_\_str\_\_  
    - decode  
        - get_chunk_length
        - check_crc
            - get_chunk_length
        ---
        - get_image_properties
            - check_crc
        - get_palette
            - check_crc
            - get_chunk_length
        - get_all_idat_data
            - check_crc  
            - get_chunk_length
        - defilter
            - left_value
            - upper_value
            - paeth_decide_which_pixel_to_add
                - left_value
                - upper_value
                - upper_left_value
        - interpret_bytes_to_color
            - get_digits
    - display  

- def bytes_to_hex
- def print_bytes
### Png
#### Attributes
- height: int
- width: int
- bit_depth: int
---
- color_type: int
- bytes_a_pixel_takes: float
- compression_method: int
- filter_method: int
- interlace_method: int
---
- crc: bool
- bin: bytes
---
- pixels: list [[(r, g, b, a), (...), ...], [...], ...]
---
- (palette): tuple ((r, g, b, PNG.de))
#### Methods
- \_\_init\_\_(self, filename, dir=".\\pics\\", pickle_dir="", from_pickle=True, to_pickle=True, crc=False) -> None:  
    Try to find if there is any pickle file for the image to be decoded. If so, load it; if not, decode it and try to store it.  
    - filename: str  
    - dir: str  
    - pickle_dir: str  
    - from_pickle: bool  
    - to_pickle: bool  
    - crc: bool  
    ---
    ```
    if stored:  
        read  
    else:  
        decode  
    ```
- decode(self, image_path) -> None:  
    Decode the image and stored the decoded image as self.pixles
    - image_path: str  
    ---
    ```
    self.bin = ~read(image_path)
    self.get_image_properties()
    if self.color_type == 3:
        self.get_palette()
    bytes_rows = self.get_all_idat_data()
    defiltered_bytes_rows = self.defilter(bytes_rows)
    self.pixels = self.interpret_bytes_to_color(defiltered_bytes_rows)
    ```
- get_image_properties(self) -> None:  
    Get image properties by reading the IHDR chunk
    ```
    self.width
    self.height
    self.bit_depth
    self.color_type
    self.bytes_a_pixel_takes
    self.compression_method
    self.filter_method
    self.interlace_method
    ```
- get_palette(self) -> None:  
    Get palette
    ```
    if not b'PLET' in self.bin:
        raise Exception("...")
    palette = ~get_palette_data_bytes(self.bin)
    self.palette = []
    ~put_into_palette(palette)
    ```
- get_idat_data(self) -> list:  
    Get all rows of decompressed bytes. Defiltering will be applied later  
    return rows [b'...', ...]
    ```
    idat_chunks_indices = ~get_all_idat_chunk_starting_indices(self.bin)
    idat_data = ~merge_all_idat_chunks_data(self.bin, idat_chunks_indices)
    idat_data = decompress(idat_data)
    rows = []
    for row_num in range(self.height):
        row.append(~get_a_row_of_data_from_idat_data(row_num))
    ```
- defilter(self, rows) -> list:
    Defilter all idat data rows and return them
    - rows: list (returned by get_idat_data)
    ```
    left_distance = ~(self.channels * self.bit_depth // 8)
    def left_value(x) -> int: ...
    def upper_value(x) -> int: ...
    def upper_left_value(x, y) -> int: ...
    def paeth_decide_which_pixel_to_add(x, y) -> tuple: ...
    defiltered_bytes = []
    for row_index, filtered_row in enumerate(rows):
        ~defilter_each_row_according_to_which_filter_each_row_uses(row_index, filtered_row)
    return defiltered_bytes
    ```
- interpret_bytes_to_color(self, rows:list) -> list:
    Turn defiltered row into RGB-alpha pixels
    - rows: list (returned by defilter)
    ```
    def get_digits(num:int) -> tuple: ...
    pixels = []
    ~add_pixels_according_to_color_type_and_bit_depth()
    return pixels
    ```


## What's worth noting
- `something in (A, B)` is better than `something == A or something == B`
- `list = []` is probably better than `list.clear()`
- `list == []` is slightly better than `len(list) == 0`
- `list.append(x); a = list` is better than `a = list + [x]`

