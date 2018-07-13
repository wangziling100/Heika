import re
import os
import pandas as pd
import logging
from datetime import timedelta
from shutil import copyfile, copytree, rmtree


def merge_csv(dir, names=[], logger=None):
    # init 
    exc_content = {}
    is_part = False
    b_get_csv = False
    df = pd.DataFrame()

    for name in names:
        if dir[-1] != '/':
            dir = dir + '/'

        fn = dir+name
        with open(fn, 'r') as f:
            for line in f:
                # init
                b_get_csv = False

                if line.startswith('tag'):
                    p_day = '(^tag )(\d+)'
                    result = re.match(p_day, line)
                    day = result.groups()[1]
                    week = None
                    uid = None
                    start_time = None
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
                    start_time = result.groups()[1]

                elif line.startswith('e'):
                    p_exc = '(^e)(\d)(.)(.*)'
                    result = re.match(p_exc, line)
                    char = result.groups()[2]
                    num = result.groups()[1]
                    if char == ':':
                        content = result.groups()[3][1:]
                        exc_content[num] = content

                    elif char == ' ':
                        b_get_csv = True
                        exc_num = num
                        infos = result.groups()[3].split(' ')

                        if infos[1].startswith('part'):
                            is_part = True
                            exc_times = infos[0][1:]
                            part_num = infos[1][-2]
                            s_time = time_to_sec(infos[2])
                            e_time = time_to_sec(infos[4])

                        else:
                            is_part = False
                            exc_times = infos[0][1:-1]
                            s_time = time_to_sec(infos[1])
                            e_time = time_to_sec(infos[3])

                    if b_get_csv:
                        week_txt = week+'te_Woche/'
                        day_txt_dir = day+'_tag/'
                        user_txt = 'heika'+uid+'_'
                        day_txt = 'd'+day+'_'
                        exc_txt = 'e'+exc_num+'_'+exc_times
                        if is_part:
                            exc_txt += '_p'+part_num

                        csv_fn = dir+week_txt+day_txt_dir+user_txt+day_txt+exc_txt+'.csv'
                        if os.path.isfile(csv_fn):
                            logger.info(csv_fn)

                            curr_df = pd.read_csv(csv_fn)
                            curr_df['uid'] = int(uid)
                            curr_df['day'] = int(day)
                            curr_df['week'] = int(week)
                            curr_df['is_part'] = is_part
                            curr_df['exc_num'] = int(exc_num)
                            curr_df['exc_times'] = int(exc_times)

                            curr_df['time'] = curr_df.index
                            interval = 1.0*(e_time-s_time)/len(curr_df.index)
                            curr_df['time'] *= interval
                            curr_df['time'] += float(start_time)+s_time
                            print(interval)
                            
                            df = pd.concat([df, curr_df])
                        else:
                            msg = "the file dosen't exit:"
                            msg += msg+csv_fn
                            logger.info(msg)

    return df


def time_to_sec(time):
    tmp = time.split(':')
    mins = tmp[0]
    secs = tmp[1]
    return timedelta(minutes=int(mins), seconds=int(secs)).total_seconds()


def main():
    logger_name = 'merge_csv'
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

    names = ['tag 1']
    return merge_csv('../data', names, logger)


if __name__ == '__main__':
    main()
    
