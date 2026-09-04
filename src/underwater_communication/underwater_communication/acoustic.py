import random

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class AcousticCommunication(Node):

    def __init__(self):

        super().__init__('acoustic_communication')

        # ==========================================================
        # Parameters
        # ==========================================================

        self.declare_parameter(
            'distance',
            50.0
        )

        self.declare_parameter(
            'max_range',
            100.0
        )

        self.declare_parameter(
            'sound_speed',
            1500.0
        )

        self.declare_parameter(
            'min_packet_loss',
            0.02
        )

        self.declare_parameter(
            'max_packet_loss',
            0.40
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

        self.sound_speed = self.get_parameter(
            'sound_speed'
        ).value

        self.min_packet_loss = self.get_parameter(
            'min_packet_loss'
        ).value

        self.max_packet_loss = self.get_parameter(
            'max_packet_loss'
        ).value

        # ==========================================================
        # ROS 2 Subscriber
        # ==========================================================

        self.subscription = self.create_subscription(
            String,
            '/acoustic/send',
            self.receive_message,
            10
        )

        # ==========================================================
        # ROS 2 Publisher
        # ==========================================================

        self.publisher = self.create_publisher(
            String,
            '/acoustic/receive',
            10
        )

        # ==========================================================
        # Information
        # ==========================================================

        self.get_logger().info(
            '------------------------------------------'
        )

        self.get_logger().info(
            'Underwater Acoustic Communication'
        )

        self.get_logger().info(
            f'Distance: {self.distance:.2f} m'
        )

        self.get_logger().info(
            f'Max range: {self.max_range:.2f} m'
        )

        self.get_logger().info(
            f'Sound speed: {self.sound_speed:.2f} m/s'
        )

        self.get_logger().info(
            '------------------------------------------'
        )

    # ==============================================================
    # Packet loss model
    # ==============================================================

    def calculate_packet_loss(self):

        if self.distance <= 0.0:

            return self.min_packet_loss

        if self.distance >= self.max_range:

            return 1.0

        ratio = self.distance / self.max_range

        packet_loss = (
            self.min_packet_loss
            +
            (
                self.max_packet_loss
                -
                self.min_packet_loss
            )
            * ratio
        )

        return max(
            0.0,
            min(packet_loss, 1.0)
        )

    # ==============================================================
    # Propagation delay
    # ==============================================================

    def calculate_delay(self):

        if self.sound_speed <= 0.0:

            return 0.0

        return self.distance / self.sound_speed

    # ==============================================================
    # Receive packet
    # ==============================================================

    def receive_message(self, msg):

        self.get_logger().info(
            f'Received acoustic packet: "{msg.data}"'
        )

        # ----------------------------------------------------------
        # Range check
        # ----------------------------------------------------------

        if self.distance > self.max_range:

            self.get_logger().warn(
                'Acoustic communication failed.'
            )

            self.get_logger().warn(
                f'Distance {self.distance:.2f} m '
                f'> maximum range {self.max_range:.2f} m'
            )

            return

        # ----------------------------------------------------------
        # Packet loss
        # ----------------------------------------------------------

        packet_loss = self.calculate_packet_loss()

        self.get_logger().info(
            f'Packet loss probability: '
            f'{packet_loss * 100:.2f}%'
        )

        random_number = random.random()

        if random_number < packet_loss:

            self.get_logger().warn(
                'Acoustic packet LOST.'
            )

            return

        # ----------------------------------------------------------
        # Propagation delay
        # ----------------------------------------------------------

        delay = self.calculate_delay()

        self.get_logger().info(
            'Acoustic packet accepted.'
        )

        self.get_logger().info(
            f'Propagation delay: {delay:.4f} seconds'
        )

        # ----------------------------------------------------------
        # Create delayed transmission
        # ----------------------------------------------------------

        timer = self.create_timer(
            delay,
            lambda: self.deliver_packet(
                msg,
                timer
            )
        )

    # ==============================================================
    # Deliver packet
    # ==============================================================

    def deliver_packet(self, msg, timer):

        self.publisher.publish(msg)

        self.get_logger().info(
            f'Acoustic packet DELIVERED: "{msg.data}"'
        )

        timer.cancel()


# ==============================================================
# Main
# ==============================================================

def main(args=None):

    rclpy.init(args=args)

    node = AcousticCommunication()

    try:

        rclpy.spin(node)

    except KeyboardInterrupt:

        pass

    finally:

        node.destroy_node()

        rclpy.shutdown()


if __name__ == '__main__':

    main()