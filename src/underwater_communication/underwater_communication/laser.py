import math

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class LaserCommunication(Node):

    def __init__(self):

        super().__init__('laser_communication')

        # ==========================================================
        # Parameters
        # ==========================================================

        self.declare_parameter(
            'distance',
            10.0
        )

        self.declare_parameter(
            'max_range',
            30.0
        )

        self.declare_parameter(
            'transmitted_power',
            1.0
        )

        self.declare_parameter(
            'absorption_coefficient',
            0.05
        )

        self.declare_parameter(
            'scattering_coefficient',
            0.05
        )

        self.declare_parameter(
            'turbidity',
            1.0
        )

        self.declare_parameter(
            'alignment',
            1.0
        )

        self.declare_parameter(
            'receiver_threshold',
            0.05
        )

        # ==========================================================
        # Read parameters
        # ==========================================================

        self.distance = self.get_parameter(
            'distance'
        ).value

        self.max_range = self.get_parameter(
            'max_range'
        ).value

        self.transmitted_power = self.get_parameter(
            'transmitted_power'
        ).value

        self.absorption_coefficient = self.get_parameter(
            'absorption_coefficient'
        ).value

        self.scattering_coefficient = self.get_parameter(
            'scattering_coefficient'
        ).value

        self.turbidity = self.get_parameter(
            'turbidity'
        ).value

        self.alignment = self.get_parameter(
            'alignment'
        ).value

        self.receiver_threshold = self.get_parameter(
            'receiver_threshold'
        ).value

        # ==========================================================
        # ROS 2 Subscriber
        # ==========================================================

        self.subscription = self.create_subscription(
            String,
            '/laser/send',
            self.receive_message,
            10
        )

        # ==========================================================
        # ROS 2 Publisher
        # ==========================================================

        self.publisher = self.create_publisher(
            String,
            '/laser/receive',
            10
        )

        # ==========================================================
        # Information
        # ==========================================================

        self.get_logger().info(
            '------------------------------------------'
        )

        self.get_logger().info(
            'Underwater Laser Communication'
        )

        self.get_logger().info(
            f'Distance: {self.distance:.2f} m'
        )

        self.get_logger().info(
            f'Max range: {self.max_range:.2f} m'
        )

        self.get_logger().info(
            f'Transmitted power: '
            f'{self.transmitted_power:.3f}'
        )

        self.get_logger().info(
            f'Absorption: '
            f'{self.absorption_coefficient:.3f}'
        )

        self.get_logger().info(
            f'Scattering: '
            f'{self.scattering_coefficient:.3f}'
        )

        self.get_logger().info(
            f'Turbidity: '
            f'{self.turbidity:.3f}'
        )

        self.get_logger().info(
            f'Alignment: '
            f'{self.alignment:.3f}'
        )

        self.get_logger().info(
            '------------------------------------------'
        )

    # ==============================================================
    # Calculate received optical power
    # ==============================================================

    def calculate_received_power(self):

        # ----------------------------------------------------------
        # Total attenuation coefficient
        # ----------------------------------------------------------

        attenuation = (
            self.absorption_coefficient
            +
            self.scattering_coefficient
        )

        # Turbidity increases scattering losses
        effective_attenuation = (
            attenuation * self.turbidity
        )

        # ----------------------------------------------------------
        # Beer-Lambert style underwater optical attenuation
        #
        # P_r = P_t * exp(-c * d)
        # ----------------------------------------------------------

        received_power = (
            self.transmitted_power
            *
            math.exp(
                -effective_attenuation
                *
                self.distance
            )
        )

        # ----------------------------------------------------------
        # Laser alignment
        # ----------------------------------------------------------

        received_power *= self.alignment

        return received_power

    # ==============================================================
    # Receive packet
    # ==============================================================

    def receive_message(self, msg):

        self.get_logger().info(
            f'Received laser packet: "{msg.data}"'
        )

        # ----------------------------------------------------------
        # Range check
        # ----------------------------------------------------------

        if self.distance > self.max_range:

            self.get_logger().warn(
                'Laser communication failed.'
            )

            self.get_logger().warn(
                f'Distance {self.distance:.2f} m '
                f'> maximum range {self.max_range:.2f} m'
            )

            return

        # ----------------------------------------------------------
        # Alignment check
        # ----------------------------------------------------------

        if self.alignment <= 0.0:

            self.get_logger().warn(
                'Laser communication failed.'
            )

            self.get_logger().warn(
                'Laser is not aligned with receiver.'
            )

            return

        # ----------------------------------------------------------
        # Calculate received power
        # ----------------------------------------------------------

        received_power = (
            self.calculate_received_power()
        )

        self.get_logger().info(
            f'Received optical power: '
            f'{received_power:.6f}'
        )

        # ----------------------------------------------------------
        # Receiver sensitivity
        # ----------------------------------------------------------

        if (
            received_power
            <
            self.receiver_threshold
        ):

            self.get_logger().warn(
                'Laser packet LOST.'
            )

            self.get_logger().warn(
                f'Received power '
                f'{received_power:.6f} '
                f'< threshold '
                f'{self.receiver_threshold:.6f}'
            )

            return

        # ----------------------------------------------------------
        # Successful transmission
        # ----------------------------------------------------------

        self.publisher.publish(msg)

        self.get_logger().info(
            f'Laser packet DELIVERED: "{msg.data}"'
        )


# ==============================================================
# Main
# ==============================================================

def main(args=None):

    rclpy.init(args=args)

    node = LaserCommunication()

    try:

        rclpy.spin(node)

    except KeyboardInterrupt:

        pass

    finally:

        node.destroy_node()

        rclpy.shutdown()


if __name__ == '__main__':

    main()