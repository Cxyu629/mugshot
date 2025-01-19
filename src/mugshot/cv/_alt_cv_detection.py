from ._base_cv_detection import BaseCVDetection
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
MODEL_DIR = os.path.join(CURRENT_DIR, "best_alt.pt")
LANDMARK_MODEL_DIR = os.path.join(CURRENT_DIR, "shape_predictor_68_face_landmarks.dat")


class AltCVDetection(BaseCVDetection):

    def __init__(self):
        # Load the YOLO model
        self.yolo_model = YOLO(MODEL_DIR)

        # Initializing the Models for Landmark and face Detection
        self.detector = dlib.get_frontal_face_detector()  # type: ignore
        self.landmark_predict = dlib.shape_predictor(LANDMARK_MODEL_DIR)  # type: ignore

        # Initialize frame counters
        self.left_eye_counter = 0
        self.right_eye_counter = 0

        self.EYE_AR_THRESH = 0.45
        """Threshold for eye closure"""

        self.EYE_AR_CONSEC_FRAMES = 3
        """Minimum consecutive frames to consider eye closed"""

    def process_frame(
        self, frame: cv2.typing.MatLike
    ) -> tuple[cv2.typing.MatLike, FrameInput]:
        """Processes a BGR frame and returns an annotated frame and inputs to be executed.

        Annotate the frame and detect the tongue using YOLO and eyes using Haar cascades.

        Arguments:
        - `frame`: cv2.Mat -- A 24-bit BGR image

        Returns:
        - A tuple of `(cv2.Mat, FrameInput)`, referring to an annotated frame and the corresponding inputs to be executed.
        """
        frame_input = FrameInput(is_left_eye_closed=False, is_right_eye_closed=False)

        # Function to calculate Eye Aspect Ratio (EAR)
        def calculate_EAR(eye):
            y1 = dist.euclidean(eye[1], eye[5])  # Vertical distance
            y2 = dist.euclidean(eye[2], eye[4])  # Vertical distance
            x1 = dist.euclidean(eye[0], eye[3])  # Horizontal distance
            ear = (y1 + y2) / x1
            return ear

        # Eye landmarks
        (L_start, L_end) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
        (R_start, R_end) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

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
            if left_ear < self.EYE_AR_THRESH:
                self.left_eye_counter += 1
            else:
                self.left_eye_counter = 0

            # Check if the right eye is closed
            if right_ear < self.EYE_AR_THRESH:
                self.right_eye_counter += 1
            else:
                self.right_eye_counter = 0

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

            if self.left_eye_counter >= self.EYE_AR_CONSEC_FRAMES:
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

            if self.right_eye_counter >= self.EYE_AR_CONSEC_FRAMES:
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
                frame_input.is_right_eye_closed = False

        # Load Haar cascades
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"  # type: ignore
        )
        eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_eye.xml"  # type: ignore
        )

        (frame_h, frame_w, _) = frame.shape

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        annotated_frame = frame

        for face_x, face_y, face_w, face_h in faces:
            # Calculate center of the face
            face_center_x = face_x + face_w // 2
            face_center_y = face_y + face_h // 2
            frame_input.cursor_pos = (face_center_x / frame_w, face_center_y / frame_h)

            # Display the center of the face
            cv2.circle(
                annotated_frame, (face_center_x, face_center_y), 5, (0, 255, 0), -1
            )  # Green dot at the center
            cv2.putText(
                annotated_frame,
                f"Center: ({face_center_x}, {face_center_y})",
                (face_center_x + 10, face_center_y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )

            cv2.rectangle(
                annotated_frame,
                (face_x, face_y),
                (face_x + face_w, face_y + face_h),
                color=(0, 255, 0),
                thickness=2,
            )

            # Extend face shape down to include tongue
            face = annotated_frame[
                face_y : face_y + int(face_h * 1.2), face_x : face_x + face_w
            ]
            gray_face = gray[face_y : face_y + face_h, face_x : face_x + face_w]

            # Detect eyes using Haar cascades
            eyes = eye_cascade.detectMultiScale(gray_face, 1.1, minNeighbors=7)
            left_eye_detected = False
            right_eye_detected = False

            for ex, ey, ew, eh in eyes:
                # too small of an eye width, must be an error
                if ew <= face_w * 0.2:
                    continue

                eye_center_x = face_x + ex + ew // 2
                cv2.rectangle(
                    annotated_frame,
                    (face_x + ex, face_y + ey),
                    (face_x + ex + ew, face_y + ey + eh),
                    color=(255, 0, 0),
                    thickness=2,
                )
                cv2.putText(
                    annotated_frame,
                    "Eye",
                    (face_x + ex, face_y + ey - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 0, 0),
                    2,
                )

                # Classify as left or right eye
                if eye_center_x < face_center_x:
                    left_eye_detected = True
                else:
                    right_eye_detected = True

            # Display closed eye status if no eye is detected
            '''if not left_eye_detected:
                cv2.putText(
                    annotated_frame,
                    "Left Eye Closed",
                    (face_x, face_y - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 255),
                    2,
                )
                frame_input.is_left_eye_closed = True
            if not right_eye_detected:
                cv2.putText(
                    annotated_frame,
                    "Right Eye Closed",
                    (face_x + face_w // 2, face_y - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 255),
                    2,
                )
                frame_input.is_right_eye_closed = True'''

            # Perform YOLO inference to detect the tongue
            results = self.yolo_model.predict(source=face, conf=0.5, save=False)

            assert results[0].boxes is not None

            for box in results[0].boxes:  # Iterate through detections
                cls = int(box.cls[0])  # Class index
                if (
                    cls == 0
                ):  # Assuming class 0 corresponds to "tongue" in your YOLO model
                    x1, y1, x2, y2 = map(
                        int, box.xyxy[0]
                    )  # Coordinates of the bounding box
                    if y1 < face_h * 0.6:
                        continue
                    cv2.rectangle(
                        annotated_frame,
                        (face_x + x1, face_y + y1),
                        (face_x + x2, face_y + y2),
                        color=(0, 0, 255),
                        thickness=2,
                    )
                    cv2.putText(
                        annotated_frame,
                        "Tongue",
                        (face_x + x1, face_y + y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 0, 255),
                        2,
                    )
                    frame_input.is_tongue_down = (y2 - y1) / (x2 - x1) > 2 / 3

        return (annotated_frame, frame_input)
