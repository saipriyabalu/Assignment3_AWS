# References: https://github.com/keithweaver/python-aws-s3/blob/master/example-upload-public.py,
# https://stackoverflow.com/questions/30249069/listing-contents-of-a-bucket-with-boto3,
# https://stackoverflow.com/questions/3140779/how-to-delete-files-from-amazon-s3-bucket
# http://boto3.readthedocs.io/en/latest/guide/collections.html
# http://boto3.readthedocs.io/en/latest/reference/services/iam.html
# http://docs.ceph.com/docs/master/radosgw/s3/python/
# http://boto3.readthedocs.io/en/latest/guide/configuration.html
# http://boto3.readthedocs.io/en/latest/guide/migrations3.html
# https://docs.python.org/2/tutorial/inputoutput.html
# https://github.com/boto/boto3/issues/597

import boto3, os, botocore
from botocore.client import Config
from flask import Flask, request

ACCESS_KEY_ID = 'AKIAJRDYO54L4JNMEZ3Q'
ACCESS_SECRET_KEY = '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'

BUCKET_NAME = 'saipriya'

# Connect to S3
s3 = boto3.resource('s3',aws_access_key_id=ACCESS_KEY_ID,aws_secret_access_key=ACCESS_SECRET_KEY,config=Config(signature_version='s3v4'))

app = Flask(__name__)

APPROOT = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/login',methods = ['POST'])
def login():
    for object in s3.Bucket('saipriya').objects.all():
        if 'signin.txt' == object.key:
            read_s3obj = object.get()['Body'].read()
            user = request.form['uname']
            passw = request.form['password']
            username,password = read_s3obj.split(b":")
            if username == user.encode() and password == passw.encode():
                print("User credentials successful")
                return app.send_static_file('filehandle.html')
            else:
                return "Wrong Password! Please try again"

@app.route('/list', methods=['POST'])
def list(temp_file=""):
    global bucket
    for bucket in s3.buckets.all():
        print(bucket.name)
        name = bucket.name
        for object in bucket.objects.all():
            temp_file += object.key + '\t\t' + 'Size:  ' + str(object.size) + 'Last Updated' + str(object.last_modified)
    return name + temp_file

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    file_name = file.filename
    data = open(file_name, 'rb')
    s3.Bucket('saipriya').put_object(Key=file_name, Body=data)
    return "File uploaded succesfully!"


@app.route('/download', methods=['POST'])
def download():
    downloadfile = request.form['filename']
    key = downloadfile
    try:
        file="https://s3.amazonaws.com/saipriya/%s"%downloadfile
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object doesnt exist")
        else:
            raise
    return '<a href=%s>download</a>'%file

@app.route('/delete', methods=['POST'])
def delete():
    filedelete = request.form['filename']
    for bucket in s3.buckets.all():
        for object in bucket.objects.all():
            if object.key == filedelete:
                object.delete()
        print('File deleted')
    return "File deleted successfully"

@app.route('/viewfile',methods=['POST'])
def view():
    view_f = request.form['filename']
    for object in s3.Bucket('saipriya').objects.all():
        if(view_f==object.key):
            file,ext=view_f.split('.')
            if ext=='jpg':
                return '<img src = "https://s3.amazonaws.com/saipriya/%s">' % view_f
            elif ext=='txt':
                read = object.get()['Body'].read()
                return '<pre>%s</pre>'%read.decode('utf-8')
            else:
                return 'Requested file is not found'

@app.route('/logout', methods=['POST'])
def logout():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(port=5010, debug=True)

