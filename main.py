import base64
import mimetypes

from fastapi import FastAPI,Request
import logging
from datetime import datetime

from starlette.responses import JSONResponse

import config

from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient, ContentSettings, PartialBatchErrorException
from SQLHelper import *
from pydantic import BaseModel
from flask import Flask, escape, request, render_template
from fastapi.middleware.wsgi import WSGIMiddleware



app = FastAPI(debug=True)

logger = logging.getLogger(__name__)

blob_service_client = BlobServiceClient(account_url=config.AZURE_STORAGE_ACCOUNT_URL,
                                        credential=config.AZURE_STORAGE_ACCOUNT_KEY)



class AttachmentDetail(BaseModel):
    attachment: str = None
    file_type: str = None
    file_name: str = None
    client_id: str = None
    complaint_id: str = None
    storage_app_name: str = None

class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name


@app.get("/")
@app.get("/home")
def read_main():
    return {"message": "Hello World"}

@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )

@app.post('/attachment_storage')
async def attachment_storage(attachmentdetail: AttachmentDetail):
    try:
        attachment = base64.b64decode(attachmentdetail.attachment.encode())
        attachmentdetail.file_name = attachmentdetail.file_name.replace(" ", "_")
        file_path_name = None
        file_name_blob = attachmentdetail.file_name + '.' + attachmentdetail.file_type
        complaintid_blob = attachmentdetail.complaint_id
        container_client = blob_service_client.get_container_client(config.CONTAINER_NAME)
        try:
            container_client.create_container()
        except ResourceExistsError:
            pass

        datetime_object = datetime.now()
        folder_nest = [datetime_object.year, datetime_object.month, datetime_object.day]
        try:
            parent_dir = [attachmentdetail.storage_app_name, attachmentdetail.client_id]
            for folder_name in folder_nest:
                parent_dir.append(folder_name)
            parent_dir.append(complaintid_blob)
            parent_dir.append(file_name_blob)
            file_path_name = '/'.join(map(str, parent_dir))

        except Exception as ex:
            pass

        blob_client = blob_service_client.get_blob_client(container=config.CONTAINER_NAME,
                                                          blob=file_path_name)
        logger.info('upload_blob invoked.')
        mimetype = mimetypes.guess_type(file_name_blob)[0]
        video = ['mp4', 'avi', 'wmv', 'flv', 'mpg', 'mpeg', 'mov', 'ogv']
        if attachmentdetail.file_type in video:
            mimetype = 'video/mp4'
        logger.info('mimetypes invoked completed' + str(mimetype))
        blob_client.upload_blob(attachment, overwrite=True,
                                content_settings=ContentSettings(content_type=mimetype))
        logger.info('upload_blob invoked completed')

        url = blob_client.url
        return url
    except Exception as ex:
        logger.error("failed in azure_storage_blob ", str(ex))
        return str(ex)



@app.delete('/delete_attachment')
async def delete_attachment(
        attachmentdetail: AttachmentDetail):  # attachment_name=None, client_id=None,complaint_id=None
    try:
        container_client = blob_service_client.get_container_client(config.CONTAINER_NAME)
        del_lst = []
        if attachmentdetail.attachment is not None:
            attachment_url = str.split(attachmentdetail.attachment, config.CONTAINER_NAME + '/')[1]
            try:
                logger.info('delete_blobs invoked.')
                container_client.delete_blobs(attachment_url)
                logger.info('delete_blobs Completed.')
                print("deleted attachment")
            except PartialBatchErrorException as ex:
                print("The attachment url doesnot exists!")

        elif attachmentdetail.client_id is not None:
            # blob_list = container_client.list_blobs()
            # print(blob_list)
            # for blob in blob_list:
            #     if blob.name.find('/' + client_id + '/') != -1:
            #         del_lst.append(blob.name)
            # print(del_lst)
            # container_client.delete_blobs(*del_lst)
            # print("deleted blobs of client")

            sql_helper = SQLHelper()
            blob_list = sql_helper.retrieve_data(
                'select message_url from nm.vw_blobstore_message_url where client_id = ' + attachmentdetail.client_id)
            for url in blob_list.get('data'):
                if url.get('message_url') is not None:
                    del_lst.append(str.split(url.get('message_url'), config.CONTAINER_NAME + '/')[1])
            print(del_lst)
            container_client.delete_blobs(*del_lst)
            print("deleted blobs of client id")


        elif attachmentdetail.complaint_id is not None:
            sql_helper = SQLHelper()
            blob_list = sql_helper.retrieve_data(
                'select message_url from nm.vw_blobstore_message_url where complaint_id = ' + attachmentdetail.client_id)
            for url in blob_list.get('data'):
                if url.get('message_url') is not None:
                    del_lst.append(str.split(url.get('message_url'), config.CONTAINER_NAME + '/')[1])
            print(del_lst)
            if len(del_lst) > 0:
                container_client.delete_blobs(*del_lst)
                print("deleted blobs of complaint id")
        else:
            print("please enter deletion criteria on basis of clientid,complaintis or attachment")

        return "deleted successfully"

    except Exception as ex:
        logger.error("failed in delete_blob ", str(ex))
        return str(ex)


# if __name__ == '__main__':
#     uvicorn.run(app, host="localhost", port="8000")
