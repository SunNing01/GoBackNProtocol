from gbn_protol.gbn_protocol import Sender, Receiver
import time


def main():
	while True:
		try:
			frame_numbering = 2 ** int(input('请输入编号位数:'))
			window_size = int(input('请输入发送窗口的大小: '))
			time_set = int(input('请输入超时时间: '))
			lost_package_pos = int(input('请输入0~100内的数字设定丢包的概率: '))
			if frame_numbering >= 2 and window_size > 0 and time_set > 0 and 0 <= lost_package_pos < 100:
				break
			else:
				print('请输入正确的数字 ！')
		except ValueError:
			print('输入错误, 请重新输入正确的数字 ！')
	sender = Sender(frame_numbering, window_size, time_set, lost_package_pos)
	sender.make_frame()  # 成帧
	# 删除帧
	del_index = int(input('请输入需要删除的帧的下标，输入9999表示结束程序！'))
	while del_index != 9999:
		sender.del_frame(del_index)
		del_index = int(input('请输入需要删除的帧的下标，输入9999表示结束程序！'))

	sender.flow_control()  # 流量控制
	sender.sender_check()  # 发送检查
	receiver = Receiver(sender)
	receiver.sender = sender
	sender.receiver = receiver
	while sender.remaining_frame > 0:  # 模拟发送过程
		sender.gbn_send()
		time.sleep(time_set)
	print(f'收到数据啦: {receiver.r_data_list}')
	print(f'本次共发送{sender.frame_num}个数据，共收到{len(receiver.r_data_list)}个数据')


if __name__ == '__main__':
	main()
