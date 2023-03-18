import png_decoder_0_2
img = png_decoder_0_2.PNG("pics\\ice")
d_img = img.decode(10)

import json
json_d_img = json.dumps(d_img)
print(d_img,end="\n\n\n")
print(json_d_img,end="\n\n\n")

print(d_img == json.loads(json_d_img))

pass