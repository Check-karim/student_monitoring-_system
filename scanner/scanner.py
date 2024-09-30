import cv2
from pyzbar import pyzbar
import requests
import webbrowser
import time  # Import time to add a delay before closing

# Function to decode QR codes from the frame
def decode_qr_codes(frame):
    qr_codes = pyzbar.decode(frame)

    for qr_code in qr_codes:
        (x, y, w, h) = qr_code.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        qr_code_data = qr_code.data.decode("utf-8")
        qr_code_type = qr_code.type

        text = f"{qr_code_data} ({qr_code_type})"
        cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        print(f"Detected QR code: {qr_code_data} | Type: {qr_code_type}")

        # Send the QR code data to the Flask route
        try:
            response = requests.post('http://127.0.0.1:5000/barcode_login', json={'barcode': qr_code_data})
            response_json = response.json()
            if response_json.get('success'):
                redirect_url = response_json.get('redirect_url')
                if redirect_url:  # Check if the URL is not None
                    print(f"QR code sent successfully. Redirecting to {redirect_url}")

                    # Open the redirect URL in the browser
                    webbrowser.open(redirect_url)

                    # Adding a delay to ensure the browser opens before closing
                    time.sleep(2)
                else:
                    error_message = "Redirect URL is None. Cannot open the browser."
                    print(error_message)
                    cv2.putText(frame, error_message, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                return True  # Indicate that the QR code was processed successfully and we can close the scanner
            else:
                error_message = "Failed to find student."
                print(error_message)
                cv2.putText(frame, error_message, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        except Exception as e:
            error_message = f"Error: {str(e)}"
            print(error_message)
            cv2.putText(frame, error_message, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    return False

def main():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Failed to grab frame")
            break

        # Process the frame for QR code detection
        if decode_qr_codes(frame):
            # If a QR code was successfully processed, close the scanner
            break

        # Display the video feed with detected QR codes (if any)
        cv2.imshow('QR Code Scanner', frame)

        # Exit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
