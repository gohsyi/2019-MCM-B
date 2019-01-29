import time
import threading
import numpy as np
from tqdm import tqdm
from itertools import permutations, product
from config import config

MULTI_THREAD = False


class Item(object):
    def __init__(self, type, container=(0, 1, 2)):
        self.type = type
        self.width = config.width[type]
        self.height = config.height[type]
        self.length = config.length[type]
        self.volume = self.width * self.height * self.length
        self.container = container


class Greedy(object):
    def __init__(self):
        self.items = []
        self.corners = {(0, 0, 0, 0), (1, 0, 0, 0), (2, 0, 0, 0)}
        self.occupied = np.zeros((config.n_contrainers, config.W, config.H, config.L), np.int8)

    def run(self):
        l, r = 1, 366
        while l < r - 1:
            time.sleep(0.1)  # for prettier output
            days = (l + r) >> 1
            tqdm.write('\ntrying to provide meds for %i days' % days)
            if self.greedy(days):
                l = days
            else:
                r = days
        self.greedy(l)
        print('max days: %i, utilization:' % l, self.utilization)

    def greedy(self, days, reset=True):
        if reset:
            self.__init__()
            self.add_drones(self.items)
            for _ in range(days):
                self.add_meds(self.items)
        # sort in descending order of volume
        self.items.sort(reverse=True, key=lambda item: item.volume)

        iterator = tqdm(self.items) if days > 1 else self.items
        for item in iterator:
            maximal_empty_spaces = None
            threads = []
            th_result = []
            for c, x, y, z in self.corners:
                if c not in item.container:
                    continue
                for w, h, l in permutations([item.width, item.height, item.length]):
                    if (x + w >= config.W or y + h >= config.H or z + l >= config.L):
                        continue
                    if np.any(self.occupied[c, x:x + w, y:y + h, z:z + l] > 0):
                        continue
                    if MULTI_THREAD:
                        threads.append(myThread(w, h, l, c, x, y, z, self.corners.copy()))
                        threads[-1].start()
                    else:
                        corner_list = self.corners.copy()
                        for d in product([0, w], [0, h], [0, l]):
                            add_corner(corner_list, np.array((c, x, y, z)) + np.array([0] + list(d)))
                        empty_spaces = cal_empty_space(corner_list)
                        if not maximal_empty_spaces or empty_spaces > maximal_empty_spaces[0]:
                            maximal_empty_spaces = empty_spaces, (c, x, y, z), (w, h, l)
            if MULTI_THREAD and threads:
                for th in threads:
                    th.join()
                    th_result.append(th.get_result())
                empty_spaces = [res[0] for res in th_result]
                empty_spaces, (c, x, y, z), (w, h, l) = th_result[int(np.argmax(empty_spaces))]
                if not maximal_empty_spaces or empty_spaces > maximal_empty_spaces[0]:
                    maximal_empty_spaces = empty_spaces, (c, x, y, z), (w, h, l)

            if not maximal_empty_spaces:
                if type(iterator) == tqdm:
                    iterator.close()
                return False

            (c, x, y, z), (w, h, l) = maximal_empty_spaces[1], maximal_empty_spaces[2]
            self.occupied[c, x:x + w, y:y + h, z:z + l] = 1
            self.refresh()
            for d in product([0, w], [0, h], [0, l]):
                add_corner(self.corners, np.array((c, x, y, z)) + np.array([0] + list(d)))

        self.utilization = [np.count_nonzero(self.occupied[i][:][:][:] == 1) / self.occupied[i][:][:][:].size
                            for i in range(config.n_contrainers)]
        return True

    def refresh(self):
        trash = []  # directly remove will cause error
        for p in self.corners:
            if self.occupied[p] == 1:
                trash.append(p)
        for p in trash:
            self.corners.remove(p)

    def add_drones(self, item_list):
        item_list.append(Item('DRONE H', [0]))
        item_list.append(Item('DRONE H', [1]))
        item_list.append(Item('DRONE H', [2]))
        item_list.append(Item('DRONE B', [0]))
        item_list.append(Item('DRONE F', [1]))
        for _ in range(2):
            item_list.append(Item('DRONE F', [2]))
        for _ in range(3):
            item_list.append(Item('DRONE B', [1, 2]))

    def add_meds(self, item_list):
        item_list.append(Item('MED 1', [0]))
        item_list.append(Item('MED 1', [1, 2]))
        item_list.append(Item('MED 3', [1, 2]))
        for _ in range(5):
            item_list.append(Item('MED 1', [1, 2]))
        for _ in range(2):
            item_list.append(Item('MED 2', [1, 2]))
        for _ in range(3):
            item_list.append(Item('MED 3', [1, 2]))


class myThread(threading.Thread):
    def __init__(self, w, h, l, c, x, y, z, corners):
        super().__init__()
        self.w = w
        self.h = h
        self.l = l
        self.c = c
        self.x = x
        self.y = y
        self.z = z
        self.corners = corners

    def run(self):
        for d in product([0, self.w], [0, self.h], [0, self.l]):
            add_corner(self.corners, np.array((self.c, self.x, self.y, self.z)) + np.array([0] + list(d)))
        self.empty_spaces = cal_empty_space(self.corners)

    def get_result(self):
        return self.empty_spaces, (self.c, self.x, self.y, self.z), (self.w, self.h, self.l)


def cal_empty_space(corners):
    return np.mean([
        np.max([p[0] for p in corners]) * config.L * config.H,
        np.max([p[1] for p in corners]) * config.H * config.W,
        np.max([p[2] for p in corners]) * config.L * config.W,
    ])


def add_corner(corner_list, corner):
    corner = tuple(corner)
    if corner not in corner_list:
        corner_list.add(corner)


if __name__ == '__main__':
    model = Greedy()
    # model.run()
    model.greedy(364)

    # util = 0.
    # day = 0
    # model.items = [Item('DRONE B', [0])]
    # while model.greedy(1, reset=False):
    #     if model.utilization[0] > util:
    #         util += 0.1
    #         print('utilization is', model.utilization[0])
    #     model.items = [Item('MED 1', [0])]
    #     day += 1
    # print('utilization is', model.utilization[0])

    # model.greedy(191)
    # print('utilization is', model.utilization)


"""
============ results singel container =============

trying to provide meds for 183 days
 35%|███▍      | 829/2386 [03:09<05:11,  5.00it/s]

trying to provide meds for 92 days
100%|██████████| 1203/1203 [18:33<00:00,  3.15s/it]

trying to provide meds for 137 days
 46%|████▋     | 828/1788 [03:15<03:49,  4.19it/s]

trying to provide meds for 114 days
100%|██████████| 1489/1489 [21:21<00:00,  2.68s/it]

trying to provide meds for 125 days
 51%|█████     | 830/1632 [05:17<03:45,  3.56it/s]

trying to provide meds for 119 days
 53%|█████▎    | 830/1554 [05:13<03:20,  3.61it/s]

trying to provide meds for 116 days
100%|██████████| 1515/1515 [26:00<00:00,  2.32s/it]

trying to provide meds for 117 days
100%|██████████| 1528/1528 [24:28<00:00,  2.25s/it]
  1%|          | 11/1541 [00:00<00:33, 45.77it/s]
trying to provide meds for 118 days
 54%|█████▍    | 830/1541 [04:59<03:04,  3.86it/s]
100%|██████████| 1528/1528 [24:09<00:00,  2.20s/it]
max days: 117, utilization: 0.406471

====================================================

trying to provide meds for 183 days
100%|██████████| 2386/2386 [54:08<00:00,  3.24s/it]

trying to provide meds for 274 days
 38%|███▊      | 1348/3569 [08:10<04:48,  7.70it/s]

trying to provide meds for 228 days
 45%|████▌     | 1348/2971 [08:11<03:07,  8.64it/s]

trying to provide meds for 205 days
 50%|█████     | 1349/2672 [08:06<02:45,  8.00it/s]

trying to provide meds for 194 days
 53%|█████▎    | 1348/2529 [08:07<02:13,  8.82it/s]

trying to provide meds for 188 days
100%|██████████| 2451/2451 [49:59<00:00,  2.79s/it]

trying to provide meds for 191 days
100%|██████████| 2490/2490 [48:10<00:00,  2.38s/it]

trying to provide meds for 192 days
 54%|█████▍    | 1349/2503 [08:12<02:34,  7.46it/s]
100%|██████████| 2490/2490 [47:55<00:00,  2.59s/it]
max days: 191, utilization: 0.642532

====================================================

100%|██████████| 2490/2490 [50:23<00:00,  2.56s/it]
utilization is [0.23478741425087402, 0.8385183271862273, 0.8542915610445675]

"""
