import cv2
import numpy as np
import pyautogui
import time
def check_white_through(gray, x_front, x_back, roi):
    ret, thresholded = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        
        area = cv2.contourArea(contour)
        if area > 100:
            x, y, w, h = cv2.boundingRect(contour)
            middle_x = x + (w // 2)
            middle_y = y + (h // 2)
            dot_x = (x+w)-3
            cv2.drawContours(roi, [contour], -1, (0, 255, 0), 2)
            cv2.circle(roi, (dot_x, middle_y), 2, (255, 0, 0), 2)
            
            if dot_x > x_front and dot_x < x_back:
                global count_time
                cv2.drawContours(roi, [contour], -1, (255, 255, 255), 2)
                cv2.circle(roi, (dot_x, middle_y), 2, (0, 0, 255), 2)
                pyautogui.press('e')
                print(f"Count Time: {count_time}")
                count_time = 0
                time.sleep(1)
            else :
                cv2.drawContours(roi, [contour], -1, (0, 255, 0), 2)
                cv2.circle(roi, (dot_x, middle_y), 2, (255, 0, 0), 2)

def process_color_mask(hsv, lower, upper, color_name, roi):
    if color_name == 'red':
        mask = cv2.bitwise_or(cv2.inRange(hsv, red_lower1, red_upper1),
                         cv2.inRange(hsv, red_lower2, red_upper2))
    else:
        mask = cv2.inRange(hsv, lower, upper)

    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    counter = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        if 700 < area < 2000:
            # print(f"{color_name} Contour area: {area}")
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(roi, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.line(roi, (x, 0), (x, 89), (0,0,255),2)
            cv2.line(roi, (x+w, 0), (x+w, 89), (0,0,255),2)
            check_white_through(gray, x, x+w, roi)
            counter += 1

    return counter

x1, y1, x2, y2 = 800, 876, 1120, 965

while True:

    screenshot = pyautogui.screenshot()
    frame = np.array(screenshot)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    cropped_frame = frame[y1:y2, x1:x2].copy()
    roi = cropped_frame.copy()
    hsv = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2GRAY)

    blue_lower = np.array([90, 50, 50])
    blue_upper = np.array([130, 255, 255])

    green_lower = np.array([35, 50, 50])
    green_upper = np.array([85, 255, 255])

    pink_lower = np.array([150, 50, 50])
    pink_upper = np.array([170, 255, 255])

    red_lower1 = np.array([0, 50, 50])
    red_upper1 = np.array([10, 255, 255])

    red_lower2 = np.array([170, 100, 50])
    red_upper2 = np.array([180, 255, 255])

    # Create masks for each color range
    blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
    green_mask = cv2.inRange(hsv, green_lower, green_upper)
    pink_mask = cv2.inRange(hsv, pink_lower, pink_upper)
    red_mask = cv2.bitwise_or(cv2.inRange(hsv, red_lower1, red_upper1),
                            cv2.inRange(hsv, red_lower2, red_upper2))

    # Combine the masks
    combined_mask = cv2.bitwise_or(blue_mask, cv2.bitwise_or(green_mask, cv2.bitwise_or(pink_mask, red_mask)))

    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # Get contours

    counter = 0

    for contour in contours:
        area = cv2.contourArea(contour)
        if 350 < area < 1500:
            # print(f"Contour area: {area}")
            
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])

                # Determine the color of the centroid point
                hsv_color = hsv[cY, cX]
                if blue_lower[0] <= hsv_color[0] <= blue_upper[0]:
                    color = "blue"
                    process_color_mask(hsv, blue_lower, blue_upper, color, roi)
                elif green_lower[0] <= hsv_color[0] <= green_upper[0]:
                    color = "green"
                    process_color_mask(hsv, green_lower, green_upper, color, roi)
                elif pink_lower[0] <= hsv_color[0] <= pink_upper[0]:
                    color = "pink"
                    process_color_mask(hsv, pink_lower, pink_upper, color, roi)
                elif (red_lower1[0] <= hsv_color[0] <= red_upper1[0]) or (red_lower2[0] <= hsv_color[0] <= red_upper2[0]):
                    color = "red"
                    process_color_mask(hsv, red_lower1, red_upper1, color, roi)
                else:
                    color = "unknown"


                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(roi, (x, y), (x + w, y + h), (255, 0, 0), 2)
                counter += 1


    cv2.putText(roi, str(count_time), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), 1)
    cv2.imshow('Bot', roi)
    # cv2.imshow('Real', cropped_frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and destroy all windows
cv2.destroyAllWindows()
