import RPi.GPIO as gpio
import time
from pynput.mouse import Listener, Button
import threading

# Constants for GPIO pin numbers
MOTOR_1A = 17  # Right side motor forward
MOTOR_1B = 27  # Right side motor reverse
MOTOR_2A = 23  # Left side motor forward
MOTOR_2B = 24  # Left side motor reverse

# PWM Frequency (Hz)
PWM_FREQUENCY = 100

# Sensitivity for turning (10% to 90% motor speed)
TURN_SENSITIVITY = 0.6
TURN_SENSITIVITY = 1 - TURN_SENSITIVITY

class CarController:
    def __init__(self):
        self.init_gpio()
        self.left_pressed = False  # Track left button pressed state
        self.right_pressed = False  # Track right button pressed state
        self.middle_pressed = False  # Track middle button pressed state
        self.last_wheel_event_time = time.time()  # Track time of the last wheel event
        self.spin_active = False  # To check if spin is active

    def init_gpio(self):
        """Initialize GPIO pins for motor control and set up PWM"""
        gpio.setmode(gpio.BCM)
        gpio.setup(MOTOR_1A, gpio.OUT)
        gpio.setup(MOTOR_1B, gpio.OUT)
        gpio.setup(MOTOR_2A, gpio.OUT)
        gpio.setup(MOTOR_2B, gpio.OUT)

        # Initialize PWM on motor pins with a specific frequency
        self.pwm_motor_1A = gpio.PWM(MOTOR_1A, PWM_FREQUENCY)
        self.pwm_motor_1B = gpio.PWM(MOTOR_1B, PWM_FREQUENCY)
        self.pwm_motor_2A = gpio.PWM(MOTOR_2A, PWM_FREQUENCY)
        self.pwm_motor_2B = gpio.PWM(MOTOR_2B, PWM_FREQUENCY)

        # Start PWM with 0 duty cycle (motors off)
        self.pwm_motor_1A.start(0)
        self.pwm_motor_1B.start(0)
        self.pwm_motor_2A.start(0)
        self.pwm_motor_2B.start(0)

    def apply_sensitivity(self, base_speed):
        """Apply the turn sensitivity to the base speed"""
        return base_speed * TURN_SENSITIVITY

    # Full speed forward-left (with sensitivity applied)
    def forward_left(self):
        """Turn forward left (right motor full speed, left motor reduced by sensitivity)"""
        right_speed = 100
        left_speed = self.apply_sensitivity(100)
        self.pwm_motor_1A.ChangeDutyCycle(right_speed)  # Right motor forward full speed
        self.pwm_motor_1B.ChangeDutyCycle(0)
        self.pwm_motor_2A.ChangeDutyCycle(left_speed)   # Left motor forward at reduced speed
        self.pwm_motor_2B.ChangeDutyCycle(0)

    # Full speed forward-right (with sensitivity applied)
    def forward_right(self):
        """Turn forward right (left motor full speed, right motor reduced by sensitivity)"""
        right_speed = self.apply_sensitivity(100)
        left_speed = 100
        self.pwm_motor_1A.ChangeDutyCycle(right_speed)  # Right motor forward at reduced speed
        self.pwm_motor_1B.ChangeDutyCycle(0)
        self.pwm_motor_2A.ChangeDutyCycle(left_speed)  # Left motor forward full speed
        self.pwm_motor_2B.ChangeDutyCycle(0)

    # Reverse at full speed
    def reverse(self):
        """Move both motors in reverse at full speed"""
        self.pwm_motor_1A.ChangeDutyCycle(0)
        self.pwm_motor_1B.ChangeDutyCycle(100)  # Right motor reverse full speed
        self.pwm_motor_2A.ChangeDutyCycle(0)
        self.pwm_motor_2B.ChangeDutyCycle(100)  # Left motor reverse full speed

    # Move forward at full speed
    def forward(self):
        """Move both motors forward at full speed"""
        self.pwm_motor_1A.ChangeDutyCycle(100)  # Right motor forward full speed
        self.pwm_motor_1B.ChangeDutyCycle(0)
        self.pwm_motor_2A.ChangeDutyCycle(100)  # Left motor forward full speed
        self.pwm_motor_2B.ChangeDutyCycle(0)

    # Spin clockwise at full speed (ignore sensitivity for spinning)
    def spin_clockwise(self):
        """Spin clockwise (right motors in reverse at full speed, left motors forward at full speed)"""
        if not self.spin_active:
            self.spin_active = True
            self.pwm_motor_1A.ChangeDutyCycle(0)  # Right motors reverse
            self.pwm_motor_1B.ChangeDutyCycle(100)  # Right motor full reverse
            self.pwm_motor_2A.ChangeDutyCycle(100)  # Left motor full forward
            self.pwm_motor_2B.ChangeDutyCycle(0)

        # Update the last wheel event time
        self.last_wheel_event_time = time.time()

    # Spin counterclockwise at full speed (ignore sensitivity for spinning)
    def spin_counterclockwise(self):
        """Spin counterclockwise (right motors forward at full speed, left motors reverse at full speed)"""
        if not self.spin_active:
            self.spin_active = True
            self.pwm_motor_1A.ChangeDutyCycle(100)  # Right motor full forward
            self.pwm_motor_1B.ChangeDutyCycle(0)
            self.pwm_motor_2A.ChangeDutyCycle(0)
            self.pwm_motor_2B.ChangeDutyCycle(100)  # Left motor full reverse

        # Update the last wheel event time
        self.last_wheel_event_time = time.time()

    def check_spin_timeout(self):
        """Stop spinning if no wheel event happened for 0.2 seconds"""
        while True:
            if self.spin_active and (time.time() - self.last_wheel_event_time >= 0.2):
                print("No recent wheel event, stopping spin.")
                self.spin_active = False
                self.stop()
            time.sleep(0.1)  # Check every 0.1 seconds

    # Stop all motors
    def stop(self):
        """Stop all motors"""
        if not self.middle_pressed:  # Only stop if the middle button is not pressed
            self.pwm_motor_1A.ChangeDutyCycle(0)
            self.pwm_motor_1B.ChangeDutyCycle(0)
            self.pwm_motor_2A.ChangeDutyCycle(0)
            self.pwm_motor_2B.ChangeDutyCycle(0)

    # Cleanup GPIO
    def cleanup(self):
        """Cleanup GPIO resources"""
        self.stop()
        self.pwm_motor_1A.stop()
        self.pwm_motor_1B.stop()
        self.pwm_motor_2A.stop()
        self.pwm_motor_2B.stop()
        gpio.cleanup()

    # Mouse click handler
    def on_click(self, x, y, button, pressed):
        if button == Button.left:
            self.left_pressed = pressed
        if button == Button.right:
            self.right_pressed = pressed
        if button == Button.middle:
            self.middle_pressed = pressed

        # Both buttons pressed = reverse
        if self.left_pressed and self.right_pressed:
            print("Both buttons pressed: Reverse")
            self.reverse()
        elif pressed:
            if button == Button.left:
                print("Left button pressed: Forward left")
                self.forward_left()
            elif button == Button.right:
                print("Right button pressed: Forward right")
                self.forward_right()
            elif button == Button.middle:
                print("Middle button pressed: Move forward")
                self.forward()
        else:
            # If any button is released, check if the middle button is still pressed
            if not self.middle_pressed:
                print("Button released: Stopping")
                self.stop()
            else:
                print("Middle button still pressed: Keep moving forward")
                self.forward()  # Keep moving forward if the middle button is pressed

    # Mouse scroll handler
    def on_scroll(self, x, y, dx, dy):
        if dy > 0:
            print("Scroll up: Spin clockwise")
            self.spin_clockwise()
        elif dy < 0:
            print("Scroll down: Spin counterclockwise")
            self.spin_counterclockwise()

    # Control the car with the mouse
    def control_with_mouse(self):
        # Start a thread to monitor spin timeouts
        spin_timeout_thread = threading.Thread(target=self.check_spin_timeout)
        spin_timeout_thread.daemon = True  # Make sure the thread stops when the main program exits
        spin_timeout_thread.start()

        # Use the Listener with grab=True to prevent OS from receiving mouse events
        with Listener(on_click=self.on_click, on_scroll=self.on_scroll, grab=True) as listener:
            listener.join()

# Main execution
if __name__ == "__main__":
    car = CarController()
    try:
        car.control_with_mouse()
    except KeyboardInterrupt:
        car.cleanup()
