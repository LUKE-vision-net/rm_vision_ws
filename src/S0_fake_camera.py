import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
import numpy as np
import cv2

class FakeCamera(Node):
    def __init__(self):
        super().__init__('fake_camera_node')
        # 发布图像和相机内参
        self.pub_img = self.create_publisher(Image, '/image_raw', 10)
        self.pub_info = self.create_publisher(CameraInfo, '/camera_info', 10)
        
        # 30Hz 定时器
        self.timer = self.create_timer(1.0 / 30.0, self.timer_callback)
        self.t = 0.0
        self.get_logger().info('假数据发生器已启动！正在发布 /image_raw...')

    def timer_callback(self):
        # 生成一张 800x600 的纯黑图片
        img = np.zeros((600, 800, 3), dtype=np.uint8)
        
        # 让一个白色的“装甲板”在画面里移动
        self.t += 0.05
        x_center = int(400 + 200 * np.sin(self.t))
        y_center = 300
        
        # 画两个蓝色的灯条（模拟真实装甲板颜色）
        cv2.rectangle(img, (x_center - 60, y_center - 40), (x_center - 40, y_center + 40), (255, 0, 0), -1)
        cv2.rectangle(img, (x_center + 40, y_center - 40), (x_center + 60, y_center + 40), (255, 0, 0), -1)

        # 构造并发布 Image 消息
        msg_img = Image()
        msg_img.header.stamp = self.get_clock().now().to_msg()
        msg_img.header.frame_id = "camera_optical_frame"
        msg_img.height = 600
        msg_img.width = 800
        msg_img.encoding = 'bgr8'
        msg_img.is_bigendian = 0
        msg_img.step = 800 * 3
        msg_img.data = img.tobytes()
        self.pub_img.publish(msg_img)

        # 构造并发布 CameraInfo 消息（S2 算 PnP 就靠这个内参了）
        msg_info = CameraInfo()
        msg_info.header.stamp = msg_img.header.stamp
        msg_info.header.frame_id = "camera_optical_frame"
        msg_info.height = 600
        msg_info.width = 800
        msg_info.distortion_model = "plumb_bob"
        msg_info.d = [0.0, 0.0, 0.0, 0.0, 0.0] # 无畸变
        # 焦距 fx=800, fy=800, 光心 cx=400, cy=300
        msg_info.k = [800.0, 0.0, 400.0, 0.0, 800.0, 300.0, 0.0, 0.0, 1.0]
        self.pub_info.publish(msg_info)

def main(args=None):
    rclpy.init(args=args)
    node = FakeCamera()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()





