**1. What does this program do?**

The objective of this assignment is to develop a secure API service, with the primary function of performing a **facial search** on a database of images.

The API has several endpoints which can be reached out by sending HTTP post/put requests in order to populate the `face` image database, to search the `face` image database in order to retrieve **top-k** matches - pertaining to the strictness or the **confidence level**, and to query the database for obtaining metadata information about an image record. The scalability and performance of this API service are quite crucial.

**2. A description of how this program works (i.e. its logic)**

The program consists of an API with five endpoints viz. `/update_metadata/`, `/search_faces/`, `/add_face/`, `/add_faces_in_bulk/`, and `/get_face_info/`.

The implementation of the `/update_metadata/` endpoint provides the functionality of updating the metadata i.e., the **version number**, the **date**, and the **location** of an image record uniquely identified by its `face_id`.

The implementation of the `/search_faces/` endpoint provides the functionality of supplying an image file containing one or more unknown faces, and comparing each of these faces against the records of the `face` image database to obtain top-k matches for each, adhering to the upper limit set by the confidence level.

The implementation of the `/add_face/` endpoint gives the functionality to populate the `face` image database by supplying an image file having a single human face.

The implementation of the `/add_faces_in_bulk/` endpoint gives the functionality to populate the `face` image database with multiple image records by supplying a zip file containing the images corresponding to these records.

The implementation of the `/get_face_info/` endpoint provides the functionality of getting information(`person_name`, `version_number`, `date`, and `location`) about a face image in the database, by providing its associated `face_id`.

**Representation of images**
To ensure performance and efficiency, each face image is represented in the database using the corresponding **128-dimensional face encoding** array returned by the `face_recognition` library. Specifically, the image is stored in the database as **two 64-dimensional cubes**, using the [cube data](https://www.postgresql.org/docs/14/cube.html) type in Postgres. The reason for using two 64-dimensional cubes(instead of a single 128-dimensional cube) for representation is due to the default limit of **100** on the number of dimensions of cubes, in Postgres.

**Retrieval of images**
The usage of `cube` data type for storing the images gives us an access to the cube operation `a <-> b`, which computes the **Euclidean distance** between the two cubes. Thus, we can reduce the additional(and probably redundant) steps of first retrieving all the records, finding the Euclidean distance between the face encoding of each of the known faces with that of the unknown face,and then sorting and filtering the records to select top-k matches - pertaining to the confidence level.
Instead, using the cube operator, all these operations can be combined into a **single** SQL query, ensuring better performance and scalability due to reduced overheads.
The SQL query resembles

```SQL
SELECT *
FROM face
WHERE (known_image_encoding <-> unknown_image_encoding) <= confidence_level
ORDER BY (known_image_encoding <-> unknown_image_encoding)
LIMIT k;
```

The above query directly returns the top-k matches pertaining to the confidence level.

**3. How to compile and run this program**

**Setting up the database**
In this implementation, a database `cs305_assignment_2` with a table `face` is created under the user `postgres`. Therefore, before running the code, ensure that you have updated the variables `hostname`, `database`, `username`, `password`, `port`, and `table_name` in `main.py` as per your requirement.
In order to create the database and the table, follow the given steps:

```SQL
CREATE DATABASE cs305_assignment_2;
```

In the database `cs305_assignment_2`, use the following commands:

```SQL
CREATE EXTENSION cube;

CREATE TABLE face(
 face_id serial PRIMARY KEY,
 person_name TEXT,
 version_number TEXT,
 date TEXT,
 location TEXT,
 image_encoding_p1 cube,
 image_encoding_p2 cube
);
```

Ensure that you have cube extension available with your Postgres installation.
You can deviate from these definitions as long as nothing breaks.

**Installing all the dependencies**
Install the following libraries/dependencies for running different aspects of this implementation:

- fastapi
- uvicorn
- [face_recognition](https://github.com/ageitgey/face_recognition)
- psycopg2
- pytest
- coverage
  etc.

**Running the code**
To run the API service, use the following command:
`uvicorn main:app`

To run the tests - without coverage, use the command given below:
`pytest`

To run the tests - with coverage, you can use the following commands:
`coverage run -m pytest test_main.py`
`coverage report -m`
