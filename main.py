from fastapi import FastAPI, File, UploadFile, Form
import face_recognition
import psycopg2
import zipfile
import tempfile
import psycopg2.extras
import db_handler
import helper_methods as hm

hostname = 'localhost'
database = 'cs305_assignment_2'
username = 'postgres'
password = 'password'
port = 5432

table_name = "face"

app = FastAPI()

@app.put("/update_metadata/")
async def update_metadata(face_id: str = Form(...), version_number: str = Form(...), date: str = Form(...), location: str = Form(...)):
    """
    API endpoint which gives the functionality to update the metadata(version_number, date, location) of a particular face image.

    Args:
        face_id: Face ID of the image, whose metadata has to be updated
        version_number: Version number for the face image
        date: Date for the face image
        location: Location for the face image

    Returns:
        A json object to the client containing the result(s) for the request
    """
    status = 'ERROR'
    body = 'Failed to Update'
    try: 
        db = db_handler.DBHandler(hostname, database, username, password, port)   
        query_string = "UPDATE " + table_name + " SET version_number = %s, date = %s, location = %s WHERE face_id = %s"
        parameters = (version_number, date, location, face_id)

        db.executeQuery(query_string, parameters)    
        db.commitChanges()

        status = 'OK'
        body = 'Updated Successfully'
    except (Exception, psycopg2.Error) as error:
        print(error)
    finally:
        db.closeConnection()

    return {"status": status, "body": body}


@app.post("/search_faces/")
async def search_faces(file: UploadFile = File(..., description="An image file, possible containing multiple human faces."), 
k : int = Form(...), confidence_level : float = Form(...)):
    """
    API endpoint which gives the functionality to search faces in the database for determing top-k matches(pertaining to the
    confidence level) for each face in the supplied image

    Args:
        file: An image file, possible containing multiple human faces
        k: Top-k matches to be determined
        confidence_level: Confidence level is the upper limit on the Euclidean distance between the face encoding arrays of
            a known and an unknown image, to be considered a valid match.

    Returns:
        A json object to the client containing the result(s) for the request
    """
    image = face_recognition.load_image_file(file.file)
    status = 'ERROR'
    body = {}
    try:
        db = db_handler.DBHandler(hostname, database, username, password, port)
        matches = {}
        count = 0
        for unknown_image_encoding in face_recognition.face_encodings(image):
            count += 1
            matches_per_face = hm.get_matches(db, table_name, unknown_image_encoding, k, confidence_level)
            matches["face" + str(count)] = matches_per_face
            
        status = 'OK'
        body = {"matches" : matches}
    except (Exception, psycopg2.Error) as error:
        print(error)
    finally:
        db.closeConnection()

    return {"status": status, "body": body}


@app.post("/add_face/")
async def add_face(file: UploadFile = File(..., description="An image file having a single human face.")):
    """
    API endpoint which gives the functionality of adding an image(containing a single human face) to the face image database

    Args:
        file: An image file having a single human face, to be added to the database
    Returns:
        A json object to the client containing the result(s) for the request
    """
    status = 'ERROR'
    body = 'Failed to add the face'
    image = face_recognition.load_image_file(file.file)
    image_encoding_arr = face_recognition.face_encodings(image)
    if(len(image_encoding_arr) == 0):
        body = 'No face found in the image!'
    else:  
        try:
            db = db_handler.DBHandler(hostname, database, username, password, port)
            hm.insert_in_database(db, table_name, file.filename, image_encoding_arr[0])
            db.commitChanges()
            
            status = 'OK'
            body = 'Face added successfully'
        except (Exception, psycopg2.Error) as error:
            print(error)
        finally:
            db.closeConnection()

    return {"status": status, "body": body}


@app.post("/add_faces_in_bulk/")
async def add_faces_in_bulk(file: UploadFile = File(..., description="A ZIP file containing multiple face images.")):
    """
    API endpoint which gives the functionality of adding multiple face images to the face image database, by supplying a
    zipped file of the images.

    Args:
        file: A ZIP file containing multiple face images, to be added to the database
    Returns:
        A json object to the client containing the result(s) for the request
    """
    with tempfile.TemporaryFile() as temp:
        temp.write(file.file.read())

        status = 'ERROR' 
        body = 'Failed to add the face(s)'
        try:
            db = db_handler.DBHandler(hostname, database, username, password, port)
            with zipfile.ZipFile(temp, 'r') as zf:
                for name in zf.namelist():
                    start_indx = name.rfind("/")
                    filename = name
                    if(start_indx != -1):
                        filename = filename[start_indx + 1 : ]
                    if(len(filename) != 0):
                        image = face_recognition.load_image_file(zf.open(name))
                        image_encoding_arr = face_recognition.face_encodings(image)

                        if(len(image_encoding_arr) != 0):                    
                            hm.insert_in_database(db, table_name, filename, image_encoding_arr[0])

            db.commitChanges()
            status = 'OK'
            body = 'Face(s) added successfully'
        except (Exception, psycopg2.Error) as error:
            print(error) 
        finally:
            db.closeConnection()               
    
    return {"status": status, "body": body}


@app.post("/get_face_info/")
async def get_face_info(api_key: str = Form(...), face_id: str = Form(...)):
    """
    API endpoint which gives the functionality of getting the information about a face image in the database, by 
    providing its face ID.

    Args:
        face_id: Face ID of the image, whose metadata has to be returned
    Returns:
        A json object to the client containing the result(s) for the request
    """
    status = 'ERROR'
    body = None
    try:
        db = db_handler.DBHandler(hostname, database, username, password, port)
        query_string = "SELECT * FROM " + table_name + " WHERE face_id = %s"
        parameters = (face_id,)

        db.executeQuery(query_string, parameters)
        result = db.fetchOne()        

        status = 'OK'
        body = {'person_name': None, 'version_number': None, 'date': None, 'location': None}
        if result is not None:
            body = {'person_name': result.get('person_name'), 'version_number': result.get('version_number'), 'date': result.get('date'), 'location': result.get('location')}
            
    except (Exception, psycopg2.Error) as error:
        print(error)
    finally:
        db.closeConnection()
            
    return {"status": status, "body": body}