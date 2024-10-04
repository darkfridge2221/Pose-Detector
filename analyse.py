import cv2
import mediapipe as mp

#Volleyball action detection function (spiking, blocking, defending)
def detect_volleyball_action(pose_landmarks):
    mp_pose = mp.solutions.pose
    if pose_landmarks:
        left_wrist = pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]
        right_wrist = pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
        left_shoulder = pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]

        left_hand_up = left_wrist.y < left_shoulder.y
        right_hand_up = right_wrist.y < right_shoulder.y

        if left_hand_up and right_hand_up:
            return "Blocking"
        elif left_hand_up or right_hand_up:
            return "Spiking"
        else:
            return "Defending"
    return "Unknown"

#Callback function for the trackbar
def on_trackbar(val):
    pass

#Function to analyse video and display volleyball actions
def analyse_video(video_path):
    mp_pose = mp.solutions.pose
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cv2.namedWindow('Volleyball Pose Estimation')
    #Add trackbar for scrubbing through the video
    cv2.createTrackbar('Position', 'Volleyball Pose Estimation', 0, total_frames, on_trackbar)
    is_paused = False
    with mp_pose.Pose(static_image_mode=False, model_complexity=1, enable_segmentation=False,
                      min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            if not is_paused:
                trackbar_pos = cv2.getTrackbarPos('Position', 'Volleyball Pose Estimation')
                cap.set(cv2.CAP_PROP_POS_FRAMES, trackbar_pos)

                ret, frame = cap.read()
                if not ret:
                    print("Reached the end of the video.")
                    break

                image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(image_rgb)
                action = "No Action Detected"

                if results.pose_landmarks:
                    action = detect_volleyball_action(results.pose_landmarks)
                    mp.solutions.drawing_utils.draw_landmarks(
                        frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                colour = (0, 255, 0)
                font_scale = 1
                if action == "Spiking":
                    colour = (0, 0, 255)
                    font_scale = 1.5
                elif action == "Blocking":
                    colour = (255, 0, 0)
                    font_scale = 1.5

                #Add action text to the frame
                cv2.putText(frame, f"Action: {action}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX,
                            font_scale, colour, 2, cv2.LINE_AA)

                #Display the frame with pose and action information
                cv2.imshow('Volleyball Pose Estimation', frame)

                #Update trackbar position based on current frame
                current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
                cv2.setTrackbarPos('Position', 'Volleyball Pose Estimation', current_frame)

            #Handle key events for play/pause functionality
            key = cv2.waitKey(30) & 0xFF
            if key == ord('q'):  #Quit the video
                break
            elif key == ord('p'):  #Toggle pause/play
                is_paused = not is_paused

    #Release video capture object and destroy all windows
    cap.release()
    cv2.destroyAllWindows()
