import sys
import os
import rosbag
import time
import tf
import rospy
import geometry_msgs.msg
import csv

def calc(filename, start=0, end=-1.0, end2=-1.0, start2=-1.0):
	with open(filename) as data_file:
		start_t = -1.0
		last_t = -1.0
		csv_entries = 0;

		lFF = geometry_msgs.msg.WrenchStamped()
		lDF = geometry_msgs.msg.WrenchStamped()
		lCS = geometry_msgs.msg.Twist()

		#bagg = rosbag.Bag(filename+'g', 'w')

		with open(filename[:-4]+".csv", 'wb') as csv_file:
			csv_writer = csv.writer(csv_file)
			csv_writer.writerow(['time','Force Input', 'Fx', 'Fy', 'Fz', 'Mx', 'My', 'Mz', 'Disturbance Force', 'Fx', 'Fy', 'Fz', 'Mx', 'My', 'Mz' , 'Velocity', 'Lx', 'Ly', 'Lz', 
				'Ax', 'Ay', 'Az' , 'Distance', 'front', 'left', 'right'])

			try:	
				for top, msg, tt in rosbag.Bag(data_file).read_messages():
					t = tt.to_sec()
					if (start_t == -1.0):
						start_t = t

					if (t - start_t) < start:
						continue 
					if ((t - start_t) >= end2) and ((t - start_t) < start2):
						continue
					if end > 0.0 and (t - start_t) >= end:
						break 
					#bagg.write(top,msg,tt)
					#continue

					if t < last_t:
						print "ERROR WITH TIMING"
						return

					if (top == '/fts/force_filtered') :
						lFF = msg

					if (top == '/heika/disturbance_force') :
						lDF = msg

					if (top == '/base_controller/command_safe') :
						lCS = msg

					if (top == '/heika_path_deviation/checkpoint_info_topic') :
						dist_front = msg.data[msg.data.find('front')+6:msg.data.find('\n')]
						dist_left = msg.data[msg.data.find('left')+5:msg.data.find('\n',msg.data.find('left'))]
						dist_right = msg.data[msg.data.find('right')+6:]
						
						csv_writer.writerow([t, '', lFF.wrench.force.x, lFF.wrench.force.y, lFF.wrench.force.z, lFF.wrench.torque.x, lFF.wrench.torque.y, lFF.wrench.torque.z, '', 
						lDF.wrench.force.x, lDF.wrench.force.y, lDF.wrench.force.z, lDF.wrench.torque.x, lDF.wrench.torque.y, lDF.wrench.torque.z, '',
						lCS.linear.x, lCS.linear.y, lCS.linear.z, lCS.angular.x, lCS.angular.y, lCS.angular.z, '', 
						dist_front, dist_left, dist_right])

						last_t = t
						csv_entries += 1
			except:
				print "ERROR"

	print filename[filename.rfind("/")+1:] + ": " + str(start) + " -- " + str(last_t - start_t) + " -- " + str(end) + " | " + str(csv_entries)
	#bagg.close()
