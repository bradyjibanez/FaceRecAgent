from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.http import StreamingHttpResponse
import os
from django.views.decorators import gzip
from django.views.decorators.csrf import csrf_exempt
import cv2
import numpy as np
from .VideoCamera import VideoCamera
# import face_recognition
# from .LA.AIProject.faceRec.faceRec import testEncounter, processMemoryEncodings, produceEncounterEncodings
# from imutils import paths

tester = None
im = []
# knownEncodings, knownNames = processMemoryEncodings(list(paths.list_images("/home/joseph/Desktop/aila/AIProject/memory/")))
# data, encounterEncodings, encounters, correspondImage = produceEncounterEncodings(list(paths.list_images("/home/joseph/Desktop/aila/AIProject/unknown/")), knownEncodings, knownNames)
# remembered = os.listdir('/home/joseph/Desktop/aila/AIProject/memory/')

# Create your views here.
def index(request):
    return render(request, 'stream/index.html', {
        'title': "Face to Face",
    })

@csrf_exempt
def resp_string(request):
    global tester
    if request.method == 'POST':
        print(request.POST['name'])
        tester = request.POST['name']
        if len(tester) < 1:
            tester = None
        return HttpResponse(request.POST['name'])
    elif request.method == 'GET':
        response = JsonResponse({
                'string': tester,
            })

        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Max-Age"] = "1000"
        response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
        return response

     

@gzip.gzip_page
def livefe(request):
    global im
    if request.method == 'GET':
        try:
            return StreamingHttpResponse(gen(None),content_type="multipart/x-mixed-replace;boundary=frame")
        except HttpResponseServerError as e:
            print(e)
    
    
@csrf_exempt
def receive_image(request):
    global im#, knownEncodings, knownNames, data, encounterEncodings, encounters, correspondImage
    if request.method == 'POST':
       
        if request.FILES.get("photo", None) is not None:

            image = request.FILES['photo'].read()
            # image = cv2.imdecode(np.fromstring(image, dtype=np.uint8), cv2.IMREAD_COLOR)
            # image, names = testEncounter(image,remembered, knownEncodings, encounterEncodings, encounters, data, correspondImage)
            # im = cv2.imencode('.jpeg',image)[1].tobytes()
            im = image
        return HttpResponse(tester)

    
def gen(camera):
    global im
    while True:
        # frame = camera.get_frame()
        frame = im
        yield(b'--frame\r\n'
        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

