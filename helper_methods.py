def find_image_encoding_str(image_encoding, start, end, flag):
    """
    Convert the 128-dimensional face encoding array into a comma separated tuple for storage
    and processing.

    Args:
        image_encoding: The 128-dimensional face encoding array
        start: Start index 
        end: End index
        flag: Bool flag to determine the presence(or absence) of enclosing round brackets

    Returns: 
        The formatted string for the desired part of the face encoding array
    """
    image_encoding_str = "(" if flag else ""

    for i in range(start, end):
        image_encoding_str += str(image_encoding[i])
        image_encoding_str += str(",")

    image_encoding_str = image_encoding_str[:-1]
    image_encoding_str += ")" if flag else ""
    
    return image_encoding_str


def get_matches(db, table_name, unknown_img_encoding, k, confidence):
    """
    Search for the top-k matches of an unknown face image in the table 'table_name',
    adhering to the strictness or the confidence level.

    Args:
        db: Object of the DBHandler class, to interact with the database at hand.
        table_name: Table against which the unknown face has to be matched
        unknown_img_encoding: The 128-dimensional face encoding array for the unknown face to be searched
        k: Top-k matches to be determined
        confidence: Confidence level is the upper limit on the Euclidean distance between the face encoding arrays of
            a known and an unknown image, to be considered a valid match.

    Returns: 
        Returns an array containing the top-k matches, adhering to the confidence level
    """
    arr_matches = []
    unknown_img_encoding_p1 = find_image_encoding_str(unknown_img_encoding, 0, len(unknown_img_encoding)//2, False)
    unknown_img_encoding_p2 = find_image_encoding_str(unknown_img_encoding, len(unknown_img_encoding)//2, len(unknown_img_encoding), False)

    expression_1 = "power(image_encoding_p1 <-> cube(array[" + unknown_img_encoding_p1 + "]), 2)"
    expression_2 = "power(image_encoding_p2 <-> cube(array[" + unknown_img_encoding_p2 + "]), 2)"
    query_string = "SELECT face_id, person_name FROM " + table_name + " WHERE sqrt(" + expression_1 + " + " + expression_2 + ") <= " + str(confidence) + " ORDER BY sqrt(" + expression_1 + " + " + expression_2 + ") LIMIT " + str(k)
    
    db.executeQuery(query_string, ())
    for record in db.fetchAll():
        arr_matches.append({'id': record['face_id'], 'person_name': record['person_name']})

    return arr_matches


def insert_in_database(db, table_name, filename, image_encoding):
    """
    Function to convert the values to be inserted into the desired storage format, and then
    insert into the database.

    Args:
        db: Object of the DBHandler class, to interact with the database at hand.
        table_name: Table in which the record should be inserted
        filename: Name of the file
        image_encoding: Face encoding array of the image
    """
    end_indx = filename.rfind('.')
    person_name = filename
    if(end_indx != -1):
        person_name = person_name[0 : end_indx]
    
    #The 128-dimensional face encoding is stored as two 64-dimensional tuples, for efficient storage and faster search.
    image_encoding_str_p1 = find_image_encoding_str(image_encoding, 0, len(image_encoding)//2, True)
    image_encoding_str_p2 = find_image_encoding_str(image_encoding, len(image_encoding)//2, len(image_encoding), True)
    
    query_string = "INSERT INTO " + table_name + "(person_name, image_encoding_p1, image_encoding_p2) VALUES(%s, %s, %s)"
    insert_parameters = (person_name, image_encoding_str_p1, image_encoding_str_p2)
    
    db.executeQuery(query_string, insert_parameters)