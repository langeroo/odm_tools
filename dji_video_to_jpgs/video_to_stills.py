#!/bin/python3

# @Author:	github.com/langeroo

# This translator converts video from a DJI Mavic Pro Platinum into a collection of JPGs
# Necessary files:
#		- DJI_VIDEO_0123.MOV
#		- DJI_VIDEO_0123.SRT
# To Run:
#		- First, make sure you have ffmpeg installed
#		- Create virtual environment, activate virtual environment, install requirements.txt
#		- python3 video_to_stills.py /path/to/DJI_VIDEO_0123.MOV
# Output:
#		- Folder of JPGs with geotags encoded as EXIF data
# Note:
#		- To run properly, your SRT file must be in the same directory as your MOV files
# 		- In order to record the SRT file, you must activate video captions in the DJI Go App
# 		- This formatting has only been tested for files coming out of a DJI Mavic Pro Platinum.
#		- I make no guarantees that the video caption data is in the same format for other UAVs or software verions
#		- Example SRT Data format:
# 			1
# 			00:00:01,000 --> 00:00:02,000
# 			HOME(-1.2345,6.7891) 2021.01.21 12:34:56
# 			GPS(-11.2233,44.5566,20) BAROMETER:110.0
# 			ISO:200 Shutter:30 EV:-1/3 Fnum:2.2 

import exif
import ffmpeg
import sys
import os

# check arguments
if len(sys.argv) < 2:
	print("Usage: " + sys.argv[0] + " /path/to/DJI_VIDEO.MOV" );
	quit();

# get filenames
file_mov = sys.argv[1];
file_srt = os.path.splitext(file_mov)[0] + '.SRT';
folder = os.path.split(file_mov)[0];
output_subdir = "images"
output_path = os.path.join(folder, output_subdir)

# make output directory
if not os.path.exists(output_path):
    os.makedirs(output_path)

# check for video (MOV)
if not os.path.isfile(file_mov):
	print("Cannot find video (MOV) file:");
	print("\t" + file_mov);
	quit();

# check for subtitle (SRT)
if not os.path.isfile(file_srt):
	print("Cannot find subtitle file:");
	print("\t" + file_srt);
	print("Please ensure that your .SRT file is in the same directory as your .MOV file and has the same base name.");
	quit();

# get all data from SRT file
srt_lines = None;
with open(file_srt) as f: 
    srt_lines = f.readlines();
    if len(srt_lines) < 5:
    	print("SRT file missing data.");
    	quit();

num_lines = len(srt_lines);
num_lines_per_entry = 6;
num_entries = num_lines / num_lines_per_entry;

# simple test 6 entries per line
if not num_entries == int(num_entries):
	print("SRT file has missing or unexpected lines")
	quit();

idx_idx = 0;
idx_vid_time = 1;
idx_home_date_time = 2;
idx_pos = 3;
idx_cam = 4;
idx_blank = 5;

exif_entries = [];
for i in range(int(num_entries)):
	step = num_lines_per_entry * i;

	vid_time = srt_lines[step + idx_vid_time].strip();
	home_date_time = srt_lines[step + idx_home_date_time].strip();
	pos = srt_lines[step + idx_pos].strip();
	cam = srt_lines[step + idx_cam].strip();

	video_time 		= vid_time.split()[0];
	img_date_time 	= " ".join(home_date_time.split()[1:3]);
	gps_string 		= pos.split()[0][4:-1];
	bar_string 		= pos.split()[1].split(":")[1];
	iso_string 		= cam.split()[0]
	shutter_string 	= cam.split()[1]
	ev_string 		= cam.split()[2]
	fnum_string 	= cam.split()[3]

	# time
	exif_date_time 	= ":".join(img_date_time.split("."))

	# position
	elem_gps = gps_string.split(",")
	exif_GPSLongitude_dec= elem_gps[0];
	exif_GPSLongitudeRef= "E";
	exif_GPSLatitude_dec= elem_gps[1];
	exif_GPSLatitudeRef	= "N";
	exif_GPSAltitude 	= bar_string;
	exif_GPSAltitudeRef = 0;
	if exif_GPSLongitude_dec[0] == "-":
		exif_GPSLongitude_dec = exif_GPSLongitude_dec[1:];
		exif_GPSLongitudeRef = "W";
	if exif_GPSLatitude_dec[0] == "-":
		exif_GPSLatitude_dec = exif_GPSLatitude_dec[1:];
		exif_GPSLatitudeRef = "S";

	# decimal degrees to Deg, Min, Sec
	longitude_deg_int = int(float(exif_GPSLongitude_dec));
	longitude_min = 60.0 * (float(exif_GPSLongitude_dec) - longitude_deg_int);
	longitude_min_int = int(longitude_min);
	longitude_sec = 60.0 * (longitude_min - longitude_min_int);
	exif_GPSLongitude = (longitude_deg_int, longitude_min_int, longitude_sec);
	latitude_deg_int = int(float(exif_GPSLatitude_dec));
	latitude_min = 60.0 * (float(exif_GPSLatitude_dec) - latitude_deg_int);
	latitude_min_int = int(latitude_min);
	latitude_sec = 60.0 * (latitude_min - latitude_min_int);
	exif_GPSLatitude = (latitude_deg_int, latitude_min_int, latitude_sec);
	exif_entries.append([exif_date_time, 
						exif_GPSLatitude, exif_GPSLatitudeRef, 
						exif_GPSLongitude, exif_GPSLongitudeRef, 
						exif_GPSAltitude, exif_GPSAltitudeRef]);

# run ffmpeg for .mov -> .jpg at 1fps
output_image_string = output_path + "/%05d.jpg";
try:
    (ffmpeg.input(file_mov)
          .filter('fps', fps=1)
          .output(output_image_string, 
                  video_bitrate='5000k',
                  sws_flags='bilinear',
                  start_number=0)
          .run(capture_stdout=True, capture_stderr=True))
except ffmpeg.Error as e:
    print('stdout:', e.stdout.decode('utf8'))
    print('stderr:', e.stderr.decode('utf8'))

# list all jpgs created by ffmpeg
all_imgs = [os.path.join(output_path, f) for f in os.listdir(output_path) if os.path.isfile(os.path.join(output_path, f))];
i = 0;

# shove position data from SRT into jpg EXIF data
for curr_img in all_imgs:
	
	my_image = None;
	# access exif for an image, set variables as found in SRT
	with open(curr_img, 'rb') as image_file:
		my_image = exif.Image(image_file)
		my_image.datetime 			= exif_entries[i][0];
		my_image.gps_latitude 		= exif_entries[i][1];
		my_image.gps_latitude_ref 	= exif_entries[i][2];
		my_image.gps_longitude 		= exif_entries[i][3];
		my_image.gps_longitude_ref 	= exif_entries[i][4];
		my_image.gps_altitude 		= exif_entries[i][5];
		my_image.gps_altitude_ref 	= exif_entries[i][6];

		print(my_image.gps_latitude)
		print(my_image.gps_latitude_ref)
		print(my_image.gps_longitude)
		print(my_image.gps_longitude_ref)


	# write the above changes to each jpg
	with open(curr_img, 'wb') as new_image_file:
		new_image_file.write(my_image.get_file())

	i += 1;
