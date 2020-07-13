import os
import csv
import glob
import wget
import requests
import datetime
import telegram
import subprocess
import numpy as np
import pandas as pd
from tqdm import tqdm
from zipfile import ZipFile 
from telegram.ext import Updater
import xml.etree.ElementTree as ET
from argparse import ArgumentParser

def send_tele(data):
    try :
        updater = Updater('805281461:AAH09xnakEe8MxOBLQ7jWaiNolGxoZyxxrM', use_context=True )
        dp = updater.dispatcher
        token='805281461:AAH09xnakEe8MxOBLQ7jWaiNolGxoZyxxrM'
        bot = telegram.Bot(token=token)
        bot.send_message(chat_id='-496362146', text=data+ str(datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")))
    except:
        print('SENDING ERROR IN plot')

def download_file_from_google_drive(id, destination):
    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value

        return None

    def save_response_content(response, destination):
        CHUNK_SIZE = 32768

        with open(destination, "wb") as f:
            with tqdm(unit='B', unit_scale=True, unit_divisor=1024) as bar:
                for chunk in response.iter_content(CHUNK_SIZE):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                        bar.update(CHUNK_SIZE)

    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()
    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)
    save_response_content(response, destination) 
def select_files(path):


    sub_foders = os.listdir(path)
    train = []
    test = []
    names = []
    for x in sub_foders:
        if x == 'test':
            test_dir = os.path.join(path,x)
            test.append(test_dir)
        elif x == 'train':
            train_dir = os.path.join(path,x)
            train.append(train_dir)
        elif x == 'names.txt':
            names_dir = os.path.join(path,x)
            names.append(names_dir)

    return train[0], test[0], names[0]

def un_zip(source,destination):
        file_name = source
      
        # opening the zip file in READ mode 
        with ZipFile(file_name, 'r') as zip: 
        # printing all the contents of the zip file 
            zip.printdir() 
          
            # extracting all the files 
            print('Extracting all the files now...') 

            # ######## ADD DESTINATION LOCATION HERE
            zip.extractall(destination) 
            print('Done!') 

def find_folder(path):
    sub_dir = os.listdir(path)
    for x in sub_dir:
        a = x.split('.')
        if len(a) == 1:
            folder = x
    return folder

class convert():
    '''
    Input sould be data_path, project_dir
    '''
    def xml_to_csv(path):
        xml_list = []
        for xml_file in glob.glob(path + '/*.xml'):
            tree = ET.parse(xml_file)
            root = tree.getroot()
            for member in root.findall('object'):
                value = (os.path.join(path,root.find('filename').text),
                         int(member[1][0].text),
                         int(member[1][1].text),
                         int(member[1][2].text),
                         int(member[1][3].text),
                         member[0].text,
                         )
                if int(member[1][0].text)<int(member[1][2].text)  and int(member[1][1].text)<int(member[1][3].text):
                    xml_list.append(value)
        column_name = ['filename', 'x1', 'y1', 'x2', 'y2', 'class_name']
        xml_df = pd.DataFrame(xml_list)
        return xml_df

    def main(data_folder_path,project_dir,name_ext):
        path = data_folder_path
        csv_p_init = os.path.join(project_dir,'train_demo.csv') 
        csv_path_demo = csv_p_init
        csv_final = os.path.join(project_dir,name_ext)
        xml_df = convert.xml_to_csv(path)
        xml_df.to_csv((csv_path_demo), index=None)
        print('Successfully converted xml to csv.')
        with open(csv_p_init,'r') as f, open(csv_final,'w') as f1:
            next(f) # skip header line
            for line in f:
                f1.write(line)

        return csv_final 

def create_names_csv(text_dir,project_dir):

    names_csv_dir = os.path.join(project_dir,'names.csv')
    file = open(text_dir)
    lines = file.readlines()
    class_names = []
    count = 0
    for x in lines:
        if x != '\n': 
            clas_name = x.split('\n',1)[0]
            string = [str(clas_name) , str(count)]
            class_names.append(string)
            count = count + 1

    with open(names_csv_dir,'w') as csvfile:

        writer = csv.writer(csvfile)
        writer.writerows(class_names)
    return names_csv_dir

if __name__ == "__main__":


    parser = ArgumentParser()
    parser.add_argument("--backbone", default='resnet101', help="Which yolo you want to use resnet101 or resnet50")
    parser.add_argument("--project", required=True, help="Give project name")
    parser.add_argument("--batch_size", default = 3 , help="Give batch size")
    parser.add_argument("--steps", default =  250, help="Give batch step size")
    parser.add_argument("--epochs", default =  25, help="Give epoch size", type = int)
    parser.add_argument("--data_source", required = True, help='Provide url or google Id or path(dir)')

    opt = parser.parse_args()

    # making project folder
    project_name = opt.project 
    project_dir = os.path.join(os.getcwd(),project_name)

    isdir = os.path.isdir(project_dir) 
    if isdir is False:
        # CREATING PROJECT DIRECTORY
        os.mkdir(project_dir)
    # TXT AND FOLDER DIRECTORIES FIND
    # text_dir_is_array = []
    # data_dir_is_array = []
    # sub_dirs = os.listdir(opt.data_source)
    # for x in sub_dirs:
    #     txt_is = x.find('.txt')
    #     if txt_is != -1:
    #         txt_dir_is=os.path.join(opt.data_source,x)
    #         text_dir_is_array.append(txt_dir_is)
    #     else:
    #         data_dir_is = os.path.join(opt.data_source,x)
    #         data_dir_is_array.append(data_dir_is)

    # # downloading data in project_name foldercreate_csv
    # data_dir = data_dir_is_array[0]

    # is_dir = os.path.isdir(data_dir)
    # #  No download just link path
    # print(data_dir)
    # if is_dir is True:
    #     print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
    #     print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
    #     print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
    #     print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
    #     print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')


    #     data_folder = data_dir
    #     print('Data_source is a directory')

    # elif is_dir is False:
    #     # Downloading from a URL
    #     is_google_id_url = data_dir.find('https')
    #     print(' checking URL or not  ',is_google_id_url)
    #     if is_google_id_url != -1:
    #         print("Download from a URL")
    #         wget.download(data_dir,project_dir)
    #         list_sub_folder = os.listdir(project_dir)
    #         for x in list_sub_folder:
    #             check = x.find('.zip')
    #             if check != -1:
    #                 source_zip = os.path.join(project_dir,x)
    #                 destination_zip = project_dir

    #                 # un_zip(source_zip,destination_zip)

    #     elif is_google_id_url == -1 and is_dir == False :
    #         # Downloading from google drive + Unzip
    #         print('Download from google drive')
    #         project_dir_zip = os.path.join(project_dir, 'custom_data.zip')

    #         download_file_from_google_drive(data_dir,project_dir_zip)
    #         sub_folder = os.listdir(project_dir)

    #         for x in range(len(sub_folder)):

    #             is_zip = sub_folder[x].find('.zip')
    #             if is_zip != -1:
    #                 zip_folder = os.path.join(project_dir,sub_folder[x])

    #         un_zip(zip_folder,project_dir)
    #     # data_folder = find_folder(project_dir)
    #     # FINDING DATA FOLDER WHERE IMGS+XMLS PRESENT TO CREATE CSV.
    #     data_folder = find_folder(project_dir)
    input_data_source = opt.data_source

    is_dir = os.path.isdir(input_data_source)


    train_path = []
    test_path = []
    names_path = []
    if is_dir is True:
        print('input_data_source is a directory')
        train_directory , test_directory, names_directory = select_files(input_data_source)

        # print('Train',train_directory)
        # print('Test',test_directory)
        # print('Names',names_directory)

    elif is_dir is False:
        '''
            aFTER DOWNLOADING DATA FROM SOURCE UNZIP IT AND THEN PASS THE DATA DIR HERE TO FIND TEST TRAIN AND NAMES

            DATA SHOULD BE DOWNLOADED IN PROJECT DIRECTORY

        '''

        is_url = input_data_source.find('https')

        if is_url != -1:
            print('input_data_source is a url')
            # Download data in project directory
            wget.download(input_data_source,project_dir)
            sub_dir = os.listdir(project_dir)
            for x in sub_dir:
                is_zip = x.split('.')[-1]
                if is_zip == 'py':
                    zip_path = os.path.join(project_dir,x)
            # zip file path
            print(zip_path)
            # source zip / project directory
            un_zip(zip_path,project_dir)

        elif is_url == -1 and is_dir == False:
            print('input_data_source is a google id')
            # while downloading frm google drive we need to provide .zip path
            download_path = os.path.join(project_dir,'download.zip')
            download_file_from_google_drive(input_data_source,download_path)
            sub_dir = os.listdir(project_dir)
            un_zip(download_path,project_dir)


        sub_project_dir = os.listdir(project_dir)
        down_fodler = []
        for x in sub_project_dir:
            folder_path = os.path.join(project_dir,x)

            is_downloaded_folder = os.path.isdir(folder_path)
            if is_downloaded_folder is True:
                downld_folder_is = is_downloaded_folder
                down_fodler.append(folder_path)
            else:
                pass

        train_directory , test_directory, names_directory = select_files(down_fodler[0])
        # print('Train',train_directory)
        # print('Test',test_directory)
        # print('Names',names_directory)

    data_gen_train_csv = convert.main(train_directory,project_dir,'train.csv')
    data_gen_test_csv = convert.main(test_directory,project_dir,'test.csv')
    names_gen_csv = create_names_csv(names_directory,project_dir)


    backup_dir = os.path.join(project_dir,'back_up_'+opt.backbone)

    store_path = ' --snapshot-path ' + str(backup_dir)
    custom = ' --backbone '+str(opt.backbone) + ' --epochs ' +str(opt.epochs)+ ' --steps '+str(opt.steps)+' --batch-size '+str(opt.batch_size)+ store_path
    run = 'keras_retinanet/bin/train.py '+str(custom)+' csv ' +str(data_gen_train_csv)+ ' ' +str(names_gen_csv) + ' --val-annotations '+str(data_gen_test_csv)

    print('######################')
    print(run)
    print('######################')



    p = subprocess.Popen(run, shell=True, stdout=subprocess.PIPE)
    once_send = 'Project : ' +str(project_name) +' Backbone : '+ str(opt.backbone) +'  '
    try:
        print('Training has been started')
        # send_tele('Training Has Been Started ')
        # send_tele(once_send)
    except:
        pass

    while True:
        out = p.stdout.readline()
        all_op = out.decode("utf-8")
        fint_var = str(opt.steps)+'/'+str(opt.steps)
        last_epoch = all_op.find(fint_var)

        if last_epoch != -1:
            # # TERMINAL OUT PUT
            # # 10/10 [==============================] - 35s 3s/step - loss: 4.1784 - regression_loss: 3.0459 - classification_loss: 1.1325
            try:
                print("Fuck you have epoch here")
                # send_tele(out.decode("utf-8"))
            except:
                pass
        epoch = all_op.find("Epoch")

        if epoch != -1:
            # TERMINAL OUT PUT
            # Epoch 1/2
            # Epoch 00001: saving model to /home/tericsoft/team_alpha/project/retinanet/keras-retinanet/mask/resnet101_csv_01.h5
            # print(out.decode("utf-8"))
            try:
                count_save = out.decode("utf-8").split(':')[0]
                epoch_save_number = int(count_save.split(' ')[-1])
                if epoch_save_number == opt.epochs:
                    print('training has been ended')
                    # send_tele('Training has been Ended \n')
                    p.terminate() # send sigterm, or ...
                    p.kill()      # send sigkill
                    break
            except:
                pass
            try:
                print("What the fuck is this")
                # send_tele(out.decode("utf-8"))
            except:
                pass

        map_is = out.decode('utf-8').find("average precision")
        if map_is != -1:
            try:
                print("What the fuck is this")
                # send_tele(out.decode('utf-8'))
            except:
                pass
        # average precision
