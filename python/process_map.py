import numpy as np
import json
from math import sqrt, pi
from PIL import Image, ImageDraw, ImageFont


class Port(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.density = None

    def cal_density(self, map, res, r):
        road = 0
        h, w = map.shape[:2]
        for i in range(self.x - r, self.x + r):
            for j in range(self.y - r, self.y + r):
                if i >= 200 and j >= 0 and i < h and j < w and l2_distance2(i, j, self.x, self.y) <= r:
                    if (res[i][j] > 0 and res[i][j] != 128):
                        road += 1
                        map[i][j][0] = 255
                        map[i][j][1] = 255
                    else:
                        res[i][j] = 128
        self.density = road / round(pi * r ** 2)
        print('port at (%i, %i), road density: %f' % (self.x, self.y, road / round(pi * r ** 2)))
        return self.density


def l1_distance2(x1, y1, x2, y2):
    return abs(x2-x1) + abs(y2-y1)


def l2_distance2(x1, y1, x2, y2):
    return sqrt((x2-x1)**2 + (y2-y1)**2)


def l1_distance3(x1, y1, z1, x2, y2, z2):
    return abs(x2-x1) + abs(y2-y1) + abs(z2-z1)


def process_annotation(scale_json, port_json):
    port_list = []
    scale_json = json.load(open(scale_json))
    port_json = json.load(open(port_json))
    scale = scale_json['shapes'][0]['points']
    ports = port_json['shapes'][0]['points']
    scale = l2_distance2(scale[0][0], scale[0][1], scale[1][0], scale[1][1])
    for x, y in ports:
        port_list.append(Port(y, x))
    return round(scale), port_list


def recognize_road(map, res, threshold, samples):
    h, w = map.shape[:2]
    for i in range(h):
        for j in range(w):
            rgb = map[i][j][:]
            r, g, b = rgb[0], rgb[1], rgb[2]
            for sample in samples:
                rr, gg, bb = sample
                if l1_distance3(r, g, b, rr, gg, bb) <= threshold:
                    res[i][j] = 255
                    break


def main():
    img = np.array(Image.open('figures/port.PNG'))
    raw = np.array(Image.open('figures/map.PNG'))
    res = np.zeros(shape=img.shape[:2], dtype=np.uint8)
    radius, ports = process_annotation('figures/scale.json', 'figures/port.json')
    h, w = img.shape[:2]

    recognize_road(raw, res, 30, samples=[
        (200, 200, 140),
        (223, 216, 162),
        (200, 195, 133),
        (208, 198, 139),
        (168, 169, 120),
        (171, 169, 120),
        (207, 199, 149),
    ])

    ports.sort(reverse=True, key=lambda p: p.cal_density(img, res, radius))

    # visualization 25km range
    for rank, p in enumerate(ports):
        print('rank %i, road density is %f' % (rank, p.density))
        for i in range(p.x - radius, p.x + radius):
            for j in range(p.y - radius, p.y + radius):
                if i >= 200 and j >= 0 and i < h and j < w and l2_distance2(i, j, p.x, p.y) <= radius:
                    if res[i][j] == 128:
                        if rank in [0, 1, 5]:
                            img[i][j][0] = 128
                        else:
                            img[i][j][2] = 128

    # add rank to the image
    image = Image.fromarray(img.astype('uint8'))
    for rank, p in enumerate(ports):
        txt = Image.new('RGBA', image.size, (255, 255, 255, 0))
        font = ImageFont.truetype('Consolas.ttf', size=40)
        ImageDraw.Draw(txt).text((p.y, p.x), '%i' % (rank + 1), font=font, fill=(255, 255, 255, 200))
        image = Image.alpha_composite(image, txt)

    # save and show
    res = Image.fromarray(res).convert('RGB')
    res.save('figures/result.jpg')
    res.show()
    image.save('figures/result.png')
    image.show()


def main2():
    img = np.array(Image.open('figures/map2.png'))
    h, w = img.shape[:2]
    scale, ports = json.load(open('figures/map2.json'))['shapes'][:2]
    scale = scale['points']
    ports = ports['points']
    radius = round(l2_distance2(scale[0][0], scale[0][1], scale[1][0], scale[1][1]) * (25 / 20))
    for p in ports:
        for i in range(p[1] - radius, p[1] + radius):
            for j in range(p[0] - radius, p[0] + radius):
                if i >= 0 and j >= 0 and i < h and j < w and l2_distance2(i, j, p[1], p[0]) <= radius:
                    img[i][j][0] = 128
    Image.fromarray(img).save('figures/result2.png')


if __name__ == '__main__':
    main2()
