import logging
import cv2
from matplotlib.pyplot import annotate
from mugshot.cv._cv_detection import CVDetection


def test_cv():
    """A simplified setup to test CV functionalities without a full GUI."""

    cv_detection = CVDetection()

    # Initialize webcam (use 0 for default webcam, otherwise replace with other camera indexes)
    cap = cv2.VideoCapture(0)

    # Check that the webcam is opened successfully
    if not cap.isOpened():
        logging.error("Video capture is not opened.")
        return

    print("Press 'q' to quit the application.")

    while True:
        ret, frame = cap.read()

        if not ret:
            logging.error("Failed to read frame.")
            return

        frame = cv2.flip(frame, 1)

        (annotated_frame, _) = cv_detection.process_frame(frame)

        # Display the annotated frame
        cv2.imshow("Inference", annotated_frame)

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Release webcam resource and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()
