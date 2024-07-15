import serial
import time

# Set the serial port and baud rate
serial_port = "COM5"  # Replace with your Arduino's serial port
baud_rate = 115200

# Create a serial connection
ser = serial.Serial(serial_port, baud_rate, timeout=1)

def send_data(data):
    # Append a newline character and encode data as bytes
    encoded_data = (str(data) + '\n').encode('utf-8')

    # Print the data being sent for debugging
    print("Sent Data:", data)

    # Send the data
    ser.write(encoded_data)

    # Read and print the response from the Arduino as bytes
    response = ser.readline().decode('ISO-8859-1').strip()
    print("Received Data:", response)

# Example usage

for i in range(5):

    user_input = "1 1 1 1 0.0 1 1 1 1 0.0"  #ms1 ms2 ms3 dir step
        
    # Replace commas with dots for decimal separator consistency
    user_input = user_input.replace(',', '.')
    
    # Send the input to the Arduino and read the response
    send_data(user_input)
    
    # Close the serial connection
    #ser.close()
