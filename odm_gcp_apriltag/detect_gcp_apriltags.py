import cv2
import numpy as np
import apriltag
from os import listdir
from os.path import isfile, join
import sys

#usage
if len(sys.argv) < 3:
	print("Usage: detect_gcp_apriltags.py path/to/image/folder path/to/gcp_locations.txt (output_file_name)")
	quit();

#get command line args
mypath = sys.argv[1];
gcp_locations = sys.argv[2];
output_file_name = "gcp_list.txt";
if len(sys.argv) > 3:
	output_file_name = sys.argv[3]

#todo: validate CLA

#read gcp locations
content = None;
with open(gcp_locations) as f:
	gcp_content = f.readlines();
gcp_content = [x.strip() for x in gcp_content]

#build gcp dict
gcps = {};
gcp_coords = {};
header = None;
for i in range(len(gcp_content)):
	line = gcp_content[i];

	#skip header
	if i == 0:
		header = line;
		continue;

	#skip comments
	if line[0] == "#":
		continue;

	elements = line.split();
	tag_name = elements[0];
	data = " ".join(elements[1:len(elements)])


	if tag_name in gcps.keys():
		print("Why do you have the " + tag_name + " tag location listed twice?");
		print("Please fix this! Exiting...");
		quit();

	gcps[tag_name] = [];
	gcp_coords[tag_name] = data;

# print(gcps)

#look for all tags. if we have coords for that target
#then add it to the dict->list for that target
#if it's an unknown, add to orphan tags
orphan_tags = [];
imagepaths = [join(mypath, f) for f in listdir(mypath) if isfile(join(mypath, f))]
imagepaths.sort();
for imagepath in imagepaths:
	print("")
	count = 0;
	print("Searching for tags in " + imagepath)

	image = cv2.imread(imagepath, cv2.IMREAD_GRAYSCALE)
	if image is None:
		print(imagepath, "isn't an image.")
		continue;

	# detector = apriltag(family)
	detector = apriltag.Detector()
	print("Running detector...")
	detections = detector.detect(image)
	print("Detected " + str(len(detections)) + " tags")


	if len(detections) > 0:
		for det in detections:
			count += 1;
			family = str(det.tag_family.decode('utf-8'));
			family_elements = family.split('h');
			family_string = '_'.join(family_elements);
			tag_name = family_string + "_" + str(det.tag_id).zfill(5);
			# print(tag_name, det.center)

			if tag_name in gcps.keys():
				gcps[tag_name].append((imagepath, det.center));
			else:
				orphan_tags.append(tag_name);
	if count == 0:
		print("\tFound no tags")
	if count == 1:
		print("\tFound 1 tag")
	if count > 1:
		print("\tFound", count, "tags");

print("")
if len(orphan_tags) > 0:
	print("Found", len(orphan_tags), "tags without location data.")
	print("Did you forget to enter in their positions?");
	for tag in orphan_tags:
		print("\t", tag);

print("\nTags with positions:")
lines_out = [];
lines_out.append(header);
for tag in gcps.keys():
	print(tag)
	if len(gcps[tag]) == 0:
		print("\tNot found in any of", len(imagepaths), "images");
		continue;
	for info in gcps[tag]:
		print("\t", info[0] + ":", info[1])
		line = str(gcp_coords[tag]) + " " + str(info[1][0]) + " " + str(info[1][1]) + " " + info[0]
		lines_out.append(line)

if len(lines_out) < 2:
	print("Didn't find any markers that were both in the coordinates and images")
	quit();

with open(output_file_name, 'w') as f:
    for item in lines_out:
        f.write("%s\n" % item)

