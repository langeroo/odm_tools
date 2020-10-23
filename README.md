# odm_tools
A collection of tools for improved Open Drone Map usage

## dji_video_to_jpgs
Inputs 
- DJI video files with captions
-- DJI_0123.MOV
-- DJI_0123.SRT
Output
- folder of JPGs with GPS tags in EXIF data

## odm_gcp_apriltag
Inputs
- A file with global locations of GCPs
- All images to be processed
Output
- A standard gcp_list.txt with GCP pixel locations automatically entered
