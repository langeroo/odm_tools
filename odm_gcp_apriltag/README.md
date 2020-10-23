# odm_gcp_apriltag
When using AprilTags as Ground Control Points in Open Drone Map, this script will take supplied ground control point locations and fill in the pixel locations for autodetected tags.

# Usage
python3 detect_gcp_apriltags.py path/to/image/folder path/to/gcp_locations.txt (output_file_name)

# Input gcp_locations.txt file
The input location file was configured to be as minimally different from the standard gcp_list.txt as possible.
The header is an exact copy, and all data lines are formatted as:
	tagfamily_id geo_x geo_y geo_z

See example_gcp_data.txt
