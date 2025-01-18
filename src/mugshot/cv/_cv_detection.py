from mugshot.mouse_input import FrameInput
import os
import cv2
from ultralytics import YOLO
import dlib
import imutils
from imutils import face_utils
from scipy.spatial import distance as dist

# Set up paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(CURRENT_DIR, "best.pt")
LANDMARK_MODEL_DIR = os.path.join(CURRENT_DIR, "shape_predictor_68_face_landmarks.dat")


class CVDetection:
    def __init__(self):
        # Load the YOLO model
        self.yolo_model = YOLO(MODEL_DIR)

        # Initializing the Models for Landmark and face Detection
        self.detector = dlib.get_frontal_face_detector()  # type: ignore
        self.landmark_predict = dlib.shape_predictor(LANDMARK_MODEL_DIR)  # type: ignore

    def process_frame(
        self, frame: cv2.typing.MatLike
    ) -> tuple[cv2.typing.MatLike, FrameInput]:

        # Function to calculate Eye Aspect Ratio (EAR)
        def calculate_EAR(eye):
            y1 = dist.euclidean(eye[1], eye[5])  # Vertical distance
            y2 = dist.euclidean(eye[2], eye[4])  # Vertical distance
            x1 = dist.euclidean(eye[0], eye[3])  # Horizontal distance
            ear = (y1 + y2) / x1
            return ear

        # Define constants
        EYE_AR_THRESH = 0.45  # Threshold for eye closure
        EYE_AR_CONSEC_FRAMES = 3  # Minimum consecutive frames to consider eye closed

        frame_input = FrameInput()

        # Eye landmarks
        (L_start, L_end) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
        (R_start, R_end) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

        # Initialize frame counters
        left_eye_counter = 0
        right_eye_counter = 0

        # Perform YOLO inference on the frame
        results = self.yolo_model.predict(
            source=frame, conf=0.5, save=False
        )  # Set confidence threshold as needed

        # Visualize detections
        annotated_frame = results[0].plot()  # Draw boxes and labels on the frame

        # Resize the frame
        frame = imutils.resize(frame, width=640)

        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the frame
        faces = self.detector(gray)
        for face in faces:
            # Get the facial landmarks
            shape = self.landmark_predict(gray, face)
            landmarks = [[p.x, p.y] for p in shape.parts()]

            # Converting the shape class directly to a list of (x,y) coordinates
            shape = face_utils.shape_to_np(shape)

            # Extract the left and right eye coordinates
            left_eye = landmarks[L_start:L_end]
            right_eye = landmarks[R_start:R_end]

            # Calculate EAR for both eyes
            left_ear = calculate_EAR(left_eye)
            right_ear = calculate_EAR(right_eye)

            # Check if the left eye is closed
            if left_ear < EYE_AR_THRESH:
                left_eye_counter += 1
            else:
                left_eye_counter = 0

            # Check if the right eye is closed
            if right_ear < EYE_AR_THRESH:
                right_eye_counter += 1
            else:
                right_eye_counter = 0

            # Draw results on the frame
            cv2.putText(
                annotated_frame,
                f"Left EAR: {left_ear:.2f}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )
            cv2.putText(
                annotated_frame,
                f"Right EAR: {right_ear:.2f}",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )

            if left_eye_counter >= EYE_AR_CONSEC_FRAMES:
                cv2.putText(
                    annotated_frame,
                    "Left Eye Closed",
                    (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2,
                )
                frame_input.is_left_eye_closed = True
            else:
                frame_input.is_left_eye_closed = False

            if right_eye_counter >= EYE_AR_CONSEC_FRAMES:
                cv2.putText(
                    annotated_frame,
                    "Right Eye Closed",
                    (10, 120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2,
                )
                frame_input.is_right_eye_closed = True
            else:
                frame_input.is_right_eye_closed

        return (annotated_frame, frame_input)
