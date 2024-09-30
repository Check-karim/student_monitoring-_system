import cv2
from pyzbar import pyzbar


# Function to decode QR codes from the frame
def decode_qr_codes(frame):
    # Detect and decode the QR codes in the frame
    qr_codes = pyzbar.decode(frame)

    for qr_code in qr_codes:
        # Extract the bounding box location of the QR code and draw a rectangle around it
        (x, y, w, h) = qr_code.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # The QR code data is a bytes object, so we decode it to a string
        qr_code_data = qr_code.data.decode("utf-8")
        qr_code_type = qr_code.type

        # Draw the QR code data and type on the frame
        text = f"{qr_code_data} ({qr_code_type})"
        cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        print(f"Detected QR code: {qr_code_data} | Type: {qr_code_type}")

    return frame


# Main function to open the camera and start scanning QR codes
def main():
    # Start capturing video from the camera
    cap = cv2.VideoCapture(0)

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        if not ret:
            print("Failed to grab frame")
            break

        # Decode QR codes in the frame
        frame = decode_qr_codes(frame)

        # Display the frame with highlighted QR codes
        cv2.imshow('QR Code Scanner', frame)

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and close windows
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
