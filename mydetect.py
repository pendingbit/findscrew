import cv2
import numpy as np
from threading import Thread
import time
import os

print(cv2.__version__)

detectthread = None
detect_clean = False
max_ok = 4
max_ng = 8
shootflag = False
shootindex = 0
shootstring = ''
shootroistring = ''
result = False
detectROI = cv2.imread("./logo.jpg")
videoIndex=0
dispW=640
dispH=480
s_x=round(dispW/4)
s_y=round(dispH/4)
e_x=round(dispW - dispW/4)
e_y=round(dispH - dispH/4)
flag=1
print(s_x,s_y,e_x,e_y)
camSet =f"v4l2src device=/dev/video{videoIndex} io-mode=2 " \
        f"! image/jpeg, width={dispW}, height={dispH}, framerate=30/1, format=MJPG " \
        f"! nvv4l2decoder mjpeg=1 " \
        f"! nvvidconv " \
        f"! video/x-raw, format=BGRx " \
        f"! videoconvert " \
        f"! video/x-raw, format=BGR " \
        f"! appsink drop=1"

def nothing(x):
    pass

def click(event,x,y,flags,params):
    global s_x
    global s_y
    global e_x
    global e_y
    global flag
    if event==cv2.EVENT_LBUTTONDOWN:
        print('left down: ',x,y)
        s_x=x
        s_y=y
        flag=0
    if event==cv2.EVENT_LBUTTONUP:
        print('left up: ',x,y)
        e_x=x
        e_y=y
        flag=1

cam=cv2.VideoCapture(camSet, cv2.CAP_GSTREAMER)

cv2.namedWindow('Detect Config',cv2.WINDOW_NORMAL)

cv2.setWindowProperty('Detect Config', cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

cv2.setMouseCallback('Detect Config', click)
#cv2.createTrackbar('Median Filter','Detect Config',17,255,nothing)
#cv2.createTrackbar('Threshold','Detect Config',100,255,nothing)
#cv2.createTrackbar('螺纹长度','Detect Config',50,255,nothing)
#cv2.createTrackbar('螺纹数量', 'Detect Config',2,10,nothing)

    
def detect_task():
    global cam
    global shootflag
    global shootstring
    global result,detectROI
    global s_x,s_y,e_x,e_y,flag,detect_clean
    timestamp=time.time()
    dt=1
    dtavg=1
    fps=1
    ok_cnt = 0
    ng_cnt = 0

    while True:
        count = 0
        frameFailCount = 0
        #print("mydetect is going")

        #test with screw.jpeg instead of real camera
        #frame =cv2.imread('screw.jpeg')

        #read frame from webCam 
        ret, frame = cam.read()
        

        while frame is None:
            result = False
            print("read frame is error,stop!")
            cam.release()
            time.sleep(.1)
            cam=cv2.VideoCapture(camSet, cv2.CAP_GSTREAMER)
            ret, frame = cam.read()
            print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
            print("cam init again",frameFailCount)
            frameFailCount += 1
            if frameFailCount > 100:
                detect_clean = True
                break

        if detect_clean == True:
            break

#######################################
        MedianFilter = 15
        #MedianFilter = cv2.getTrackbarPos('Median Filter','Detect Config')
        #if MedianFilter%2 == 0:
        #    MedianFilter += 1
######################################
        Threshold = 95
        #Threshold = cv2.getTrackbarPos('Threshold','Detect Config')
######################################
        ContoursLength = 50
        #ContoursLength = cv2.getTrackbarPos('螺纹长度','Detect Config')
######################################
        TargetNumber = 2
        #TargetNumber = cv2.getTrackbarPos('螺纹数量','Detect Config')
######################################
        
        
        try:
            if flag==1:
                if s_x>e_x:
                    temp=s_x
                    s_x=e_x
                    e_x=temp
                if s_y>e_y:
                    temp=s_y
                    s_y=e_y
                    e_y=temp
                if ((e_x-s_x)*(e_y-s_y)) < (dispH*dispW/20):
                    s_x=round(dispW/4)
                    s_y=round(dispH/4)
                    e_x=round(dispW - dispW/4)
                    e_y=round(dispH - dispH/4)
                if s_x < 0:
                    s_x = 0
                if s_y < 0:
                    s_y = 0
                if e_x > 639:
                    e_x = 639
                if e_y > 479:
                    e_y = 479

                roi=frame[s_y:e_y,s_x:e_x]       

                #draw a rectangle, the parameters are(frame, one coner, the other coner, BGR, line weight)
                cv2.rectangle(frame,(s_x,s_y),(e_x,e_y),(0,0,255),2)

                #medianBlur filter frame and show it as 'filter cam'
                FrameFilter = cv2.medianBlur(roi, MedianFilter)
                FrameFilter = cv2.absdiff(FrameFilter, roi)
                #cv2.imshow('filter cam', FrameFilter)
                #cv2.moveWindow('filter cam',640 ,50)

                #convert BGR to GRAY and show it as 'gray'
                gray=cv2.cvtColor(FrameFilter, cv2.COLOR_BGR2GRAY)
                #cv2.imshow('gray', gray)
                #cv2.moveWindow('gray', 0, 500)

                #threshold 2 value and show it as 'thres'
                _,thres=cv2.threshold(gray,Threshold,255,cv2.THRESH_BINARY)
                #cv2.imshow('thres',thres)
                #cv2.moveWindow('thres',640,500)

                #find contours and draw it on orignal frame
                contours,hierarchy = cv2.findContours(thres, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                for i in range(0, len(contours)):
                    length = cv2.arcLength(contours[i], True)
                    if length > ContoursLength:
                        count += 1
                        #cv2.drawContours(roi, contours[i], -1, (0,0,255), 2)

        except:
            print("error occur")

        dt=time.time()-timestamp
        dtavg=dtavg*0.9+dt*0.1
        fps=1/dtavg
        timestamp=time.time()
        cv2.putText(frame,str(round(fps,1))+' fps ',(550,460),cv2.FONT_HERSHEY_DUPLEX, 0.6, (0,0,255), 1)

        if count > TargetNumber:
            ok_cnt += 1
            if ok_cnt > max_ok:
                ok_cnt =  max_ok
            if ng_cnt > 0:
                ng_cnt -= 1
        else:
            ng_cnt += 1
            if ng_cnt > max_ng:
                ng_cnt = max_ng
            if ok_cnt > 0:
                ok_cnt -= 1

        if ok_cnt == max_ok:
            cv2.putText(frame, 'OK' , (20,50), cv2.FONT_HERSHEY_DUPLEX, 2, (0,255,0), 3)
            cv2.putText(frame,'current/target : '+str(count)+'/'+str(TargetNumber),(0,460),cv2.FONT_HERSHEY_DUPLEX,0.6,(0,255,0),1)
            result = True
        elif ng_cnt == max_ng:
            cv2.putText(frame, 'NG' , (20,50), cv2.FONT_HERSHEY_DUPLEX, 2, (0,0,255), 3)
            cv2.putText(frame,'current/target : '+str(count)+'/'+str(TargetNumber),(0,460),cv2.FONT_HERSHEY_DUPLEX,0.6,(0,0,255),1)
            result = False
        else:
            if result == True:
                cv2.putText(frame, 'OK' , (20,50), cv2.FONT_HERSHEY_DUPLEX, 2, (0,255,0), 3)
                cv2.putText(frame,'current/target : '+str(count)+'/'+str(TargetNumber),(0,460),cv2.FONT_HERSHEY_DUPLEX,0.6,(0,255,0),1)
            else:
                cv2.putText(frame, 'NG' , (20,50), cv2.FONT_HERSHEY_DUPLEX, 2, (0,0,255), 3)
                cv2.putText(frame,'current/target : '+str(count)+'/'+str(TargetNumber),(0,460),cv2.FONT_HERSHEY_DUPLEX,0.6,(0,0,255),1)
 
        #show oritnal cam
        cv2.imshow('Detect Config', frame)
        #cv2.moveWindow('Detect Config', 0,50)

        if shootflag == True:
            cv2.imwrite(shootstring,frame)
            #cv2.imwrite(shootroistring, roi)
            shootflag = False

        if cv2.waitKey(1)==ord('q'):
            break


    cam.release()
    cv2.destroyAllWindows()

    detect_clean = True   



def detect_get_result():
    return result

def main():
    global detectthread
    detectthread = Thread(target=detect_task)
    detectthread.daemon = True
    detectthread.start()

if __name__ == '__main__':
    main()
