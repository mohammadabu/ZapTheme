from odoo import api, models, exceptions
import base64
import face_recognition as fr
import os
import cv2
import face_recognition
import numpy as np
from time import sleep
from datetime import datetime
from os import listdir
from odoo.exceptions import UserError
from time import sleep

class CheckWebCamEmployee(models.Model):
    _inherit = "hr.employee"

    @classmethod
    def get_encoded_faces(cls):
        """
        looks through the faces folder and encodes all
        the faces

        :return: dict of (name, image encoded)
        """
        encoded = {}

        for dirpath, dnames, fnames in os.walk("local_addons/web_widget_image_webcam/models/faces"):
            for f in fnames:
                if f.endswith(".jpg") or f.endswith(".png"):
                    face = fr.load_image_file("local_addons/web_widget_image_webcam/models/faces/" + f)
                    encoding = fr.face_encodings(face)[0]
                    encoded[f.split(".")[0]] = encoding

        return encoded

    @classmethod
    def classify_face(cls, *image_attendance, **name_user):
        """
        will find all of the faces in a given image and label
        them if it knows what they are

        :param im: str of file path
        :return: list of face names
        """

        # ---
        """
            Convert image after taking snapshot to image and 
            Save into folder
        """
        imgdata = base64.b64decode(name_user['image_attendance'])
        filename = f"local_addons/web_widget_image_webcam/static/src/img/{name_user['name_user']}/{name_user['name_user']}.jpg"
        with open(filename, 'wb') as f:
            f.write(imgdata)

        # ---
        """
            Compare faces in order to get face's name correctly
        """
        faces = cls.get_encoded_faces()
        faces_encoded = list(faces.values())
        known_face_names = list(faces.keys())

        img = cv2.imread(filename, 1)

        face_locations = face_recognition.face_locations(img)
        unknown_face_encodings = face_recognition.face_encodings(img, face_locations)

        face_names = []
        for face_encoding in unknown_face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(faces_encoded, face_encoding)
            name = "Unknown"

            # use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(faces_encoded, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            face_names.append(name)
        # ----

        if face_names:
            path = "local_addons/web_widget_image_webcam/models/time/"
            now = datetime.now()
            current_time = now.strftime("%m-%d-%y %H:%M:%S")
            print(current_time)
            attendance_path = path + name + '/' + str(current_time)
            path_name_temprory = "local_addons/web_widget_image_webcam/models/name_temprory/" + name
            path_temprory = "local_addons/web_widget_image_webcam/models/name_temprory/"

            try:
                os.mkdir(attendance_path)
            except FileExistsError:
                print("Directory ", attendance_path, " already exists")

            folders = 0
            for _, dirnames, _ in os.walk(path_temprory):
                folders += len(dirnames)
            if folders > 0:
                # Remove time in directory
                for i in listdir(path_temprory):
                    try:
                        os.rmdir(path_temprory + '/' + f'{i}')
                    except OSError as e:
                        print("Error: %s : %s" % (path_temprory, e.strerror))
            try:
                os.mkdir(path_name_temprory)
            except FileExistsError:
                print("Directory ", path_name_temprory, "already exists")
        else:
            raise exceptions.ValidationError("Undefined Face !!")

        return face_names


    # Post time check in
    def create_time_check_in(self, *image_attendance, **name_user):
        """
        Post time check in with correct user
        :param id_user:
        :param name_user:
        :return:
        """
        self.classify_face(*image_attendance, **name_user)
        # Here is exception when take snapshot consiously
        name = [name for name in listdir('local_addons/web_widget_image_webcam/models/name_temprory')]
        mypath = f"local_addons/web_widget_image_webcam/models/time/{name[0]}"
        search_name = self.env['hr.employee'].search([('name', '=', name[0])])

        folders = 0
        for _, dirnames, _ in os.walk(mypath):
            folders += len(dirnames)
        if folders > 1:
            # Remove time in directory
            for i in listdir(mypath):
                try:
                    os.rmdir(mypath + '/' + f'{i}')
                except OSError as e:
                    print("Error: %s : %s" % (mypath, e.strerror))
        # ---

        time_check = [i for i in listdir(mypath)]
        time_check_in = datetime.strptime((time_check[0]), '%m-%d-%y %H:%M:%S')
        vals = {
            'employee_id': search_name.id,
            'check_in': str(time_check_in)
        }
        self.env['hr.attendance'].create(vals)

    # Post time check out
    def create_time_check_out(self, *image_attendance, **name_user):
        """
        Post time check out with correct user
        :param id_user:
        :param name_user:
        :return:
        """

        self.classify_face(*image_attendance, **name_user)
        name = [name for name in listdir('local_addons/web_widget_image_webcam/models/name_temprory')]
        mypath = f"local_addons/web_widget_image_webcam/models/time/{name[0]}"

        sleep(0.5)
        time_check = [i for i in listdir(mypath)]
        time_check_out = datetime.strptime((time_check[-1]), '%m-%d-%y %H:%M:%S')
        search_name = self.env['hr.employee'].search([('name', '=', name[0])])

        vals = {
            'check_out': str(time_check_out),
        }
        search_check_out = self.env['hr.attendance'].search([('check_out', '=', False),
                                                             ('employee_id', '=',search_name.id)])
        if search_check_out:
            search_check_out.sudo().write(vals)

        # Remove time in directory
        for i in listdir(mypath):
            try:
                os.rmdir(mypath + '/' + f'{i}')
            except OSError as e:
                print("Error: %s : %s" % (mypath, e.strerror))

    # Save into server after save image employee
    def write(self, vals):
        if self.env.user.has_group('web_widget_image_webcam.faceid_manager'):
            res = super(CheckWebCamEmployee, self).write(vals)
            path = "local_addons/web_widget_image_webcam/models/faces/"
            employee_id = self.sudo().env['hr.employee'].search([('id', '=', self.id)])
            dirname = os.path.dirname(path)
            image_name = employee_id.name.replace(" ", "_")  # Convert space to '_'
            link_image = os.path.join(dirname, image_name + ".jpg")
            imgdata = base64.b64decode(employee_id.image_1920)  # Convert base64 to image
            with open(link_image, 'wb') as f:
                f.write(imgdata)

            # Create folder to save time check in /out
            employee_name = self.sudo().env['hr.employee'].search([])
            path_time = "local_addons/web_widget_image_webcam/models/time/"
            path_img = "local_addons/web_widget_image_webcam/static/src/img/"
            for name in employee_name:
                path_time_name = path_time + name['name']
                path_img_name = path_img + name['name']
                try:
                    os.mkdir(path_time_name)
                except FileExistsError:
                    print("Directory ", path_time_name, " already exists")

                try:
                    os.mkdir(path_img_name)
                except FileExistsError:
                    print("Directory ", path_img_name, " already exists")

            return res

        else:
            raise UserError("You need permission to excicute this attribute!")

