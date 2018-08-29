import rosbag 
import pickle
import os

def topic_filter(dirs, topics, dest_dir):
    miss = []
    for dir in dirs:
        filenames = os.listdir(dir)
        for filename in filenames:
            try:
                processed_bags = pickle.load(open('../data/processed_bags.p', 'rb'))
            except FileNotFoundError:
                processed_bags = []

            if filename in processed_bags:
                continue
            try:
                basename = os.path.splitext(filename)[0]
                dest_path = os.path.join(dest_dir, basename+'_leg_source.bag')
                new_bag = rosbag.Bag(dest_path, w)
                source_path = os.path.join(dir, filename)

                for topic, msg, tt in rosbag.Bag(source_path).read_messages(topics=topics):
                    new_bag.write(topic, msg, tt)
                processed_bags.append(source_path)    
                pickle.dump(processed_bags, open('../data/processed_bags.p', 'wb'))
            except:
                miss.append(source_path)
                pickle.dump(miss, open('../data/miss_bags.p', 'wb'))

if __name__ == '__main__':
    dirs = []
    dest_dirs = []
    weeks = ['1te_Woche', '2te_Woche', '3te_Woche']
    days = ['1_tag', '2_tag', '3_tag', '4_tag', '5_tag']
    base_dir = '/media/uvebl/HEiKA-Lager'
    dest_dir = '../data/leg_position_source'
    for week in weeks:
        for day in days:
            dir = os.path.join(base_dir, week, day)
            dest_dir = os.path.join(dest_dir, week, day)
            dirs.append(dir)
            dest_dirs.append(dest_dir)


    topics = ['/tf', '/scan_rear', '/scan_rear_raw']
    for s,d in zip(dirs, dest_dirs):
        topic_filter(s, topics, d)
