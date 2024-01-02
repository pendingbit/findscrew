import myio
import mydetect
import time
import argparse

print("my screw detect start")

cnt_total = 0
cnt_ok = 0
cnt_ng = 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='指定保存照片及日志的路径')
    parser.add_argument('logpath', type=str,help='指定路径路径')
    args = parser.parse_args()
    logpath = args.logpath

    myio.main()
    mydetect.main()
    count = 0
    result = False

    while True:
        if mydetect.detect_clean:
            break

        if myio.io_get_event()==True and count==0:
            cnt_total += 1
            #tigger detection , delay 0.5s for detection
            time.sleep(0.8)
            result = mydetect.detect_get_result()
            if result == True:
                cnt_ok += 1
                mydetect.shootstring = logpath+'OK_'+str(cnt_total)+'.jpeg'
            else:
                cnt_ng += 1
                mydetect.shootstring = logpath+'NG_'+str(cnt_total)+'.jpeg'
            
            mydetect.shootroistring = logpath+'ROI_'+str(cnt_total)+'.jpeg'
            mydetect.shootflag = True
            count = 50
            print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
            print("OK数量: ",cnt_ok,"   NG数量: ",cnt_ng)

        if count > 0:
            count -= 1
            if True == result:
                myio.io_set_status(1)
            else:
                myio.io_set_status(0)
        else:
            myio.io_set_status(0)

        time.sleep(.05)
    
    print("ready to clean")
    myio.io_clean = True
    mydetect.detectthread.join()
    myio.iothread.join()
    print("the application is done")

