"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import random
import re


class SampleValidateException(Exception):

    def __init__(self, msg):
        super().__init__(msg)


class GroupSample(object):

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


class RangeSample(object):

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


class RandomSample(object):
    def __init__(self, amount, frequency, seed):
        self.__amount = amount
        self.__frequency = frequency
        self.__seed = seed

    def get_amount(self):
        return self.__amount

    def get_frequency(self):
        return self.__frequency

    def get_seed(self):
        return self.__seed


class SampleValidate:

    @staticmethod
    def __range_sample_validation(sample, files_size):
        start, stop, step = SampleValidate.__input_validate_range(sample, files_size)
        if start is not None:
            if files_size is None or files_size == 0:
                raise SampleValidateException(
                    'The file list is empty.')
            elif start < 0:
                raise SampleValidateException('The start parameter should be greater than or equal to zero.')
            elif start >= stop:
                raise SampleValidateException('The start parameter should be smaller than the stop.')
            elif step >= stop:
                raise SampleValidateException('The step parameter should be smaller than the stop.')
            elif stop > files_size:
                raise SampleValidateException(
                    'The stop parameter should be smaller than or equal to the file list size.')
        else:
            raise SampleValidateException(
                'The --range-sample=<start:stop:step> or  --range-sample=<start:stop>:'
                ' requires positive integer values. The stop parameter can be \'all\', \'-1\' or any integer greater than zero')
        return RangeSample(start=start, stop=stop, step=step)

    @staticmethod
    def __group_sample_validation(sample, seed, files_size):
        re_sample = re.search(r'^(\d+)\:(\d+)$', sample)
        re_seed = re.search(r'^(\d+)$', seed)
        if (re_sample and re_seed) is not None:
            amount = int(re_sample.group(1))
            group_size = int(re_sample.group(2))
            seed = int(re_seed.group(1))
            if amount == 0:
                raise SampleValidateException('The amount parameter should be greater than zero.')
            elif group_size <= 0:
                raise SampleValidateException('The group size parameter should be greater than zero.')
            elif files_size is None or files_size == 0:
                raise SampleValidateException(
                    'The file list is empty.')
            elif amount >= group_size:
                raise SampleValidateException('The amount parameter should be smaller than the group size.')
            elif group_size >= files_size:
                raise SampleValidateException(
                    'The group size parameter should be smaller than the file list size.')
        else:
            raise SampleValidateException(
                'The --group-sample=<amount:group-size> --seed=<seed>: requires positive integer values.')
        return GroupSample(amount=amount, group_size=group_size, seed=seed)

    @staticmethod
    def __random_sample_validation(sample, seed, files_size):
        re_sample = re.search(r'^(\d+)\:(\d+)$', sample)
        re_seed = re.search(r'^(\d+)$', seed)
        if (re_sample and re_seed) is not None:
            amount = int(re_sample.group(1))
            frequency = int(re_sample.group(2))
            seed = int(re_seed.group(1))
            if frequency <= 0:
                raise SampleValidateException('The frequency  parameter should be greater than zero.')
            if files_size is None or files_size == 0:
                raise SampleValidateException(
                    'The file list is empty.')
            elif amount >= frequency:
                raise SampleValidateException('The amount parameter should be smaller than the frequency.')

            elif frequency >= files_size:
                raise SampleValidateException(
                    'The frequency  parameter should be smaller than the file list size.')
        else:
            raise SampleValidateException(
                'The --random-sample=<amount:frequency> --seed=<seed>: requires positive integer values.')
        return RandomSample(amount=amount, frequency=frequency, seed=seed)

    @staticmethod
    def __stop_validate(stop, files_size):
        if 'all' == stop or '-1' == stop:
            return files_size
        else:
            return int(stop)

    @staticmethod
    def __range_sample(start, stop, files, step):
        set_files = {}
        for key in range(start, stop, step):
            list_file = list(files)
            set_files.update({list_file[key]: files.get(list_file[key])})
        return set_files

    @staticmethod
    def __group_sample(amount, group_size, files, parts, seed):
        random.seed(seed)
        set_files = {}
        count = 0
        while count < round(len(files) / parts):
            start = group_size - parts
            for key in random.sample(range(start, group_size - 1), amount):
                list_file = list(files)
                set_files.update({list_file[key]: files.get(list_file[key])})
            count = count + 1
            group_size = group_size + parts
        return set_files

    @staticmethod
    def __random_sample(amount, frequency, files, seed):
        random.seed(seed)
        set_files = {}
        for key in random.sample(range(len(files)), round((amount*len(files)/frequency))):
            list_file = list(files)
            set_files.update({list_file[key]: files.get(list_file[key])})
        return set_files

    @staticmethod
    def process_samples(samples, files):
        if samples is not None:
            if 'group' in samples:
                group = SampleValidate.__group_sample_validation(samples['group'], samples['seed'], len(files))
                if group:
                    return SampleValidate.__group_sample(group.get_amount(), group.get_group_size(), files,
                                                         group.get_group_size(), group.get_seed())
                return None
            elif 'range' in samples:
                range_samp = SampleValidate.__range_sample_validation(samples['range'], len(files))
                if range_samp:
                    return SampleValidate.__range_sample(range_samp.get_start(), range_samp.get_stop(), files,
                                                         range_samp.get_step())
                return None
            elif 'random' in samples:
                random_samp = SampleValidate.__random_sample_validation(samples['random'], samples['seed'], len(files))
                if random_samp:
                    return SampleValidate.__random_sample(random_samp.get_amount(), random_samp.get_frequency(), files, random_samp.get_seed())
                return None
        else:
            raise SampleValidateException('The sample parameter cannot be None')

    @staticmethod
    def __input_validate_range(sample, files_size):
        if re.search(r'^(\d+)\:(all|-1|\d+)$', sample) is not None:
            range_regex = re.search(r'^(\d+)\:(all|-1|\d+)$', sample)
            return int(range_regex.group(1)), SampleValidate.__stop_validate(range_regex.group(2), files_size), 1
        elif re.search(r'^(\d+)\:(all|-1|\d+)\:(\d+)$', sample) is not None:
            range_regex = re.search(r'^(\d+)\:(all|-1|\d+)\:(\d+)$', sample)
            return int(range_regex.group(1)), SampleValidate.__stop_validate(range_regex.group(2), files_size), int(
                range_regex.group(3))
        else:
            return None, None, None
