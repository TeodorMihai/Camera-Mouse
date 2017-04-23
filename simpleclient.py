#!/usr/bin/env python3.4

import gi
gi.require_version('Gtk', '2.0')
from gi.repository import Gtk
from gi.repository import Gdk
from clientstate import ClientState, MOUSE_UP, MOUSE_DOWN
import socket
import threading
import time
import random

import numpy as np
import cv2
from collections import deque

cap = cv2.VideoCapture(0)

greenLower = (1, 20, 122)
greenUpper = (6, 255, 255)

pts = deque(maxlen=50)

HOST = "localhost"
PORT = 10000
SERVER_STATE_UPDATE_FREQUENCY_SECONDS = 0.01
     
ptsYellow = deque(maxlen=50)
ptsRed = deque(maxlen=50)

def nothing(x):
    pass
 
#cv2.namedWindow('image')
#cv2.createTrackbar('UR','image',0,255,nothing)
#cv2.createTrackbar('UG','image',0,255,nothing)
#cv2.createTrackbar('UB','image',0,255,nothing)
#cv2.createTrackbar('LR','image',0,255,nothing)
#cv2.createTrackbar('LG','image',0,255,nothing)
#cv2.createTrackbar('LB','image',0,255,nothing)
#redUpper = (6,255,255)
#redLower = (1,20,120)


class Client(threading.Thread):
  def __init__(self):
    global HOST, PORT
    super(Client, self).__init__()
    self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.conn.connect((HOST, PORT))
    self.state = ClientState(0, 0, MOUSE_UP)

  def run(self):
    global SERVER_STATE_UPDATE_FREQUENCY_SECONDS
    self.state.sendTeamName(self.conn, "test-client")
    while True:
      time.sleep(SERVER_STATE_UPDATE_FREQUENCY_SECONDS)
      self.state.send(self.conn)

class GtkGUI:

  def motion_notify_event(widget, event):
    return True

  def destroy(self, widget, data=None):
    Gtk.main_quit()

  def motion_cb(self, widget, event):
    self.client.state.setState(int(event.x),
                               int(event.y),
                               MOUSE_DOWN if event.state else MOUSE_UP)

  def __init__(self):
    self.client = Client()
    self.client.start()

    self.window = Gtk.Window()
    self.window.connect("destroy", self.destroy)
    self.window.set_border_width(0)
    self.window.resize(640, 480)

    self.area = Gtk.DrawingArea()
    #self.area.connect("motion-notify-event", self.motion_cb)

    redUpper = (7,255,255)
    redLower = (1,100,122)
    yellowUpper = (26,255,255)
    yellowLower = (15,203,138)
    nrcadre = 10
    pressed = 0
     
    deque_size = 10
    yel_deque = deque()
    yellow_in = 0
    for i in range(deque_size):
      yel_deque.append(0)
    


    d = deque(maxlen=3)

    while(True):
      ret, frame = cap.read()
      # redUpper = (cv2.getTrackbarPos('UR','image'), cv2.getTrackbarPos('UG','image'), cv2.getTrackbarPos('UB','image'))
      # redLower = (cv2.getTrackbarPos('LR','image'), cv2.getTrackbarPos('LG','image'), cv2.getTrackbarPos('LB','image'))
   
      # Our operations on the frame come here
      gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
      frame = cv2.flip(frame, flipCode=1)
      blurred = cv2.GaussianBlur(frame, (11, 11), 0)
      hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
   
      maskYellow = cv2.inRange(hsv, yellowLower, yellowUpper)
      maskYellow = cv2.erode(maskYellow, None, iterations=2)
      maskYellow = cv2.dilate(maskYellow, None, iterations=2)
   
      maskRed = cv2.inRange(hsv, redLower, redUpper)
      maskRed = cv2.erode(maskRed, None, iterations=2)
      maskRed = cv2.dilate(maskRed, None, iterations=2)
   
      cntsYellow = cv2.findContours(maskYellow.copy(), cv2.RETR_EXTERNAL,
                              cv2.CHAIN_APPROX_SIMPLE)[-2]
   
      cntsRed = cv2.findContours(maskRed.copy(), cv2.RETR_EXTERNAL,
                              cv2.CHAIN_APPROX_SIMPLE)[-2]
   
      center = None
  #portiunea pentru galben
      if len(cntsYellow) > 0:
          # find the largest contour in the mask, then use
          # it to compute the minimum enclosing circle and
          # centroid
          c = max(cntsYellow, key=cv2.contourArea)
          ((x, y), radius) = cv2.minEnclosingCircle(c)
          M = cv2.moments(c)
          center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
   
          area = M["m00"]
   
          # only proceed if the radius meets a minimum size
          if radius > 10:
              # draw the circle and centroid on the frame,
              # then update the list of tracked points
              cv2.circle(frame, (int(x), int(y)), int(radius),
                         (0, 255, 255), 2)
              cv2.circle(frame, center, 5, (0, 0, 255), -1)

              pressed = 1
              # update the points queue

   
          # if(len(ptsYellow)<1):
          #     ptsYellow.appendleft(center)
          else:
            pressed = 0
      else:
        pressed = 0
   
      #print (yellow_in)
   
      print("pressed: " + str(pressed))
   
   
      # if(len(ptsYellow)>0 and nrcadre>15 ):
      #     nrcadre=0
      #     pressed = 1-pressed
      #     ptsYellow.pop()
      #     # ptsYellow = deque(maxlen=50)
      # else:
      #     nrcadre+=1
      # print("pressed: "+str(pressed))
   
      # for i in range(1, len(ptsYellow)):
          # if either of the tracked points are None, ignore
          # them
          # if ptsYellow[i - 1] is None or ptsYellow[i] is None:
          #     continue
   
          # otherwise, compute the thickness of the line and
          # draw the connecting lines
          # thickness = int(np.sqrt(50 / float(i + 1)) * 2.5)
          # cv2.line(frame, ptsYellow[i - 1], ptsYellow[i], (255, 0, 0), thickness)
   
  #portiunea pentru red
      if len(cntsRed) > 0:
          # find the largest contour in the mask, then use
          # it to compute the minimum enclosing circle and
          # centroid
          c = max(cntsRed, key=cv2.contourArea)
          ((x, y), radius) = cv2.minEnclosingCircle(c)
          M = cv2.moments(c)
          center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
   
          area = M["m00"]
   
          # only proceed if the radius meets a minimum size

          if radius > 10:
              # draw the circle and centroid on the frame,
              # then update the list of tracked points


              rez = 2*np.array(center)
              if len(d) > 2:
                for tup in d:
                  rez += np.array(tup)
                rez /= (len(d)+2)
                rez = rez.astype('int')
                center = tuple(rez)

              d.append(center)

              cv2.circle(frame, (int(x), int(y)), int(radius),
                         (0, 255, 255), 2)
              cv2.circle(frame, center, 5, (0, 0, 255), -1)
   
              # update the points queue

      ptsRed.appendleft(center)
   
      for i in range(1, len(ptsRed)):
          # if either of the tracked points are None, ignore
          # them
          if ptsRed[i - 1] is None or ptsRed[i] is None:
              continue
   
          # otherwise, compute the thickness of the line and
          # draw the connecting lines
          thickness = int(np.sqrt(50 / float(i + 1)) * 2.5)
          cv2.line(frame, ptsRed[i - 1], ptsRed[i], (0, 0, 255), thickness)
   
      # Display the resulting frame

      if(center != None):
        self.client.state.setState(center[0],
                               center[1],
                               pressed) #else MOUSE_UP
      time.sleep(0.01)
      cv2.imshow('frame', frame)
      if cv2.waitKey(1) & 0xFF == ord('q'):
          break
   
    cap.release()
    cv2.destroyAllWindows()


    self.window.add(self.area)
    self.area.show()
    self.window.show()

  def main(self):
    Gtk.main()

if __name__ == "__main__":
  GtkGUI().main()
