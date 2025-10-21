from machine import Pin, I2C
import time

# 1 CONFIGURATION SECTION
# I2C bus setup:
# Using I2C1 with SDA on GPIO14 and SCL on GPIO15. 
# This allows the Pico to communicate with the DS3231 RTC module.
i2c_bus = I2C(1, scl=Pin(15), sda=Pin(14))  

# The 7-bit I2C address of the DS3231 real-time clock chip.
RTC_DEVICE_ADDRESS = 0x68  

# The GPIO pin used for the user button to start and stop the game.
GAME_BUTTON_PIN = 13  

# Log file path in flash memory where elapsed times will be stored.
GAME_LOG_FILE = "time_log.txt"


# 2️ FUNCTION TO READ SECONDS FROM DS3231 RTC

def get_rtc_seconds():
    """
    Reads the current seconds value from the DS3231 RTC.
    Returns the seconds as a decimal integer (0-59).

    Steps:
    1. Read 1 byte from the seconds register (0x00) of the RTC.
    2. Mask out the clock halt bit using 0x7F.
    3. Convert BCD (binary-coded decimal) to decimal.
       - Upper nibble (bits 4-6) is tens of seconds.
       - Lower nibble (bits 0-3) is units of seconds.
    """
    raw_byte = i2c_bus.readfrom_mem(RTC_DEVICE_ADDRESS, 0x00, 1)[0]
    seconds_bcd = raw_byte & 0x7F  # Mask out the clock halt bit

    tens_place = (seconds_bcd >> 4) & 0x07  # Extract tens of seconds
    ones_place = seconds_bcd & 0x0F         # Extract units of seconds

    seconds_decimal = tens_place * 10 + ones_place
    return seconds_decimal
#3️SETUP THE BUTTON FOR GAME INTERACTION
#Configure the button pin as an input with an internal pull-down resistor.
# This ensures the pin reads 0 when the button is not pressed and 1 when pressed.
game_button = Pin(GAME_BUTTON_PIN, Pin.IN, Pin.PULL_DOWN)

# 4️ MAIN GAME LOOP
print("HEYYYYY! Press the button to start counting 15 seconds in your head.")

try:
    while True:
        # Wait for the first button press to start the timer
        while not game_button.value():
            # Keep checking the button state
            # Sleep is optional here but can be added for debounce
            time.sleep(0.01)
        print("Timer started! Press the button when you think 15 seconds have passed.")

        #Record starting time
        start_seconds_rtc = get_rtc_seconds()   # Read seconds from RTC
        start_system_ms = time.ticks_ms()       # Also record system milliseconds for accuracy
        # Wait for button release and next press
        while game_button.value():  # Wait until the button is released
            pass
        while not game_button.value():  # Wait for the user to press again
            pass
        #Record ending time
        end_seconds_rtc = get_rtc_seconds()    # Read seconds from RTC
        end_system_ms = time.ticks_ms()        # Record system milliseconds
        # Calculate elapsed time
      
        #Use system milliseconds difference to handle wrap-around and sub-second precision
        elapsed_time_seconds = time.ticks_diff(end_system_ms, start_system_ms) / 1000.0

        #Display the result
    
        print("You counted {:.2f} seconds!".format(elapsed_time_seconds))

        #Log the result to a file in append mode
       
        #Each new time is added at the end of the log file
        with open(GAME_LOG_FILE, "a") as log_file:
            log_file.write("{:.2f}\n".format(elapsed_time_seconds))

        # Prepare for the next round
        
        print("Press the button again to play another round...but you better get it right this time or I wipe out your OS(directly to macbook users) ")
        while game_button.value():  #Wait for button release
            pass
        time.sleep(0.5)  #delay to avoid accidental double press

#Handle game exit

except KeyboardInterrupt:
    print("Game ended. All results saved to '{}'.".format(GAME_LOG_FILE))
