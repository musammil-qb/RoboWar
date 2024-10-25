from ultralytics import YOLO
import os, sys

model = YOLO("best.pt")

image = sys.argv[1]

result = model(image,save=True)
