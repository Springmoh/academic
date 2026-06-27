#include "PID/PID.h"
#include <rclcpp/rclcpp.hpp>
#include <rclcpp/executors.hpp>
#include "stdint.h"
#include <chrono>
#include <thread>
#include "geometry_msgs/msg/point.hpp"
#include "geometry_msgs/msg/point32.hpp"
#include "std_msgs/msg/bool.hpp"

using namespace std::chrono_literals;

#define La 200.0
#define BASE_HEIGHT 158.0
#define INITIAL_X 135.0
#define INITIAL_Y 0.0
#define INITIAL_Z 348.0
#define TARGET_X 330.0
#define TARGET_Y 260.0
#define CHILI_DISTANCE 280.0

class pid_calc : public rclcpp::Node
{
public:
    // Constructor
    pid_calc() : Node("pid_calc"), executor_(std::make_shared<rclcpp::executors::SingleThreadedExecutor>())
    {
        executor_->add_node(this->get_node_base_interface());
        RCLCPP_INFO(this->get_logger(), "Node has started!");

        rclcpp::QoS qos_profile(10);
        qos_profile.best_effort();

        target_coordinate_subscriber_ = this->create_subscription<geometry_msgs::msg::Point>(
            "target_coordinate",
            qos_profile,
            std::bind(&pid_calc::targetPointCallback, this, std::placeholders::_1));

        current_coor_subscriber_ = this->create_subscription<geometry_msgs::msg::Point32>(
            "current_coordinates",
            qos_profile,
            std::bind(&pid_calc::targetCoorCallback, this, std::placeholders::_1));

        target_request_subscriber_ = this->create_subscription<geometry_msgs::msg::Point32>(
            "target_request",
            qos_profile,
            std::bind(&pid_calc::targetRequestCallback, this, std::placeholders::_1));

        cutdata_subscriber_ = this->create_subscription<geometry_msgs::msg::Point>(
            "cutdata",
            qos_profile,
            std::bind(&pid_calc::cutdataCallback, this, std::placeholders::_1));

        target_point_publisher_ = this->create_publisher<geometry_msgs::msg::Point32>(
            "target_point",
            qos_profile);

        cut_publisher_ = this->create_publisher<std_msgs::msg::Bool>(
            "cut_request",
            qos_profile);

        timer_ = this->create_wall_timer(
            5ms,
            std::bind(&pid_calc::timerCallback, this));
    }

    // Method to run the main loop
    int run()
    {

        PIDSourceInit(&err_x, &out_x, &pid_x);
        PIDGainInit(0.005, 1.0, 1.0 / 320.0, 1.0, 1.0, 0.0, 0.0001, 60.0, &pid_x);
        PIDDelayInit(&pid_x);
        PIDSourceInit(&err_y, &out_y, &pid_y);
        PIDGainInit(0.005, 1.0, 1.0 / 320.0, 1.0, 1.0, 0.0, 0.0001, 60.0, &pid_y);
        PIDDelayInit(&pid_y);
        current_x = INITIAL_X;
        current_y = INITIAL_Y;
        current_z = INITIAL_Z;
        request_x = INITIAL_X;
        request_y = INITIAL_Y;
        request_z = INITIAL_Z;
        cnt = 0;
        no_target = 1.0;
        cut_request = false;
        limit_request = false;
        control_request = false;
        state = 0;

        while (rclcpp::ok())
        {
            executor_->spin_some();
        }
        return 0;
    }

private:
    std::shared_ptr<rclcpp::executors::SingleThreadedExecutor> executor_;
    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::Subscription<geometry_msgs::msg::Point>::SharedPtr target_coordinate_subscriber_;
    rclcpp::Subscription<geometry_msgs::msg::Point32>::SharedPtr current_coor_subscriber_;
    rclcpp::Subscription<geometry_msgs::msg::Point32>::SharedPtr target_request_subscriber_;
    rclcpp::Subscription<geometry_msgs::msg::Point>::SharedPtr cutdata_subscriber_;
    rclcpp::Publisher<geometry_msgs::msg::Point32>::SharedPtr target_point_publisher_;
    rclcpp::Publisher<std_msgs::msg::Bool>::SharedPtr cut_publisher_;

    float coordinate_x, coordinate_y, err_x, out_x, err_y, out_y;
    float current_x, current_y, current_z;
    float feedbackx, feedbacky, feedbackz;
    float request_x, request_y, request_z;
    float no_target;
    float chili_distance;
    bool limit_request, control_request;
    float tol_area, target_area;
    uint8_t state;
    uint16_t delaycnt;


    uint32_t cnt;
    bool cut_request;

    PID_t pid_x, pid_y;

    void cutdataCallback(const geometry_msgs::msg::Point::SharedPtr msg)
    {
        tol_area = msg->x;
        target_area = msg->y;
    }

    void targetRequestCallback(const geometry_msgs::msg::Point32::SharedPtr msg)
    {
        limit_request = true;
        request_x = msg->x;
        request_y = msg->y;
        request_z = msg->z;
        if(request_y != INITIAL_Y || request_z != INITIAL_Z){
            control_request = true;
        }
    }

    void targetPointCallback(const geometry_msgs::msg::Point::SharedPtr msg)
    {
        coordinate_x = (float)msg->x;
        coordinate_y = (float)msg->y;
        no_target = msg->z;
        
        err_x = TARGET_X - coordinate_x;
        err_y = TARGET_Y - coordinate_y;
    }

    void targetCoorCallback(const geometry_msgs::msg::Point32::SharedPtr msg)
    {
        feedbackx = msg->x;
        feedbacky = msg->y;
        feedbackz = msg->z;
    }

    void timerCallback() // 5ms
    {
        PID(&pid_x);
        PID(&pid_y);

        float limit = 0.1;

        if(out_x > limit){
            out_x = limit;
        } else if(out_x < -limit){
            out_x = -limit;
        }

        if(out_y > limit){
            out_y = limit;
        } else if(out_y < -limit){
            out_y = -limit;
        }

        if(control_request == false){ //auto
            switch(state){
                case 0: //return original pos
                    current_x = INITIAL_X;
                    current_y = INITIAL_Y;
                    current_z = INITIAL_Z;
                    cut_request = false;
                    delaycnt = delaycnt + 1;
                    if(delaycnt > 200){ //1s
                        state = 1;
                        delaycnt = 0;
                    }
                break;

                case 1: //move to target
                    chili_distance = limit_request ? request_x : CHILI_DISTANCE;
                    if(current_x < chili_distance && err_x == 0 && err_y == 0 && no_target == 0.0){
                        current_x += 0.1;
                    }
                    if(current_x > chili_distance){
                        current_x = chili_distance;
                    }
                    current_y = current_y + out_x;
                    current_z = current_z + out_y;
                    if(fabs(chili_distance - current_x) < 1.0 && current_x > 230.0 && err_x == 0 && err_y == 0 && no_target == 0.0){
                        state = 2;
                    }
                break;

                case 2: //stop for a while
                    delaycnt = delaycnt + 1;
                    if(delaycnt > 200){ //1s
                        state = 3;
                        delaycnt = 0;
                    }
                break;

                case 3: //cut
                    cut_request = true;
                    delaycnt = delaycnt + 1;
                    if(delaycnt > 200){ //1s
                        state = 4;
                        delaycnt = 0;
                    }
                break;

                case 4: //release cut
                    cut_request = false;
                    delaycnt = delaycnt + 1;
                    if(delaycnt > 200){ //1s
                        state = 5;
                        delaycnt = 0;
                    }
                break;

                case 5: //x to ori pos
                    current_x = INITIAL_X;
                    delaycnt = delaycnt + 1;
                    if(delaycnt > 200){ //1s
                        state = 0;
                        delaycnt = 0;
                    }
                break;

            }

        }else{ //manual
            current_x = request_x;
            current_y = request_y;
            current_z = request_z;
            cut_request = false;
        }

        // Publish target point
        geometry_msgs::msg::Point32 point_msg;
        point_msg.x = current_x;
        point_msg.y = current_y;
        point_msg.z = current_z;

        std_msgs::msg::Bool cut;
        cut.data = cut_request;

        target_point_publisher_->publish(point_msg);
        cut_publisher_->publish(cut);

        RCLCPP_INFO(this->get_logger(), "Out_x: %.3f, Out_y: %.3f, CR: %d, LR: %d", out_x, out_y, control_request, limit_request);
    
        
    }
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<pid_calc>();
    node->run();
    rclcpp::shutdown();
    return 0;
}