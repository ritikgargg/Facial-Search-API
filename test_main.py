from fastapi.testclient import TestClient

from main import app

client = TestClient(app)    

def test_update_metadata():
    """
    Function to test update_metadata() of main.py
    This test function works on the assumption that the face image table contains an image with face_id == 1
    """
    response =  client.put(
            "/update_metadata/",
            data = {
                "face_id": "1",
                "version_number": "2.5",
                "date": "23-09-2019",
                "location" : "New York"
            },
            )
    assert response.status_code == 200
    assert response.json() == {"status": "OK", "body": "Updated Successfully"}

def test_search_faces():
    """Function to test search_faces() of main.py"""
    fpath = "resources/Atal_Bihari_Vajpayee_0001.jpg"
    with open(fpath, 'rb') as f:
        response =  client.post(
                    "/search_faces/",
                    data = {
                        "k": 1,
                        "confidence_level" : 0.5
                    },
                    files = {"file": ("Atal_Bihari_Vajpayee_0001.jpg", f, "image/jpeg")}
                    )
        assert response.status_code == 200
        assert response.json()['status'] == 'OK'
        assert response.json()['body']['matches']['face1'][0]['person_name'] == 'Atal_Bihari_Vajpayee_0001'

def test_add_face():
    """Function to test add_face() of main.py"""

    #Adding an image file containing a face.
    fpath = "resources/Atal_Bihari_Vajpayee_0001.jpg"
    with open(fpath, 'rb') as f:
        response =  client.post(
                    "/add_face/",
                    files = {"file": ("Atal_Bihari_Vajpayee_0001.jpg", f, "image/jpeg")}
                    )
        assert response.status_code == 200
        assert response.json() == {"status": "OK", "body": "Face added successfully"}

    #Adding an image file containing no face.
    fpath = "resources/no_face.jpeg"
    with open(fpath, 'rb') as f:
        response =  client.post(
                    "/add_face/",
                    files = {"file": ("no_face.jpeg", f, "image/jpeg")}
                    )
        assert response.status_code == 200
        assert response.json() == { "status": "ERROR", "body": "No face found in the image!"}
    

def test_add_faces_in_bulk():
    """Function to test add_faces_in_bulk() of main.py"""
    fpath = "resources/input.zip"
    with open(fpath, 'rb') as f:
        response = client.post(
            "/add_faces_in_bulk/",
            files = {"file" : ("input.zip", f, "application/x-zip-compressed")}
        )

        assert response.status_code == 200
        assert response.json() == {"status": "OK", "body": "Face(s) added successfully"}

def test_get_face_info():
    """
    Function to test get_face_info() of main.py
    This test function works on the assumption that the face image table contains an image with face_id == 2 and
    person_name == 'Jennifer_Lopez_0001'
    """
    response =  client.post(
            "/get_face_info/",
            data = {
                "api_key" : "45678",
                "face_id": "2",
            },
            )

    assert response.status_code == 200
    assert response.json()['status'] ==  "OK"
    assert response.json()['body']['person_name'] == 'Jennifer_Lopez_0001'