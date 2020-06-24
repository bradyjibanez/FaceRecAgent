## Face Rec Detection/Recognition Driver
Household guest detection multiagent system 
----------------------------------------------------------------------------------------------------------

The purpose of this multiagent facilitated application is to allow for a learning AI system capable of interaction with a limited visulaized environment (a front door area). The first agent, the eye node, recognizes faces through facial detection as implemented through the use of openCV and facial_recognition, a Python library created by ageitgy.

The eye node agent relays detected face images to the brain node, located on a more computationally capable device than the eye node. The brain node generates encodings of memorized faces, the new encounter face, and compares the new encounter to all of the memory face encodings in order to recognize possible known guests within a new encounter. 

The brain node utilizes facial_recognition as well, but to a more extensive degree, and implements HOG facial analysis (a 128 bit point array generating algorithm for for all qualifiable points within an encounter image) in order to generate matches. If matches are not found, the brain node will request further information from the user (a definition of the guest in order to save them to memory for further encounters). Should the user respond, the image is added, as well as subsequent matches. Should the user not respond, the image is discarded. 

The learning aspect of the brain agent lives within the faceRec directory, and can be observed through the memory and unknown folders where images of remembered guests and unknowns encounters are maintained, respectively. 

A django front end is implemented to allow for user interfacing with this multi agent AI system. 
