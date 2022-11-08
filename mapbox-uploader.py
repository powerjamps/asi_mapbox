#!/Users/james/Documents/AirspaceIntelligence/Projects/mapbox-uploader/env/bin/python

from mapbox import Uploader
from pathlib import Path
import argparse

def upload(filename, tileset_name, token):
    # check variables
    if not isinstance(filename, str):
        raise TypeError('Filenmae must be a string.')
    if not filename.endswith('.geojson'):
        raise ValueError('Can only upload .geojson files. Got ' + str(filename))
    if not isinstance(tileset_name, str):
        raise TypeError('Tileset name must be a string.')

    # create uploader object
    u = Uploader(access_token=token)

    # upload the file to s3 staging bucket
    print('Uploading ' + filename + ' to s3 bucket...')
    url = u.stage(open(filename, 'rb'))

    # import to mapbox from the s3 bucket, convert to tileset
    print('Importing to mapbox and creating a new tileset...')
    job = u.create(url, tileset_name).json()

    # do nothing while the job is still ongoing
    while not u.status(job).json()['complete']:
        pass
    
    # delete the job from the uploader once it completes
    u.delete(job)

    print('Import complete. Check Mapbox to see if successful.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Mapbox Uploader')
    parser.add_argument('file_to_upload', type=str, help='.geojson file to upload')
    parser.add_argument('--tileset-name', dest='tileset_name', type=str, help='Mapbox tileset name')
    parser.add_argument('--token', dest='token', type=str, help='Upload config file')

    args = parser.parse_args()
    file_to_upload = args.file_to_upload
    if args.tileset_name is not None:
        tileset_name = args.tileset_name
    else:
        # If the tileset name is not supplied, use the input filename minus .geojson
        tileset_name = Path(file_to_upload).stem
    if args.token is not None:
        token = args.token
    else:
        # If token is not supplied, use the default Airspace Intelligence token
        token = 'sk.eyJ1Ijoia3VraWVsIiwiYSI6ImNrbGp6N3N6dTFyd2kydm9pcWMyeHJzOXYifQ.VNsGUn66LTJLhZmjD4N7Fw'

    upload(file_to_upload, tileset_name, token)