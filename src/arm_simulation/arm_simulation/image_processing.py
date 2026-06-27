#!/home/mohnc/ros2_ws/.env/bin/python3
from ultralytics import YOLO
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from std_msgs.msg import Int16
from arm_simulation.home_config import TARGET_X, TARGET_Y
import cv2
import time
import torch
import math

class ImageProcessing(Node):

    def __init__(self):
        super().__init__('image_processing')
        self.model = YOLO("/home/mohnc/ros2_ws/src/arm_simulation/arm_simulation/model/last_minV1.pt")
        # self.model = YOLO("yolo26n.pt")
        self.target_track_id = 1
        self.timeout = 1.0
        self.x_publish = TARGET_X
        self.y_publish = TARGET_Y
        self.z_publish = 0.0

        # Select and log device
        if torch.cuda.is_available():
            self.device = "cuda:0"
            gpu_name = torch.cuda.get_device_name(0)
            self.get_logger().info(f"CUDA available. Using GPU: {gpu_name}")
        else:
            self.device = "cpu"
            self.get_logger().warn("CUDA not available. Using CPU.")
        
        # Create publisher for target coordinates with best effort QoS
        qos_profile = rclpy.qos.QoSProfile(depth=10)
        qos_profile.reliability = rclpy.qos.ReliabilityPolicy.BEST_EFFORT
        self.target_publisher_ = self.create_publisher(
            Point,
            'target_coordinate',
            qos_profile
        )

        self.cutdata_publisher_ = self.create_publisher(
            Point,
            'cutdata',
            qos_profile
        )

        self.result_publisher_ = self.create_publisher(
            Int16,
            'results',
            qos_profile
        )

            
        video_path = "/dev/video4"
        # video_path = "/home/mohnc/Desktop/File/academic/IDP/test/output1.mp4"
        
        self.cap = cv2.VideoCapture(video_path)

        #to record video
        frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = 20.0 # Standard FPS
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.out = cv2.VideoWriter('/home/mohnc/Downloads/output.mp4', fourcc, fps, (frame_width, frame_height))

    def run(self):
        target_lost = False
        target_lost_time = 0.0
        retrackx_min = 0
        retrackx_max = 0
        retracky_min = 0
        retracky_max = 0
        tolx_min = TARGET_X - 30
        tolx_max = TARGET_X + 30
        toly_min = TARGET_Y - 30
        toly_max = TARGET_Y + 30
        nearest_dist = 0
        nearest = 0
        while self.cap.isOpened():
            start_time = time.time()
            success, frame = self.cap.read()


            if success:

                #for recording video
                self.out.write(frame) # Save frame

                results = self.model.track(frame, persist=True, verbose=False)

                max_area = 0
                
                if results[0].boxes is not None and results[0].boxes.id is not None:
                    boxes = results[0].boxes
                    track_ids = results[0].boxes.id.int().cpu().tolist()
                    index = 0

                    for box, track_id in zip(boxes, track_ids):
                        x_min, y_min, x_max, y_max = box.xyxy[0].tolist()
                        x_center = (x_min + x_max) / 2.0
                        y_center = (y_min + y_max) / 2.0
                        tx_center = 0
                        ty_center = 0
                        confidence = box.conf[0].item()

                        # print(f"Track ID: {track_id}")

                        if(track_id == self.target_track_id):
                            if((x_max - x_min) > 50):
                                retrackx_min = x_min
                                retrackx_max = x_max
                            else:
                                retrackx_min = x_min
                                retrackx_max = x_min + 50

                            if((y_max - y_min) > 50):
                                retracky_min = y_min
                                retracky_max = y_max
                            else:
                                retracky_min = y_min
                                retracky_max = y_min + 50

                            tx_center = x_center
                            ty_center = y_center

                            cutdata_msg = Point()


                            target_area = (x_max - x_min) * (y_max - y_min)
                            tol_area = (tolx_max - tolx_min) * (toly_max - toly_min)
                            cutdata_msg.x = tol_area
                            cutdata_msg.y = target_area
                            cutdata_msg.z = 0.0
                            self.cutdata_publisher_.publish(cutdata_msg)
                            self.get_logger().info(f"tol_area: {tol_area:.2f}, TargetArea: {target_area:.2f}")

                            if(tolx_min < x_center < tolx_max and toly_min < y_center < toly_max):
                                self.x_publish = TARGET_X
                                self.y_publish = TARGET_Y
                            else:
                                self.x_publish = (x_min + x_max) / 2.0
                                self.y_publish = (y_min + y_max) / 2.0
                            self.z_publish = 0.0
                            
                        cv2.rectangle(
                            frame,
                            (int(x_min), int(y_min)),
                            (int(x_max), int(y_max)),
                            (0, 0, 255),
                            2
                            )

                        dist = math.sqrt((tx_center-x_center)*(tx_center-x_center) + (ty_center-y_center)*(ty_center-y_center))

                        if(dist < nearest_dist):
                            nearest = track_id
                            nearest_dist = dist
                        

                        if(target_lost == True):
                            if(retrackx_min < x_center and x_center < retrackx_max and retracky_min < y_center and y_center < retracky_max):
                                self.target_track_id = track_id
                                target_lost = False

                        
                        
                        cv2.putText(
                            frame,
                            f"Track ID: {track_id}, dist: {dist:.2f}",
                            (int(x_min), int(y_min) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (0, 0, 255),
                            2
                        )

                        box_area = (x_max - x_min) * (y_max - y_min)

                        if box_area > max_area:
                            max_area = box_area
                            max_target_track_id = track_id
                            max_x_min, max_y_min, max_x_max, max_y_max = x_min, y_min, x_max, y_max
                        index = index + 1;
                    
                    result_msg = Int16()
                    result_msg.data = index
                    self.result_publisher_.publish(result_msg)


                    # cv2.rectangle(
                    #     frame,
                    #     (int(max_x_min), int(max_y_min)),
                    #     (int(max_x_max), int(max_y_max)),
                    #     (0, 255, 0),
                    #     2
                    # )

                    if self.target_track_id not in track_ids:
                       if target_lost == False:
                            target_lost_time = time.time()
                            target_lost = True

                    else:
                          target_lost = False

                    

                    if target_lost and (time.time() - target_lost_time) > self.timeout:
                    #    self.target_track_id = max_target_track_id
                        self.target_track_id = nearest

                    # self.get_logger().info(f"Current target track ID: {self.target_track_id}")

                else:
                    max_area = 0
                    self.x_publish = TARGET_X
                    self.y_publish = TARGET_Y
                    self.z_publish = 1.0

                cv2.rectangle(
                        frame,
                        (int(retrackx_min), int(retracky_min)),
                        (int(retrackx_max), int(retracky_max)),
                        (0, 255, 0),
                        2
                    )
                
                cv2.line(frame, (0, int(TARGET_Y)), (640, int(TARGET_Y)), (0, 255, 0), 1)
                cv2.line(frame, (int(TARGET_X), 0), (int(TARGET_X), 480), (0, 255, 0), 1)
                
                cv2.rectangle(
                        frame,
                        (int(tolx_min), int(toly_min)),
                        (int(tolx_max), int(toly_max)),
                        (255, 255, 255),
                        2
                    )
                
                endtime = time.time()
                cv2.putText(frame, f"FPS: {(1.0 / (endtime - start_time)):.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # # Publish detected target coordinates
                # if len(results[0].boxes) > 0:
                #     # Get the first detection's bounding box
                #     box = results[0].boxes[0]
                #     x_min, y_min, x_max, y_max = box.xyxy[0].tolist()
                #     # Calculate center point
                #     center_x = (x_min + x_max) / 2.0
                #     center_y = (y_min + y_max) / 2.0


                    
                #     # Create and publish Point message
                point_msg = Point()
                point_msg.x = self.x_publish
                point_msg.y = self.y_publish
                point_msg.z = self.z_publish
                # self.get_logger().info(f"Publishing target coordinates: x={self.x_publish}, y={self.y_publish}")
                self.target_publisher_.publish(point_msg)



                cv2.imshow("YOLO Inference", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            else:
                break

        self.cap.release()
        self.out.release() # Release the video writer
        cv2.destroyAllWindows()

def main(args=None):
    rclpy.init(args=args)
    node = ImageProcessing()

    try:
        node.run()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()