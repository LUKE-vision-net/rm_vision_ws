#include <iostream>
#include <vector>
#include <opencv2/opencv.hpp>
#include <cmath>
#include <rclcpp/rclcpp.hpp>
#include<std_msgs/msg/float32_multi_array.hpp>
const float RL_armor_width =0.135; 
const float RL_armor_height=0.055;
class S2PnPNode : public rclcpp::Node{
public:
    S2PnPNode():Node("S2_PnP_Node"){
    subscription_= this->create_subscription<std_msgs::msg::Float32MultiArray>(
        "armor_rect",10,std::bind(&S2PnPNode::rect_callback,this,std::placeholders::_1));
    RCLCPP_INFO(this->get_logger(),"S2 node started, waiting for S1...");
    }
private:


    void rect_callback(const std_msgs::msg::Float32MultiArray::SharedPtr msg){
         if(msg->data.size()<4)return;
        float x = msg->data[0];
        float y = msg->data[1];
        float w = msg->data[2];
        float h = msg->data[3];
             cv::Rect armor_rect((int)x,(int)y,(int)w,(int)h);
             solveArmorPnP(armor_rect,RL_armor_width,RL_armor_height);
            };

std::vector<cv::Point3f> getArmorObjectPoints(float RL_armor_width, float RL_armor_height) {
    return {
        {-RL_armor_width / 2.0f,   RL_armor_height/ 2.0f, 0.0f}, // 左上
        { RL_armor_width / 2.0f,   RL_armor_height/ 2.0f, 0.0f}, // 右上
        { RL_armor_width / 2.0f, -RL_armor_height/ 2.0f, 0.0f}, // 右下
        {-RL_armor_width / 2.0f,  -RL_armor_height/ 2.0f, 0.0f}  // 左下
    };
}

void solveArmorPnP(const cv::Rect& armor_rect, float RL_armor_width, float RL_armor_height) {
    // 1. 提取2D像素点
    std::vector<cv::Point2f> image_points = {
       {(float)armor_rect.x,(float)armor_rect.y},
       {(float)(armor_rect.x+armor_rect.width),(float)armor_rect.y},
       {(float)(armor_rect.x+armor_rect.width),(float)(armor_rect.y+armor_rect.height)},
       {(float)armor_rect.x,(float)(armor_rect.y+armor_rect.height)}
    };

    // 2. 获取3D物理点
    std::vector<cv::Point3f> object_points = getArmorObjectPoints(RL_armor_width, RL_armor_height);

    // 3. 相机内参
    cv::Mat camera_matrix = (cv::Mat_<double>(3, 3) << 
        800.0, 0.0, 400.0,
        0.0, 800.0, 300.0,
        0.0, 0.0, 1.0);
    cv::Mat dist_coeffs = cv::Mat::zeros(5, 1, CV_64F);

    cv::Mat rvec, tvec;
    bool success = false;

    // 4. PnP 解算
    try {
        success = cv::solvePnP(
            object_points, image_points, camera_matrix, dist_coeffs, 
            rvec, tvec, false, cv::SOLVEPNP_IPPE_SQUARE
        );
    } catch (const std::exception& e) {
        std::cerr << "PnP Error: " << e.what() << std::endl;
        return;
    }

    // 5. 处理结果
    if (success) {
        double  x = tvec.at<double>(0, 0);
        double  y = tvec.at<double>(1, 0);
        double  z = tvec.at<double>(2, 0);

        if ( z > 0.5 &&  z < 15.0) {
            double yaw = std::atan2( x,  z);
            double pitch = std::atan2( y, std::sqrt( x* x +  z* z));
            double yaw_deg = yaw * 180.0 / CV_PI;
            double pitch_deg = pitch * 180.0 / CV_PI;

            std::cout << "====== PnP Success ======" << std::endl;
            std::cout << "distance_Z: " << z << " meters" << std::endl;
            std::cout << "YAW: " << yaw_deg << " deg, PITCH: " << pitch_deg << " deg" << std::endl;
            } else {
                std::cout << "PnP distance abnormal, drop frame." << std::endl;
            }
        } else {
            std::cout << "PnP computation fail." << std::endl;
        }
    } 
    rclcpp::Subscription<std_msgs::msg::Float32MultiArray>::SharedPtr subscription_;
   };

int main(int argc, char** argv) {
    rclcpp::init(argc,argv);
    rclcpp::spin(std::make_shared<S2PnPNode>());
    rclcpp::shutdown();
    return 0;
}
