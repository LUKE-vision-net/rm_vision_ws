import rclpy 
import cv2
import numpy as np 
import math
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from std_msgs.msg import Float32MultiArray 

class S1Detector(Node):
    def __init__(self):
     super().__init__('s1_detector_node')
     self.subscription = self.create_subscription(Image,'/image_raw',self.image_callback,10)

     self.bridge= CvBridge()
     self.get_logger().info('S1 识别单元已启动 正在等待 S0 的图像')
     self.publisher =self.create_publisher(Float32MultiArray,'armor_rect',10)
     
    def image_callback(self,msg):
        print("叮咚，收到新图片")
        img =self.bridge.imgmsg_to_cv2(msg,desired_encoding='bgr8')
        if img is None:
            print("识图失败，未识别到图片")

        hsv=cv2.cvtColor (img,cv2.COLOR_BGR2HSV)

        lower1 = np.array([100, 80, 50])
        upper1 = np.array([140, 255, 255])

        mask=cv2.inRange(hsv,lower1,upper1)

        contours,_=cv2.findContours(mask, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)



        light_bars=[]
        for contour in contours:
            area=cv2.contourArea(contour)
            if area>10:
                x,y,w,h=cv2.boundingRect(contour)
                if w>h:
                    w,h=h,w
                cx=x+w/2
                cy=y+h/2
                light_bars.append ({'x':x,'y':y,'w':w,'h':h,'cx':cx,'cy':cy})
                cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),1)

        for i in range(len(light_bars)) :
            for j in range(i+1,len(light_bars)):
                bar1=light_bars[i]
                bar2=light_bars[j]



            if abs (bar1['cy']-bar2['cy'])>200:
                continue

        
            

        
           

            armor_x=min(bar1['x'],bar2['x'])
            armor_y=min(bar1['y'],bar2['y'])
            armor_x_max=max(bar1['x']+bar1['w'],bar2['x']+bar2['w'])
            armor_y_max=max(bar1['y']+bar1['h'],bar2['y']+bar2['h'])
            armor_width=armor_x_max-armor_x
            armor_height=armor_y_max-armor_y
            
           
            if armor_width/armor_height>2:
                continue
            
            armor_cx=(armor_x+ armor_x_max)/2
            armor_cy=(armor_y+ armor_y_max)/2
            cv2.rectangle(img,(armor_x,armor_y),(armor_x_max,armor_y_max),(0,255,0),2)
            cv2.putText(img,"S1 Detected",(armor_x,armor_y-10),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2)
            cv2.circle(img,(int(armor_cx),int(armor_cy)),4,(0,0,255),-1)
            out_msg=Float32MultiArray()
            out_msg.data=[float(armor_x),float(armor_y),float(armor_width),float(armor_height)]
            self.publisher.publish(out_msg)
            
            
        cv2.imshow("S1 Detector Window",img)
        cv2.waitKey(1)
def main(args=None):
   rclpy.init(args=args)
   node =S1Detector()
   rclpy.spin(node)
   node.destroy_node()
   cv2.destroyAllWindows()
   rclpy.shutdown()



if __name__ =='__main__':
   main()