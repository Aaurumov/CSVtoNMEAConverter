import os
import pandas as pd

# path to the directory where input files will be read
read_directory = './input_csv/'

# path to the directory where converted files will be created and stored
save_directory = './output_nmea/'


# Calculation of checksum value of the nmea sentence
def calculate_checksum(sentence):
    checksum = 0

    for char in sentence:
        if char == '$':
            continue

        if char == '*':
            break

        # Calculate checksum of each char in the nmea sentence
        checksum ^= ord(char)
    # Cast the output value to Hexadecimal format, which should consist of only 2 values, like 2F.
    checksum_str = hex(checksum)[2:].upper().zfill(2)

    return checksum_str


# Go through each file in read_directory
for filename in os.listdir(read_directory):

    # Open and read each file in read_directory
    data = pd.read_csv(f"{read_directory}/{filename}")

    # Create the same name for the output file, but with .nmea extension
    output_filename = os.path.splitext(filename)[0] + '.nmea'

    # Create and save new empty output file in save_directory
    output_file = os.path.join(save_directory, output_filename)

    try:
        # Open the newly created .nmea file to write the gps data there
        with open(output_file, "w") as file:
            # Go through values of each row in the csv document
            for raw in data.values:

                # Get the integer value of timestamp (seconds), which is in the first position
                time_value_before_dot = int(raw[0])
                # Get the float value of timestamp (milliseconds)
                time_value_after_dot = raw[0] % 1

                # Calculate the hours
                hh = int(time_value_before_dot / 3600)
                # Calculate the minutes
                mm = int((time_value_before_dot % 3600) / 60)
                # Calculate the seconds
                ss = int(time_value_before_dot % 60)
                # Get milliseconds to 2 decimal places (format 0.xx)
                ms = f"{time_value_after_dot:.2f}"

                """
                Compose the timestamp string for the coordinates string.
                
                Hours, minutes and second should have only 2 decimal places and
                from millisecond we need only decimal part (without 0.)
                """
                timestamp = f"{hh:02d}{mm:02d}{ss:02d}.{ms.split('.')[1]}"

                # Get the latitude value from the row, which is in second position
                lat = pd.to_numeric(raw[1])
                # Get the integer value of latitude, which represents the degree value
                lat_degrees = int(lat)
                # Calculate the latitude decimal minutes value
                lat_decimal_minutes = (lat - lat_degrees) * 60
                # Define the latitude hemisphere direction
                hemisphere_lat = "N" if lat >= 0 else "S"

                """
                 Compose the latitude string for the coordinates string.
                 
                 Latitude degrees should have only 2 numbers and
                 if the number is less than 10, at the start should be 0, like 02.
                 
                 Latitude decimal minutes should have 4 decimal places, like 0.1245.
                """
                lat = f"{lat_degrees:02d}{lat_decimal_minutes:.4f}"

                # Get the longitude value from the row, which is located at third place
                lon = pd.to_numeric(raw[2])
                # Get the integer value of longitude, which represents the longitude degrees value
                lon_degrees = int(lon)
                # Calculate longitude decimal minutes value
                lon_decimal_minutes = (lon - lon_degrees) * 60
                # Define the longitude hemisphere direction
                hemisphere_lon = "E" if lon >= 0 else "W"

                """
                 Compose the longitude string for coordinate string.
                 
                 Longitude degrees should have only 3 numbers and
                 if the number is less than 100, at the start should be 0, like 002 or 023.
                 
                 Longitude decimal minutes should have 4 decimal places, like 0.1245.
                """
                lon = f"{lon_degrees:03d}{lon_decimal_minutes:.4f}"

                """
                 Compose the gps coordinates, which consists of:
                 - $GPGGA: This is the start of the sentence and serves as a header to indicate
                 that it contains GPS fix data.
                 - timestamp: Represents the timestamp of the coordinate in format of: HHMMSS.ms.
                 - lat: Latitude in degrees and decimal minutes.
                 - hemisphere_lat: Hemisphere indicator for latitude.
                 - lon: Longitude in degrees and decimal minutes.
                 - hemisphere_lon: Hemisphere indicator for longitude.
                 - 7-th element: GPS fix quality indicator. "0" = No fix, "1" = GPS fix (a valid fix).
                 - 8-th element: Number of satellites being tracked.
                 - 9-th element: Horizontal dilution of precision (HDOP).
                 - 10-th element: Altitude above sea level.
                 - 11-th element: Unit of measurement for altitude, in this case, meters.
                 - 12-th element: Height of geoid (undulation) above the WGS84 ellipsoid.
                 - 13-th element: Unit of measurement for the geoid height, in this case, meters.
                 - 14-th element: Age of differential GPS data (if available).
                 - 15-th element: Reference station ID (if available).
                 - 16-th element: This is a hexadecimal value calculated based on the previous characters in the
                 sentence and is used for error checking and data integrity.
                 
                 In our case we have only timestamp, latitude and longitude, that is why we can not define or calculate
                 values after 5-th element. These values are not important to create the .nmea file and check on some
                 map service, that can work with .nmea format. The last element can be calculated.
                """
                line = f"$GPGGA,{timestamp},{lat},{hemisphere_lat},{lon},{hemisphere_lon},0,1,999.9,0,M,0.0,M,,, "
                # Calculate the 16-th element value.
                checksum_value = calculate_checksum(line)
                # Composing of the final GPS coordinate string using data we could calculate.
                nmea_sentence = f"{line}*{checksum_value}"

                # Write the final coordinate line into the .nmea document.
                file.write(nmea_sentence + "\n")
        # After all lines will be writen to the file, close the file
        file.close()

    # If an error occurs, print it.
    except IOError as e:
        print(f"Error: {e}")
