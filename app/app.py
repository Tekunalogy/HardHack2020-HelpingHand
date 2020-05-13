import sys
import time
import RPi.GPIO as GPIO

# Import alwaysAI computer vision and video processing tools
import cv2
import edgeiq

# Object centering settings
FRAME_WIDTH_CENTER = 1280/2
ERROR_MARGIN = 40
LEFT_ERROR = FRAME_WIDTH_CENTER - ERROR_MARGIN
RIGHTERROR = FRAME_WIDTH_CENTER + ERROR_MARGIN

# rpi motor ports
LEFT_PORT = 22
RIGHT_PORT = 23

# Camera Frame Settings
FRAME_A_RATE = 2
LAG_COMPENSATION = 0

debug_On = true


def image_Centering(resultList):
    if(len(resultList) > 0):
        selectItem = resultObj[0]
        resultBox = selectItem.box

        if(resultBox.center > RIGHT_PORT):
            alert_Motor(RIGHT_PORT)
        
        elif(resultBox.center < LEFT_ERROR):
            alert_Motor(LEFT_PORT)


def alert_Motor(port):
    GPIO.output(port, GPIO.HIGH)
    time.sleep(FRAME_A_RATE - LAG_COMPENSATION)
    GPIO.output(port, GPIO.LOW)


def main():
    # Set up object detection API
    obj_detect = edgeiq.ObjectDetection(
            "alwaysai/mobilenet_ssd")
    obj_detect.load(engine=edgeiq.Engine.DNN)

    # Set up rpi ports
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(LEFT_PORT, GPIO.OUT)
    GPIO.setup(RIGHT_PORT, GPIO.OUT)

    fps = edgeiq.FPS()

    try:
        with edgeiq.WebcamVideoStream(cam=0) as video_stream, \
                edgeiq.Streamer() as streamer:
            # Allow Webcam to warm up
            time.sleep(2.0)
            fps.start()

            # loop detection
            while True:
                frame = video_stream.read()
                results = obj_detect.detect_objects(frame, confidence_level=.8) # Maybe filter the result to bottles or bags for demo?
                
                image_Centering(results.predictions)

                # Debug information
                if(debug_On):
                    frame = edgeiq.markup_image(
                            frame, results.predictions, colors=obj_detect.colors)

                    # Generate text to display on streamer
                    text = ["Model: {}".format(obj_detect.model_id)]
                    text.append(
                            "Inference time: {:1.3f} s".format(results.duration))
                    text.append("Objects:")

                    for prediction in results.predictions:
                        text.append("{}: {:2.2f}%".format(
                            prediction.label, prediction.confidence * 100))

                streamer.send_data(frame, text)

                fps.update()

                time.sleep(FRAME_A_RATE)

                if streamer.check_exit():
                    break

    finally:
        fps.stop()
        print("elapsed time: {:.2f}".format(fps.get_elapsed_seconds()))
        print("approx. FPS: {:.2f}".format(fps.compute_fps()))


if __name__ == "__main__":
    main()
