""" greedy policy with space division """
import time
import numpy as np
import csv
from copy import deepcopy
from tqdm import tqdm
from config import config
from itertools import permutations


class Scheme(object):
    def __init__(self):
        self.scheme = []
        for _ in range(config.n_contrainers):
            self.scheme.append([])

    def add_item(self, item, c):
        """ place item in container c """
        self.scheme[c].append(item)

    def analyse_item(self, item):
        """ analyse each type of item """
        res = {'total': 0}
        for c in range(config.n_contrainers):
            res['in container %i' % c] = self.scheme[c].count(item)
            res['total'] += res['in container %i' % c]
        return res

    def analyse_container(self, c):
        """ analyse each container """
        res = {}
        for item in config.drones:
            res[item] = self.scheme[c].count(item)
        for item in config.meds:
            res[item] = self.scheme[c].count(item)
        return res

    def utilization(self):
        """ calculate current utilization of each container """
        res = []
        for c, container in enumerate(self.scheme):
            util = 0
            for item in container:
                util += Item(item).v / config.V
            res.append(util)
        res.append(np.mean(res))
        return res


class Item(object):
    def __init__(self, type, container=(0, 1, 2)):
        self.w = config.width[type]
        self.h = config.height[type]
        self.l = config.length[type]
        self.v = self.w * self.h * self.l
        self.c = container
        self.type = type


class Greedy(object):
    def __init__(self):
        self.scheme = Scheme()
        self.items = []
        self.recycle = []
        self.spaces = [
            (2, config.W, config.H, config.L),  # container, width, height, length
            (1, config.W, config.H, config.L),
            (0, config.W, config.H, config.L)]

    def run(self):
        """ use binary search to find the max days of meds we can provide """
        l, r = 1, 1000
        while l < r - 1:
            days = (l + r) >> 1
            tqdm.write('\ntrying to provide meds for %i days ...' % days)
            if self.greedy(days):
                tqdm.write('utilization is %s' % str(self.scheme.utilization()))
                l = days
            else:
                tqdm.write('utilization is %s' % str(self.scheme.utilization()))
                r = days

        max_days = l
        tqdm.write('\nmax days: %i\noptimizing ...' % max_days)
        self.greedy(max_days)

        l, r = max_days, 1000
        scheme_ = deepcopy(self.scheme)
        spaces_ = deepcopy(self.spaces)
        while l < r - 1:
            days = (l + r) >> 1
            tqdm.write('\ntrying to provide meds for %i days ...' % days)
            if self.new_exp(scheme_, spaces_, days - max_days):
                tqdm.write('utilization is %s' % str(self.scheme.utilization()))
                l = days
            else:
                tqdm.write('utilization is %s' % str(self.scheme.utilization()))
                r = days
        tqdm.write('\noptimization finished, new max days: %i' % l)
        assert self.new_exp(scheme_, spaces_, l - max_days)
        return l

    def greedy(self, days, reset=True):
        """ calculate whether we can provide meds for `days` days according to our greedy algorithm """
        if reset:
            self.__init__()
            self.add_drones(self.items)
            for _ in range(days):
                self.add_meds(self.items)
        # sort in descending order of volume
        self.items.sort(key=lambda item: item.v, reverse=True)

        iterator = tqdm(self.items) if days > 1 else self.items
        for item in iterator:
            while len(self.spaces) > 0:
                max_transferable = None
                space = self.spaces.pop()
                if space[0] in item.c:
                    for w, h, l in permutations([item.w, item.h, item.l]):  # enumerate placement directions
                        if self.fit_in((w, h, l), space):
                            transferable = self.cal_transferable((w, h, l), space)
                            # update max_transferable
                            if not max_transferable or max_transferable[0] < transferable:
                                max_transferable = transferable, (w, h, l), space
                if max_transferable:
                    container = max_transferable[2][0]
                    self.scheme.add_item(item.type, container)
                    self.spaces.extend(reversed(self.recycle))
                    self.recycle.clear()
                    space_x, space_y, space_z = self.segment(max_transferable[1], max_transferable[2])
                    if space_z:
                        self.spaces.append(space_z)
                    if space_y:
                        self.spaces.append(space_y)
                    if space_x:
                        self.spaces.append(space_x)
                    break
                else:
                    self.recycle.append(space)
            else:
                if type(iterator) == tqdm:
                    iterator.close()
                self.spaces.extend(reversed(self.recycle))
                self.recycle.clear()
                time.sleep(0.01)  # for prettier output
                return False

        assert len(self.recycle) == 0
        time.sleep(0.01)
        return True

    def fit_in(self, item, space):
        """ whether item can fit in space """
        w, h, l = item
        _, ww, hh, ll = space
        return w <= ww and h <= hh and l <= ll

    def segment(self, item, space):
        """ segement space into space_x, space_y, space_z """
        w, h, l = item
        cc, ww, hh, ll = space
        space_x = (cc, ww - w, hh, ll) if ww > w else None
        space_y = (cc, w, hh, ll - l) if ll > l else None
        space_z = (cc, w, hh - h, l) if hh > h else None
        return space_x, space_y, space_z

    def cal_transferable(self, item, space):
        """ calculate transferable space after placing item in space """
        w, h, l = item
        _, ww, hh, ll = space
        return (ww - w) * (ll - l) * hh

    def add_drones(self, item_list):
        """ add drones to item_list according to our pre-calculation """
        # port 0
        item_list.append(Item('DRONE H', [0]))
        for _ in range(1 + 5):
            item_list.append(Item('DRONE B', [0]))
        # port 1
        item_list.append(Item('DRONE H', [1]))
        for _ in range(1):
            item_list.append(Item('DRONE G', [1]))
        for _ in range(3 + 10):
            item_list.append(Item('DRONE B', [1]))
        # port 2
        item_list.append(Item('DRONE H', [2]))
        for _ in range(1 + 4):
            item_list.append(Item('DRONE B', [2]))

        # port 2->1
        for _ in range(2):
            item_list.append(Item('DRONE B', [1, 2]))

        # consider backup drones
        # item_list.append(Item('DRONE H', [0]))
        # item_list.append(Item('DRONE B', [0]))
        # item_list.append(Item('DRONE H', [1]))
        # item_list.append(Item('DRONE B', [1]))
        # item_list.append(Item('DRONE G', [1]))
        # item_list.append(Item('DRONE H', [2]))
        # item_list.append(Item('DRONE B', [2]))

    def add_meds(self, item_list, share=False):
        """ add daily meds to item_list according to our pre-calculation """
        # port 0
        item_list.append(Item('MED 1', [0]))
        # port 1
        for _ in range(5):
            item_list.append(Item('MED 1', [1, 2] if share else [1]))
        for _ in range(2):
            item_list.append(Item('MED 2', [1, 2] if share else [1]))
        for _ in range(3):
            item_list.append(Item('MED 3', [1, 2] if share else [1]))
        # port 2
        item_list.append(Item('MED 1', [2, 1] if share else [2]))
        item_list.append(Item('MED 3', [2, 1] if share else [2]))

    def new_exp(self, scheme_, spaces_, days):
        del self.scheme
        del self.spaces
        self.scheme = deepcopy(scheme_)
        self.spaces = deepcopy(spaces_)
        self.items.clear()
        for _ in range(days):
            self.add_meds(self.items, share=True)
        return self.greedy(days, reset=False)


def main():
    ########## stage 1 ##########
    model = Greedy()
    max_days = model.run()

    ########## stage 2 ##########
    item_list = []
    for item in config.meds:
        item_list.append(Item(item, [0, 1, 2] if item == 'MED 1' else [1, 2]))
        # container 0 doesn't need MED 1
    item_list.sort(key=lambda item: item.v, reverse=True)
    space_list = model.spaces
    tqdm.write('\nrecycling ...')

    for i in tqdm(range(len(space_list), 0, -1)):
        while len(space_list) > i:
            space = space_list.pop()
            for item in item_list:
                model.items = [item]
                model.spaces = [space]
                model.recycle.clear()
                if model.greedy(1, reset=False):
                    space_list.extend(model.spaces)
                    break

    u = model.scheme.utilization()
    analyse = {}
    for item in config.drones:
        analyse[item] = model.scheme.analyse_item(item)
    for item in config.meds:
        analyse[item] = model.scheme.analyse_item(item)
    for c in range(config.n_contrainers):
        analyse[c] = model.scheme.analyse_container(c)

    # write to csv file
    with open('analyse.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['container'] + config.drones + config.meds + ['utilization'])
        for c in range(config.n_contrainers):
            res = model.scheme.analyse_container(c)
            writer.writerow([str(c)] + [res[item] for item in config.drones + config.meds] + [str(u[c])])

    # analyse inter-port delivery
    delta = {}
    delta['MED 1'] = max(0, 5 * max_days - analyse[1]['MED 1'])
    delta['MED 2'] = max(0, 2 * max_days - analyse[1]['MED 2'])
    delta['MED 3'] = max(0, 3 * max_days - analyse[1]['MED 3'])
    print(delta)
    delivery = delta['MED 1'] // 2 + delta['MED 3'] // 2 + delta['MED 2'] // 4
    tqdm.write('total delivery: %f' % delivery)


if __name__ == '__main__':
    main()


"""
****************************************************
* fill arbitrary meds, redundant drones (240 days) *
****************************************************

optimize finished, final utilization is {'container 0': 0.855704194048334, 'container 1': 0.8083494519664949, 'container 2': 0.8703971791391056, 'mean': 0.8448169417179783}
analyse DRONE A: {'total': 0, 'in container 0': 0, 'in container 1': 0, 'in container 2': 0}
analyse DRONE B: {'total': 8, 'in container 0': 2, 'in container 1': 4, 'in container 2': 2}
analyse DRONE C: {'total': 0, 'in container 0': 0, 'in container 1': 0, 'in container 2': 0}
analyse DRONE D: {'total': 0, 'in container 0': 0, 'in container 1': 0, 'in container 2': 0}
analyse DRONE E: {'total': 0, 'in container 0': 0, 'in container 1': 0, 'in container 2': 0}
analyse DRONE F: {'total': 6, 'in container 0': 0, 'in container 1': 2, 'in container 2': 4}
analyse DRONE G: {'total': 0, 'in container 0': 0, 'in container 1': 0, 'in container 2': 0}
analyse DRONE H: {'total': 6, 'in container 0': 2, 'in container 1': 2, 'in container 2': 2}
analyse MED 1: {'total': 2350, 'in container 0': 910, 'in container 1': 618, 'in container 2': 822}
analyse MED 2: {'total': 488, 'in container 0': 0, 'in container 1': 267, 'in container 2': 221}
analyse MED 3: {'total': 1682, 'in container 0': 595, 'in container 1': 757, 'in container 2': 330}
analyse container 0: {'DRONE A': 0, 'DRONE B': 2, 'DRONE C': 0, 'DRONE D': 0, 'DRONE E': 0, 'DRONE F': 0, 'DRONE G': 0, 'DRONE H': 2, 'MED 1': 910, 'MED 2': 0, 'MED 3': 595}
analyse container 1: {'DRONE A': 0, 'DRONE B': 4, 'DRONE C': 0, 'DRONE D': 0, 'DRONE E': 0, 'DRONE F': 2, 'DRONE G': 0, 'DRONE H': 2, 'MED 1': 618, 'MED 2': 267, 'MED 3': 757}
analyse container 2: {'DRONE A': 0, 'DRONE B': 2, 'DRONE C': 0, 'DRONE D': 0, 'DRONE E': 0, 'DRONE F': 4, 'DRONE G': 0, 'DRONE H': 2, 'MED 1': 822, 'MED 2': 221, 'MED 3': 330}


*******************************************************
* fill arbitrary meds, no redundant drones (309 days) *
*******************************************************

optimize finished, final utilization is {'container 0': 0.8746606076624744, 'container 1': 0.8551420442031307, 'container 2': 0.8817167645798778, 'mean': 0.8705064721484943}
analyse DRONE A: {'total': 0, 'in container 0': 0, 'in container 1': 0, 'in container 2': 0}
analyse DRONE B: {'total': 4, 'in container 0': 1, 'in container 1': 0, 'in container 2': 3}
analyse DRONE C: {'total': 0, 'in container 0': 0, 'in container 1': 0, 'in container 2': 0}
analyse DRONE D: {'total': 0, 'in container 0': 0, 'in container 1': 0, 'in container 2': 0}
analyse DRONE E: {'total': 0, 'in container 0': 0, 'in container 1': 0, 'in container 2': 0}
analyse DRONE F: {'total': 3, 'in container 0': 0, 'in container 1': 1, 'in container 2': 2}
analyse DRONE G: {'total': 0, 'in container 0': 0, 'in container 1': 0, 'in container 2': 0}
analyse DRONE H: {'total': 3, 'in container 0': 1, 'in container 1': 1, 'in container 2': 1}
analyse MED 1: {'total': 3031, 'in container 0': 1177, 'in container 1': 858, 'in container 2': 996}
analyse MED 2: {'total': 631, 'in container 0': 0, 'in container 1': 424, 'in container 2': 207}
analyse MED 3: {'total': 2015, 'in container 0': 427, 'in container 1': 1014, 'in container 2': 574}
analyse container 0: {'DRONE A': 0, 'DRONE B': 1, 'DRONE C': 0, 'DRONE D': 0, 'DRONE E': 0, 'DRONE F': 0, 'DRONE G': 0, 'DRONE H': 1, 'MED 1': 1177, 'MED 2': 0, 'MED 3': 427}
analyse container 1: {'DRONE A': 0, 'DRONE B': 0, 'DRONE C': 0, 'DRONE D': 0, 'DRONE E': 0, 'DRONE F': 1, 'DRONE G': 0, 'DRONE H': 1, 'MED 1': 858, 'MED 2': 424, 'MED 3': 1014}
analyse container 2: {'DRONE A': 0, 'DRONE B': 3, 'DRONE C': 0, 'DRONE D': 0, 'DRONE E': 0, 'DRONE F': 2, 'DRONE G': 0, 'DRONE H': 1, 'MED 1': 996, 'MED 2': 207, 'MED 3': 574}


******************************************************************
* fill arbitrary meds and drones, no redundant drones (309 days) *
******************************************************************
optimize finished, final utilization is {'container 0': 0.9106772428927906, 'container 1': 0.8551420442031307, 'container 2': 0.8817167645798778, 'mean': 0.8825120172252663}
analyse DRONE A: {'total': 0, 'in container 0': 0, 'in container 1': 0, 'in container 2': 0}
analyse DRONE B: {'total': 24, 'in container 0': 21, 'in container 1': 0, 'in container 2': 3}
analyse DRONE C: {'total': 0, 'in container 0': 0, 'in container 1': 0, 'in container 2': 0}
analyse DRONE D: {'total': 0, 'in container 0': 0, 'in container 1': 0, 'in container 2': 0}
analyse DRONE E: {'total': 0, 'in container 0': 0, 'in container 1': 0, 'in container 2': 0}
analyse DRONE F: {'total': 5, 'in container 0': 2, 'in container 1': 1, 'in container 2': 2}
analyse DRONE G: {'total': 4, 'in container 0': 4, 'in container 1': 0, 'in container 2': 0}
analyse DRONE H: {'total': 5, 'in container 0': 3, 'in container 1': 1, 'in container 2': 1}
analyse MED 1: {'total': 2350, 'in container 0': 496, 'in container 1': 858, 'in container 2': 996}
analyse MED 2: {'total': 631, 'in container 0': 0, 'in container 1': 424, 'in container 2': 207}
analyse MED 3: {'total': 1799, 'in container 0': 211, 'in container 1': 1014, 'in container 2': 574}
analyse container 0: {'DRONE A': 0, 'DRONE B': 21, 'DRONE C': 0, 'DRONE D': 0, 'DRONE E': 0, 'DRONE F': 2, 'DRONE G': 4, 'DRONE H': 3, 'MED 1': 496, 'MED 2': 0, 'MED 3': 211}
analyse container 1: {'DRONE A': 0, 'DRONE B': 0, 'DRONE C': 0, 'DRONE D': 0, 'DRONE E': 0, 'DRONE F': 1, 'DRONE G': 0, 'DRONE H': 1, 'MED 1': 858, 'MED 2': 424, 'MED 3': 1014}
analyse container 2: {'DRONE A': 0, 'DRONE B': 3, 'DRONE C': 0, 'DRONE D': 0, 'DRONE E': 0, 'DRONE F': 2, 'DRONE G': 0, 'DRONE H': 1, 'MED 1': 996, 'MED 2': 207, 'MED 3': 574}
"""
