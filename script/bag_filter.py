import re
import os
import logging
from os.path import splitext
from ntpath import basename
import subprocess


def bag_filter(dir, topics, target_dir, names=[], logger=None):
    # init 
    exc_content = {}
    is_part = False
    b_get_bag = False
    processed_bags = []

    for name in names:
        if dir[-1] != '/':
            dir = dir + '/'

        fn = dir+name
        with open(fn, 'r') as f:
            for line in f:
                # init
                b_get_bag = False

                if line.startswith('tag'):
                    p_day = '(^tag )(\d+)'
                    result = re.match(p_day, line)
                    day = result.groups()[1]
                    week = None
                    uid = None
                elif line.startswith('woche'):
                    p_week = '(^woche)(\d+)'
                    result = re.match(p_week, line)
                    week = result.groups()[1]

                elif line.startswith('HEiKA'):
                    p_uid = '(^HEiKA)(\d*)'
                    result = re.match(p_uid, line)
                    uid = result.groups()[1]

                elif line.startswith('start_time'):
                    p_start_time = '(^start_time: )(.*)'
                    result = re.match(p_start_time, line)

                elif line.startswith('e'):
                    p_exc = '(^e)(\d)(.)(.*)'
                    result = re.match(p_exc, line)
                    char = result.groups()[2]
                    num = result.groups()[1]
                    if char == ':':
                        content = result.groups()[3][1:]
                        exc_content[num] = content

                    elif char == ' ':
                        b_get_bag = True
                        exc_num = num
                        infos = result.groups()[3].split(' ')

                        if infos[1].startswith('part'):
                            is_part = True
                            exc_times = infos[0][1:]
                            part_num = infos[1][-2]

                        else:
                            is_part = False

                    if b_get_bag:
                        week_txt = week+'te_Woche/'
                        day_txt_dir = day+'_tag/'
                        user_txt = 'heika'+uid+'_'
                        day_txt = 'd'+day+'_'
                        exc_txt = 'e'+exc_num+'_'+exc_times
                        if is_part:
                            exc_txt += '_p'+part_num

                        bag_fn = dir+week_txt+day_txt_dir+"cut/"+user_txt+day_txt+exc_txt+'.bag'
                        if os.path.isfile(bag_fn):
                            target_file = basename(bag_fn)
                            target_file = splitext(target_file)[0]+'_leg_position_source.bag'
                            target_file = target_dir+target_file
                            cmd = 'rosbag filter '+bag_fn+' '+target_file
                            cmd = cmd + ' '+'"'
                            for topic in topics:
                                cmd = cmd + " topic=='"+topic+"' or"

                            cmd = cmd[:-3] + '"'
                            print(cmd)
                            subprocess.Popen(cmd.split, stdout=subprocess.PIPE)

                            logger.info(bag_fn)
                            break

                        else:
                            msg = "the file dosen't exit:"
                            msg += msg+bag_fn
                            logger.info(msg)


def main(dir, topics, target_dir, conf_files=None):
    logger_name = 'bag_filter'
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = os.path.join(dir_path, '..')
    dir_path = os.path.join(dir_path, 'data/log')
    logger_path = os.path.join(dir_path, logger_name+'.log')
    fh = logging.FileHandler(logger_path)
    fh.setLevel(logging.INFO)
    fmt = fmt = "%(asctime)-15s %(levelname)-6s %(filename)-10s %(lineno)d \
                            %(process)d %(message)-5s"
    datafmt = "%d %b %Y %H:%M:%S"
    formatter = logging.Formatter(fmt, datafmt)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    print(logger_path)
    if conf_files is None:
        conf_files = ['tag 1']
    bag_filter(dir, topics, target_dir, conf_files, logger)


if __name__ == '__main__':
    main()
