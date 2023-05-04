import wx
import vlc
import time
import argparse

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("-v", "--input_video", required=True, help="video file")
	parser.add_argument("-s", "--input_srt", required=True, help="subtitle file")

	args = parser.parse_args()

	return args

class MyFrame(wx.Frame):
	def __init__(self, parent, title, video_file, srt_file):
		wx.Frame.__init__(self, parent, title=title)

		# Create a panel to hold the VLC player
		self.video_panel = wx.Panel(self)

		# Create a panel to hold the buttons and slider
		self.control_panel = wx.Panel(self)

		# Load button icons
		# from here https://www.flaticon.com/
		play_icon = wx.Bitmap("icons/play_icon.png", wx.BITMAP_TYPE_PNG).ConvertToImage().Rescale(32, 32)
		pause_icon = wx.Bitmap("icons/pause_icon.png", wx.BITMAP_TYPE_PNG).ConvertToImage().Rescale(32, 32)
		forward_icon = wx.Bitmap("icons/forward_icon.png", wx.BITMAP_TYPE_PNG).ConvertToImage().Rescale(32, 32)
		backward_icon = wx.Bitmap("icons/backward_icon.png", wx.BITMAP_TYPE_PNG).ConvertToImage().Rescale(32, 32)

		# Create buttons with resized icons for play, pause, forward, backward
		self.play_button = wx.BitmapButton(self.control_panel, bitmap=wx.Bitmap(play_icon))
		self.pause_button = wx.BitmapButton(self.control_panel, bitmap=wx.Bitmap(pause_icon))
		self.forward_button = wx.BitmapButton(self.control_panel, bitmap=wx.Bitmap(forward_icon))
		self.backward_button = wx.BitmapButton(self.control_panel, bitmap=wx.Bitmap(backward_icon))

		# Create a slider for the time bar and a label for elapsed time
		self.time_slider = wx.Slider(self.control_panel, minValue=0, maxValue=1000, size=(350, -1))
		self.time_label = wx.StaticText(self.control_panel, label='00:00')

		# Bind events for buttons and slider
		self.play_button.Bind(wx.EVT_BUTTON, self.on_play)
		self.pause_button.Bind(wx.EVT_BUTTON, self.on_pause)
		self.forward_button.Bind(wx.EVT_BUTTON, self.on_forward)
		self.backward_button.Bind(wx.EVT_BUTTON, self.on_backward)
		self.time_slider.Bind(wx.EVT_SLIDER, self.on_seek)

		# Create a VLC instance
		self.instance = vlc.Instance()

		# Create a VLC media player
		self.player = self.instance.media_player_new()

		# Set the media to play
		self.player.set_mrl(video_file)

		# Attach the player to the panel
		self.player.set_hwnd(self.video_panel.GetHandle())

		# Start playing the media
		self.player.play()

		self.player.video_set_subtitle_file(srt_file)

		# Wait for the video to start playing
		time.sleep(1.0)

		# Get the dimensions of the video
		video_size = self.player.video_get_size()

		self.player.video_set_key_input(False)
		self.player.video_set_mouse_input(False)

		# Set the size of the window to match the video size
		self.SetSize((video_size[0], video_size[1] + 100))

		# Create a box sizer for the controls
		control_sizer = wx.BoxSizer(wx.HORIZONTAL)
		control_sizer.Add(self.play_button)
		control_sizer.Add(self.pause_button)
		control_sizer.Add(self.forward_button)
		control_sizer.Add(self.backward_button)
		control_sizer.Add(self.time_slider, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)
		control_sizer.Add(self.time_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)

		self.control_panel.SetSizer(control_sizer)

		# Create a vertical sizer to position the video panel and the control panel
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		main_sizer.Add(self.video_panel, 1, wx.EXPAND)
		main_sizer.Add(self.control_panel, 0, wx.EXPAND | wx.ALL, 10)

		self.SetSizer(main_sizer)
		self.Layout()

		# Create a timer for updating the time bar and elapsed time
		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.update_time, self.timer)
		self.timer.Start(100)

	def on_play(self, event):
		self.player.play()

	def on_pause(self, event):
		self.player.pause()

	def on_forward(self, event):

		current_time = self.player.get_time()
		self.player.set_time(current_time + 5000)  # Jump 5 seconds forward

	def on_backward(self, event):
		current_time = self.player.get_time()
		self.player.set_time(current_time - 5000)  # Jump 5 seconds backward

	def update_time(self, event):
		current_time = self.player.get_time() / 1000
		length = self.player.get_length() / 1000

		if self.player.get_state() == vlc.State.Playing :

			# Check if the video has reached its end
			if int(current_time) >= int(length) and length > 0:
				self.time_slider.SetValue(int(length * 1000 / length))
				mins, sec = divmod(length, 60)
				self.time_label.SetLabel("{:02d}:{:02d}".format(int(mins), int(sec)))
				self.player.stop()

			else:
				self.time_slider.SetValue(int(current_time * 1000 / length))
				mins, sec = divmod(current_time, 60)
				self.time_label.SetLabel("{:02d}:{:02d}".format(int(mins), int(sec)))

	def on_seek(self, event):
		# Calculate the new time based on the slider value and video length
		new_time = self.time_slider.GetValue() * self.player.get_length() // 1000

		# Set the new time for the player
		self.player.set_time(new_time)

		# Start playing the video if it's not already playing
		if not self.player.is_playing():
			self.player.play()


if __name__ == "__main__":

	namespace = parse_args()

	video_file = namespace.input_video
	srt_file = namespace.input_srt


	app = wx.App(False)
	frame = MyFrame(None, "VLC with wxPython", video_file = video_file, srt_file = srt_file)
	frame.Show()
	app.MainLoop()

