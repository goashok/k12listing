image_dir = "static/img/uploads"

subdirs = {'Book' : 'books', 'Game' : 'games', 'Instrument' : 'instruments'}

def get_filename(imageObj):
    if imageObj is not None:
        filepath = imageObj.filename.replace('\\', '/')  # replaces the windows-style slashes with linux ones.
        if filepath == "":
            return None
        return filepath.split('/')[-1]  # splits the and chooses the last part (the filename with extension)
    else:
        return None

def upload(type, imageObj, postid):
    filename = get_filename(imageObj)
    filepath = image_dir + '/' + subdirs[type] + '/' + str(postid) + "_" + filename
    print(">>> Uploading " + filepath)
    fout = open(filepath, 'w')  # creates the file where the uploaded file should be stored
    fout.write(imageObj.file.read())  # writes the uploaded file to the newly created file.
    fout.close()  # closes the file, upload complete.
