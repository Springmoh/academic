#include <rclcpp/rclcpp.hpp>
#include "stdint.h"
#include "stdio.h"
#include <math.h>
#include <chrono>
#include <thread>

#include "geometry_msgs/msg/point32.hpp"

#define La 200.0
#define BASE_HEIGHT 158.0
#define INITIAL_X 135.0
#define INITIAL_Y 0.0
#define INITIAL_Z 348.0

using namespace std::chrono_literals;

class angle_calc : public rclcpp::Node
{
public:
    // Constructor
    angle_calc() : Node("angle_calc")
    {
        RCLCPP_INFO(this->get_logger(), "Node has started!");

        rclcpp::QoS qos_profile(10);
        qos_profile.best_effort();

        target_point_subscriber_ = this->create_subscription<geometry_msgs::msg::Point32>(
            "target_point",
            qos_profile,
            std::bind(&angle_calc::targetPointCallback, this, std::placeholders::_1));

        joint_angles_publisher_ = this->create_publisher<geometry_msgs::msg::Point32>(
            "joint_angles",
            qos_profile);

        stm32_publisher_ = this->create_publisher<geometry_msgs::msg::Point32>(
            "stm32_angles",
            qos_profile);


        timer_ = this->create_wall_timer(
            5ms,
            std::bind(&angle_calc::timerCallback, this));
    }

    // Method to run the main loop
    int run()
    {
        rclcpp::executors::SingleThreadedExecutor executor;
        executor.add_node(this->shared_from_this());

        while (rclcpp::ok())
        {
            executor.spin_some();
        }

        return 0;
    }

private:
    rclcpp::TimerBase::SharedPtr timer_;

    rclcpp::Subscription<geometry_msgs::msg::Point32>::SharedPtr target_point_subscriber_;
    rclcpp::Publisher<geometry_msgs::msg::Point32>::SharedPtr joint_angles_publisher_;
    rclcpp::Publisher<geometry_msgs::msg::Point32>::SharedPtr stm32_publisher_;

    // =========================
    // Manipulated variable
    // =========================
    double x_t = INITIAL_X;
    double y_t = INITIAL_Y;
    double z_t = INITIAL_Z;

    // =========================
    // Buffer for calculation
    // =========================
    double l = 0.0;
    double h = 0.0;
    double phi = 0.0;
    double theta = 0.0;
    bool runonce = false;
    double a_b_offset = 0.0;
    double a_e_offset = 0.0;
    double a_w_offset = 0.0;

    // =========================
    // Output angle
    // =========================
    double a_b = 0.0;
    double a_e = 0.0;
    double a_w = 0.0;

    void targetPointCallback(const geometry_msgs::msg::Point32::SharedPtr msg)
    {
        if(runonce == true){
            x_t = msg->x;
            y_t = msg->y;
            z_t = msg->z - BASE_HEIGHT;
        }
    }

    void timerCallback() // 5ms
    {
        // Avoid division by zero because your algorithm uses y_t / x_t
        if (x_t <= 0.0)
        {
            RCLCPP_WARN(this->get_logger(), "FAIL: x_t must be > 0");
            return;
        }

        if(runonce == false){
            x_t = INITIAL_X;
            y_t = INITIAL_Y;
            z_t = INITIAL_Z - BASE_HEIGHT;
        }

        // =========================
        // Your final algorithm
        // =========================
        l = sqrt(pow(x_t, 2) + pow(y_t, 2));

        h = sqrt(pow(z_t, 2) + pow(x_t, 2) + pow(y_t, 2));

        phi = atan(z_t / l);

        // Check reachable range before acos()
        if (h > (2.0 * La))
        {
            RCLCPP_WARN(this->get_logger(), "FAIL: target point is out of reachable range");
            return;
        }

        theta = acos(h / (2.0 * La));

        a_b = atan(y_t / x_t);

        a_e = phi + theta;

        a_w = phi - theta;

        // =========================
        // Publish joint angles
        // x = a_b
        // y = a_e
        // z = a_w
        // Unit: radian
        // =========================
        geometry_msgs::msg::Point32 joint_angles_msg;
        geometry_msgs::msg::Point32 stm32_angles_msg;
        if(runonce == true){
            joint_angles_msg.x = a_b;
            joint_angles_msg.y = a_e;
            joint_angles_msg.z = a_w;
            stm32_angles_msg.x = (a_b - a_b_offset) * 180.0 / M_PI;
            stm32_angles_msg.y = (a_e - a_e_offset) * 180.0 / M_PI;
            stm32_angles_msg.z = (a_w - a_w_offset) * 180.0 / M_PI;
            joint_angles_publisher_->publish(joint_angles_msg);
            stm32_publisher_->publish(stm32_angles_msg);
        }else{
            a_b_offset = a_b;
            a_e_offset = a_e;
            a_w_offset = a_w;
            RCLCPP_INFO(this->get_logger(), "Ab = %.3lf, Ae = %.3lf, Aw = %.3lf,", a_b_offset, a_e_offset, a_w_offset);
            runonce = true;
        }
    }
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<angle_calc>();
    node->run();
    rclcpp::shutdown();
    return 0;
}