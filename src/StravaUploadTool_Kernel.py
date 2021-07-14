from authentication import *
from file_manipulation import *
import requests, urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import os, glob, time
from typing import Any, Tuple



# ------------------------------------
# activity uploading related functions
# ------------------------------------
def upload_Fit_Activity_Files(access_token: str):
    uploads_url = "https://www.strava.com/api/v3/uploads"
    payload = {'client_id': CLIENT_ID, 'data_type': 'fit'}
    header = {'Authorization': 'Bearer ' + access_token}

    print("Start uploading...\n")

    os.chdir(os.path.join(zwift_activity_dir, "FixedActivities"))
    for filename in glob.glob("*.fit"):
        with open(filename, 'rb') as fitfile:
            f = {'file': fitfile}
            r = requests.post(uploads_url,
                              data=payload,
                              headers=header,
                              files=f)
                                          
            print("Uploading your workout activity... " + filename)
            
            upload_ID = r.json().get('id_str')
            while (True):
                # polling the upload status per second
                wait(1)
                
                # THIS BLOCK WILL RAISE TYPEERROR (i.e., upload_ID is NoneType) - I don't know why exactly....
                # uploads_url = "https://www.strava.com/api/v3/uploads/" + upload_ID
                # header = {'Authorization': 'Bearer ' + access_token}
                
                # r = requests.get(uploads_url, headers=header)
                
                # error = r.json().get('error')
                # status = r.json().get('status')
                # activity_id = r.json().get('activity_id')

                # if (error is None) and (activity_id is None):  # Possibility 1: Your activity is still being processed.
                    # print(status + '.. ' + filename)
                # elif (error):                                  # Possibility 2: There was an error processing your activity. (check for malformed data and duplicates)
                    # print(status + '.. ' + filename)
                    # print("ERROR - " + error)
                    # print("\n")
                    # break
                # elif (activity_id is not None):                # Possibility 3: Your activity is ready.
                    # print(status + ' ( ' + filename + ' )')
                    # print("\n")
                    # fitfile.close()
                    # move_To_Uploaded_Activities_Folder(filename)
                    # break
                isError, activity_id = check_Upload_Status(access_token, filename, upload_ID)
                                                            
                if (isError):
                    break
                if (activity_id is not None):
                    fitfile.close()
                    move_To_Uploaded_Activities_Folder(filename)
                    break
    
    print("End of uploading.\n")


def check_Upload_Status(access_token: str, filename: str, upload_ID: str) -> Tuple[bool, Any]:
    uploads_url = "https://www.strava.com/api/v3/uploads/" + upload_ID
    header = {'Authorization': 'Bearer ' + access_token}
    
    r = requests.get(uploads_url, headers=header)
    
    error = r.json().get('error')
    status = r.json().get('status')
    activity_id = r.json().get('activity_id')

    if (error is None) and (activity_id is None):  # Possibility 1: Your activity is still being processed.
        print(status + '.. ' + filename)
        return (False, activity_id)
    elif (error):                                  # Possibility 2: There was an error processing your activity. (check for malformed data and duplicates)
        print(status + '.. ' + filename)
        print("ERROR - " + error)
        print("\n")
        return (True, activity_id)
    else:                                          # Possibility 3: Your activity is ready.
        print(status + ' ( ' + filename + ' )')
        print("\n")
        return (False, activity_id)


def wait(poll_interval: float):
    time.sleep(poll_interval)