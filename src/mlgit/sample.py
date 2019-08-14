"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import random
import re


class SampleValidateExcepetion(Exception):

    def __init__(self, msg):
        super().__init__(msg)


class GroupSample:

    def __init__(self, amount, group_size, seed):
        self.__amount = amount
        self.__group_size = group_size
        self.__seed = seed

    def get_amount(self):
        return self.__amount

    def get_group_size(self):
        return self.__group_size

    def get_seed(self):
        return self.__seed


class RangeSample:

    def __init__(self, start, stop, step):
        self.__start = start
        self.__stop = stop
        self.__step = step

    def get_start(self):
        return self.__start

    def get_stop(self):
        return self.__stop

    def get_step(self):
        return self.__step


class SampleValidate:

    @staticmethod
    def range_sample_validation(sample, files):
        start, stop, step = SampleValidate.input_validate_range(sample, files)
        if start is not None:
            if start < 0:
                raise SampleValidateExcepetion("The step parameter above or equal that of zero.")
            elif start >= stop:
                raise SampleValidateExcepetion("The start parameter must be smaller that of the stop.")
            elif stop < 0:
                raise SampleValidateExcepetion("The stop parameter above zero.")
            elif step < 0:
                raise SampleValidateExcepetion("The step parameter above zero.")
            elif step > stop:
                raise SampleValidateExcepetion("The stop parameter must be greater that of the step.")
            elif stop > len(files):
                raise SampleValidateExcepetion(
                    "The stop parameter must be smaller that of the file list.")
            elif step > len(files):
                raise SampleValidateExcepetion(
                    "The step parameter must be smaller that of the file list.")
        else:
            raise SampleValidateExcepetion(
                "The --range-sample=<start:stop:step> or  --range-sample=<start:stop>: requires integer values.The stop parameter can be all or -1 or any integer above zero")
        return RangeSample(start=start, stop=stop, step=step)

    @staticmethod
    def group_sample_validation(sample, seed, files):
        re_sample = re.search(r"^(\d+)\:(\d+)$", sample)
        re_seed = re.search(r"^(\d+)$", seed)
        if (re_sample and re_seed) is not None:
            amount = int(re_sample.group(1))
            group_size = int(re_sample.group(2))
            seed = int(re_seed.group(1))
            if group_size < 0:
                raise SampleValidateExcepetion("The group size parameter above zero.")
            elif amount >= group_size:
                raise SampleValidateExcepetion("The amount parameter must be greater than that of the group.")
            elif group_size > len(files):
                raise SampleValidateExcepetion(
                    "The group size parameter must be smaller than that of the file list.")
            elif amount > len(files):
                raise SampleValidateExcepetion(
                    "The amount must be smaller than that of the file list.")
        else:
            raise SampleValidateExcepetion(
                "The --group-sample=<amount:group-size> --seed=<seed>: requires integer values.")
        return GroupSample(amount=amount, group_size=group_size, seed=seed)

    @staticmethod
    def stop_validate(stop, files):
        if stop is 'all' or '-1':
            return len(files)
        else:
            return stop

    @staticmethod
    def range_sample(start, stop, files, step, set_files):

        for key in range(start, stop, step):
            list_file = list(files)
            set_files.update({list_file[key]: files.get(list_file[key])})

    @staticmethod
    def group_sample(amount, group_size, files, parts, set_files, seed):
        random.seed(seed)
        div = group_size
        count = 0
        dis = group_size - parts
        if div <= len(files):
            while count < amount:
                for key in random.sample(range(dis, group_size - 1), amount):
                    list_file = list(files)
                    set_files.update({list_file[key]: files.get(list_file[key])})
                    count = count + 1
                div = div + parts
            SampleValidate.group_sample(amount, div, files, parts, set_files, seed)

    @staticmethod
    def is_samples(samples, files):
        set_files = {}
        try:
            if samples is not None:
                if 'group' in samples:
                    group = SampleValidate.group_sample_validation(samples['group'], samples['seed'], files)
                    if group:
                        SampleValidate.group_sample(group.get_amount(), group.get_group_size(), files, group.get_group_size(),
                                     set_files, group.get_seed())
                        return set_files
                    else:
                        return None
                elif 'range' in samples:
                    range_sample = SampleValidate.range_sample_validation(samples['range'], files)
                    if range_sample:
                        SampleValidate.range_sample(range_sample.get_start(), range_sample.get_stop(), files,
                                     range_sample.get_step(), set_files)
                        return set_files
                    else:
                        return None
        except Exception as e:
            raise e

    @staticmethod
    def input_validate_range(sample, files):
        if re.search(r"^(\d+)\:(all|-1|\d+)$", sample) is not None:
            range_regex = re.search("^(\d+)\:(all|-1|\d+)$", sample)
            return int(range_regex.group(1)), SampleValidate.stop_validate(range_regex.group(2), files), 1
        elif re.search(r"(\d+)\:(all|-1|\d+)\:(\d+)$", sample) is not None:
            range_regex = re.search(r"(\d+)\:(all|-1|\d+)\:(\d+)$", sample)
            return int(range_regex.group(1)), SampleValidate.stop_validate(range_regex.group(2), files), int(
                range_regex.group(3))
        else:
            return None, None, None
