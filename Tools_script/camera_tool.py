import sys

try:
    import cv2
except ImportError:
    cv2 = None


def main():
    print("Starting camera...")
    if cv2 is None:
        print("Error: OpenCV is not installed. Install it with 'pip install opencv-python'.")
        return
    
    # Initialize the camera (0 is usually the default webcam)
    cap = cv2.VideoCapture(0)
    
    # Check if camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera")
        sys.exit(1)
    
    print("Camera started successfully!")
    print("ENJOY YOURSELF !")
    
    while True:
        # Read frame from camera
        ret, frame = cap.read()
        
        if not ret:
            print("Error: Can't receive frame")
            break
        
        # Display the frame
        cv2.imshow('Camera', frame)
        
        # Wait for key press
        key = cv2.waitKey(1) & 0xFF
        
        # Press 'q' to quit
        if key == ord('q'):
            print("Closing camera...")
            break
        
        # Press 's' to save photo
        elif key == ord('s'):
            filename = f"photo_{cv2.getTickCount()}.jpg"
            cv2.imwrite(filename, frame)
            print(f"Photo saved as {filename}")
    
    # Release the camera and close windows
    cap.release()
    cv2.destroyAllWindows()
    print("Camera closed")

if __name__ == "__main__":
    main()
