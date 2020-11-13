import time
import threading
from random import randint, randrange
import sys

'''
定义两个类: 一个发送者Sender, 一个接收者receiver
发送者: 发送窗口，窗口大小 = 用户输入，定时器，窗口的起始位置和结束位置，
接收者: 接收窗口
'''


class Sender():
	frame_numbering: int
	frame_num: int  # 帧的总数
	remaining_frame: int
	window_size: int
	timer: float
	front_id = 0
	end_id = 0
	receiver = None
	time_set: int  # 设定超时重传时间
	out_time_flag = False  # 超时标志
	lost_package_pos = int  # 丢包概率
	data_list = []

	def __init__(self, frame_numbering, window_size: int, time_set: int, lost_package_pos: int):
		'''
		初始化 几个一循环 窗口大小，时间设置，丢包概率
		'''
		self.frame_numbering = frame_numbering
		self.window_size = window_size
		self.time_set = time_set
		self.lost_package_pos = lost_package_pos
		self.end_id += self.window_size

	def flow_control(self):
		'''控制本次发送的最大数据量'''
		flow_max = int(input('请输入本次发送的最大数据量: '))
		if flow_max <= self.frame_num:
			self.frame_num = flow_max
			self.remaining_frame = self.frame_num
		else:
			print('最大数据流量已超过帧数，程序准备全部发送！')

	def slide_window(self, ack_id):  # 滑动自己的窗口
		while self.front_id % self.frame_numbering != ack_id:
			if self.end_id < self.frame_num:
				self.front_id += 1
				self.end_id += 1
			if self.end_id == self.frame_num:
				if self.front_id < self.end_id:
					if self.front_id % self.frame_numbering != ack_id:
						self.front_id += 1
				if self.front_id == self.end_id:
					print('帧已经全部传输完成！')
					break
		self.remaining_frame = self.frame_num - self.front_id

	def make_frame(self):  # 成帧
		print('请输入数据进行组装，每次输入结束后请按回车键，终止请输入esc退出')
		cnt = 0
		data = input(f'请进行输入第{cnt}次输入: ')
		while data != 'esc':
			self.data_list.append(data)
			cnt += 1
			data = input(f'请进行输入第{cnt}次输入: ')
		print('已经组装成帧！')
		self.frame_num = len(self.data_list)
		self.remaining_frame = self.frame_num

	def del_frame(self, del_index):  # 删除帧
		try:
			del self.data_list[del_index]
		except IndexError:
			print('帧不存在！')
		else:
			if self.frame_num > 0:
				self.frame_num -= 1
				self.remaining_frame = self.frame_num
			else:
				print('帧已经为空，不能再删除了')
				sys.exit()

	def sender_check(self):  # 发送检查
		if self.window_size < self.frame_numbering and self.window_size <= self.frame_num:
			print(f'检查完毕！窗口长度{self.window_size}与编号个数{self.frame_numbering}和帧长度{self.frame_num}的关系满足条件! ')
		else:
			print('窗口长度错误 ！')

	def send_frame(self, frame_id):  # 发送帧
		'''
		在发送时候启动一个定时器，如果发送成功，应该是接收者的接收窗口移动一个
		将窗口内的帧全部发送出去
		'''
		print(f'[发送窗口]: 正在发送{frame_id % self.frame_numbering}号帧')
		if randint(1, 100) > self.lost_package_pos:
			print(f'[发送窗口]: {frame_id % self.frame_numbering}号帧发送成功！')
			self.receiver.receive_frame(frame_id)
			self.receiver.send_ack(self.receiver.window_id % self.frame_numbering)
		else:  # 发送失败先更改重传标志
			self.out_time_flag = True

	def gbn_send(self):
		if self.out_time_flag:
			time.sleep(self.time_set)
			print('[发送窗口]: 现在开始重发啦! ')
		threads = []
		for frame_id in range(self.front_id, self.end_id):
			t = threading.Thread(target=self.send_frame, args=(frame_id,))
			threads.append(t)
			t.start()
		for t in threads:
			t.join()

	def receive_ack(self, ack_id):  # ack_id 接收者下一个希望接受的帧
		print(f'[发送窗口]: {ack_id}号ACK接收成功！')
		self.out_time_flag = False
		self.slide_window(ack_id)
		return True


class Receiver():  # 接收者
	block_size: int  # 每个分组的长度
	lost_package_pos: int  # 丢包概率
	window_id = 0
	sender: Sender = None
	r_data_list = []

	def __init__(self, sender: Sender):
		self.lost_package_pos = sender.lost_package_pos
		self.block_size = sender.frame_numbering

	def slide_window(self):  # 滑动窗口
		self.window_id = (self.window_id + 1)

	def receive_frame(self, frame_id):  # 接收帧
		if frame_id == self.window_id:
			print(f'[接收窗口]: {frame_id % self.block_size}号帧接收成功！')
			if frame_id < len(self.sender.data_list):
				self.r_data_list.append(self.sender.data_list[frame_id])
			self.slide_window()
		else:
			print(f'[接收窗口]: 现在希望接收{self.window_id % self.block_size}号帧！')
			self.send_ack((self.window_id % self.block_size))

	def send_ack(self, ack_id):  # 发送ack
		if randint(1, 100) > self.lost_package_pos:  # 如果传输成功, 发送者的窗口应该会移动
			self.sender.receive_ack(ack_id)
			return True
		else:
			self.sender.out_time_flag = True
			print(f'[接收窗口]: {ack_id}号ACK传输失败！')
