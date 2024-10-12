# BreakingIntoRobotics
Tutorial on how to setup simple and cheap chassis for people who want to focus on the algorithm side of things and not on hardware itself. The focus was made on simplicity

https://www.youtube.com/watch?v=a_QKCKZybW4

Amazon car (21$) https://amzn.to/3Y2h7Ej <br>
L298N ESC (10$) https://amzn.to/3Y2h7Ej <br>
5V to 12V converter (8$) https://amzn.to/4dDVYGo <br>

# MouseRC Car Raspberry Pi Setup

1. **Copy Source Code**  
   Place `car_control.py` from raspberry-pi folder of this repo in the Desktop folder of your Raspberry Pi.

2. **Create a Shell Script to Run the Python Script**  
   Open the terminal and follow these steps:

   ```bash
   cd Desktop
   nano start_car_control.sh
   ```

   Paste the following content inside `start_car_control.sh`:

   ```bash
   sudo /usr/bin/python3 /home/<your username>/Desktop/car_control.py >> /home/<your username>/Desktop/car_control_log.txt 2>&1
   ```

   Save the file, then make it executable:

   ```bash
   chmod +x start_car_control.sh
   ```

3. **Add to Autostart**  
The following way of adding the python script to autostart allows to see the console with the stdout which is more convinient than some cron job etc. <br> <br>
   Open the LXDE autostart file:

   ```bash
   nano /etc/xdg/lxsession/LXDE-pi/autostart
   ```

   Add the following line after `@pcmanfm --desktop --profile LXDE-pi`:

   ```bash
   @lxterminal -e sudo sh /home/<your username>/Desktop/start_car_control.sh
   ```

   Save the changes and respart the Pi