import cv2
import pyaudio
import wave
import threading
import time
import subprocess
import os,sys
import numpy as np
from PIL import ImageGrab
from mhmovie  import *
#from mhmovie.code import *
import winsound
########################
## JRF
## VideoRecorder and AudioRecorder are two classes based on openCV and pyaudio, respectively. 
## By using multithreading these two classes allow to record simultaneously video and audio.
## ffmpeg is used for muxing the two signals
## A timer loop is used to control the frame rate of the video recording. This timer as well as
## the final encoding rate can be adjusted according to camera capabilities
##

########################
## Usage:
## 
## numpy, PyAudio and Wave need to be installed
## install openCV, make sure the file cv2.pyd is located in the same folder as the other libraries
## install ffmpeg and make sure the ffmpeg .exe is in the working directory
##
## 
## start_AVrecording(filename) # function to start the recording
## stop_AVrecording(filename)  # "" ... to stop it
##
##
########################

class VideoRecorder():
	# Video class based on openCV 
	def __init__(self):
		self.open = True
		self.device_index = 0
		self.fps = 6               # fps should be the minimum constant rate at which the camera can
		self.fourcc = "MJPG"       # capture images (with no decrease in speed over time; testing is required)
		self.frameSize = (640,480) # video formats and sizes also depend and vary according to the camera used
		self.video_filename = "temp_video.avi"
		self.video_cap = cv2.VideoCapture(self.device_index)
		self.video_writer = cv2.VideoWriter_fourcc(*self.fourcc)
		self.video_out = cv2.VideoWriter(self.video_filename, self.video_writer, self.fps, self.frameSize)
		self.frame_counts = 1
		self.start_time = time.time()
	# Video starts being recorded 
	def record(self):
		#		counter = 1
		timer_start = time.time()
		timer_current = 0
		
		
		while(self.open==True):
			ret, video_frame = self.video_cap.read()
			if (ret==True):
				
					self.video_out.write(video_frame)
#					print str(counter) + " " + str(self.frame_counts) + " frames written " + str(timer_current)
					self.frame_counts += 1
#					counter += 1
#					timer_current = time.time() - timer_start
					time.sleep(0.16)
					
					# Uncomment the following three lines to make the video to be
					# displayed to screen while recording
					
#					gray = cv2.cvtColor(video_frame, cv2.COLOR_BGR2GRAY)
#					cv2.imshow('video_frame', gray)
#					cv2.waitKey(1)
			else:
				break
							
				# 0.16 delay -> 6 fps
				# 
				

	# Finishes the video recording therefore the thread too
	def stop(self):
		
		if self.open==True:
			
			self.open=False
			self.video_out.release()
			self.video_cap.release()
			cv2.destroyAllWindows()
			
		else: 
			pass


	# Launches the video recording function using a thread			
	def start(self):
		video_thread = threading.Thread(target=self.record)
		video_thread.start()

class ScreenRecorder():
	
	# Video from computer screen
	def __init__(self):
		self.open = True
		self.fname = 'temp_video.avi' 
		self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
		self.video_out = cv2.VideoWriter(self.fname,self.fourcc, 6.0, (1366,768	))
		self.start_time = time.time()
		self.frame_counts = 1
	
	def record(self):
		timer_start = time.time()
		timer_current = 0
		while(self.open==True):
			img = ImageGrab.grab()
			img_np = np.array(img)
			frame = cv2.cvtColor(img_np,cv2.COLOR_BGR2RGB)
			self.video_out.write(frame)
			self.frame_counts += 1
			time.sleep(0.16)
	# Finishes the video recording therefore the thread too
	def stop(self):
		if self.open==True:
			self.open=False
			self.video_out.release()
			cv2.destroyAllWindows()	
		else: 
			pass	
	# Launches the video recording function using a thread			
	def start(self):
		screen_thread = threading.Thread(target=self.record)
		screen_thread.start()


class AudioRecorder():
	# Audio class based on pyAudio and Wave
	def __init__(self):
		self.open = True
		self.rate = 44100
		self.frames_per_buffer = 1024
		self.channels = 2
		self.format = pyaudio.paInt16
		self.audio_filename = "temp_audio.wav"
		self.audio = pyaudio.PyAudio()
		self.stream = self.audio.open(format=self.format,channels=self.channels,rate=self.rate,input=True,frames_per_buffer = self.frames_per_buffer)
		self.audio_frames = []
	# Audio starts being recorded
	def record(self):
		self.stream.start_stream()
		while(self.open == True):
			data = self.stream.read(self.frames_per_buffer) 
			self.audio_frames.append(data)
			if self.open==False:
				break
	# Finishes the audio recording therefore the thread too    
	def stop(self):
		if self.open==True:
			self.open = False
			self.stream.stop_stream()
			self.stream.close()
			self.audio.terminate()
			waveFile = wave.open(self.audio_filename, 'wb')
			waveFile.setnchannels(self.channels)
			waveFile.setsampwidth(self.audio.get_sample_size(self.format))
			waveFile.setframerate(self.rate)
			waveFile.writeframes(b''.join(self.audio_frames))
			waveFile.close()
		pass
	# Launches the audio recording function using a thread
	def start(self):
		audio_thread = threading.Thread(target=self.record)
		audio_thread.start()

def beep():
	frequency = 2500  # Set Frequency To 2500 Hertz
	duration = 100  # Set Duration To 1000 ms == 1 second
	winsound.Beep(frequency, duration)

def start_AVrecording(p_mode):
	print('inside start_AVrecording with p_mode : {}'.format(p_mode))				
	global video_thread
	global audio_thread
	if p_mode == 'S':
		video_thread = ScreenRecorder()
	else:
		video_thread = VideoRecorder()
	audio_thread = AudioRecorder()
	audio_thread.start()
	video_thread.start()

def combine_audio(vidname, audname, outname):
	print('inside combine_audio {} ---  {} --- {}'.format(vidname, audname, outname))
	m = Movie(vidname)
	mu = Music(audname)
	#mu.Aconvert()#convert wav to mp3
	final = m+mu
	#final.save('C:\\Users\\MURENGAR\\eclipse-workspace\\Project1\\AVrecordeR-master\\output.mp4')
	final.save(outname)
	print('Completed')

def stop_AVrecording():
	print('inside stop av recording')	
	audio_thread.stop() 
	frame_counts = video_thread.frame_counts
	elapsed_time = time.time() - video_thread.start_time
	recorded_fps = frame_counts / elapsed_time
	print("total frames {} ".format(str(frame_counts)))
	print("elapsed time {}".format(str(elapsed_time)))
	print("recorded fps {} ".format(str(recorded_fps)))
	video_thread.stop() 

	# Makes sure the threads have finished
	while threading.active_count() > 1:
		time.sleep(1)

	out_dir_name = os.path.join(os.getcwd(),'OutputScreenRecording')
	len_no_files  = len(os.listdir(out_dir_name)) + 1 
	#filename = filename+'_{}.mp4'.format(len_no_files) 
	#	 Merging audio and video signal
	combine_audio('temp_video.avi','temp_audio.wav',os.path.join(out_dir_name,(str(len_no_files) + '.mp4')))
	
	print('Completed')


def clear_files():
	for files in os.listdir():
		if files.endswith('.wav') or files.endswith('.avi') or files.endswith('.mp3'):
			os.remove(files)

def write_exit_file(value):
	fp = open('ExitFile.txt','w')
	fp.write(value)
	fp.close()

def read_exit_file():
	try:
		fp = open('ExitFile.txt','r')
		line = fp.readline()
		fp.close()
		print('value in file is {}'.format(line[0]))
		return str(line[0])
	except:
		print('Err reading file will return 0 for safer side')
		return '0'

def execute(p_mode):
	write_exit_file('0')
	l_exit = 0 
	while True:
		beep()
		start_AVrecording(p_mode)
		while True:
			l_exitval = read_exit_file()
			if l_exitval == '1':
				print('Will stop Recording Now')
				write_exit_file('0')
				l_exit = 1 
				break
			'''else:
				print('sleep 20 secs')
				time.sleep(20)
				break'''
		stop_AVrecording()
		print('l_exit is {}'.format(l_exit))
		if l_exit > 0:
			break
		
	clear_files()
	print("Done")


def stop_recording():
	beep()
	write_exit_file('1')
	
	
if __name__== "__main__":
	print('Starting...')
	execute('S')
	time.sleep(10)
	stop_recording()
	print('Starting...')
	'''if sys.argv[1] == 'A':
		execute('S')
	elif sys.argv[1] == 'B':
		stop_recording()'''
	print("Done")



