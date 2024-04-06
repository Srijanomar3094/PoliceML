from django.http import JsonResponse,HttpResponse
import json
from django.contrib.auth.models import User
from register.models import User_Details
from .models import Panel,Shared,Data,File_Icon,FIR
import re
import datetime
import os
from PIL import Image
from django.conf import settings
import PyPDF2
import pytesseract
from django.http import JsonResponse
from datetime import datetime
from .models import Data, File_Icon, User_Details, FIR
from django.contrib.auth.models import User
from PyPDF2 import PdfReader






def left_panel(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            items=Panel.objects.filter(panel_type="left",delete_status=False).values('option','state','icon')
            return JsonResponse(list(items),safe=False)
        else:
             return JsonResponse({"message":"user is not authenticated"},status=401)
    else:
         return JsonResponse({"message":"invalid request method"},status=400)
        



def right_panel(request):
     if request.method == 'GET':
            
        if request.user.is_authenticated:
            user_id = request.user.id
            items=Panel.objects.filter(panel_type="right",delete_status=False).values('option','state','icon')
            

            return JsonResponse(list(items),safe=False)
        else:
             return JsonResponse({"message":"user is not authenticated"},status=401)
     else:
         return JsonResponse({"message":"invalid request method"},status=400)
     



def dots_panel(request):
    if request.method == 'GET':
            
        if request.user.is_authenticated:
            items=Panel.objects.filter(panel_type="dots",delete_status=False).values('option','state','icon')
            return JsonResponse(list(items),safe=False)
        else:
             return JsonResponse({"message":"user is not authenticated"},status=401)
    else:
         return JsonResponse({"message":"invalid request method"},status=400)




def profile_pic(request):
    if request.method == 'POST':
            
        if request.user.is_authenticated:
            user_id = request.user.id
            item=User.objects.filter(id=user_id).values('first_name','last_name')
            return JsonResponse(list(item),safe=False)
        else:
             return JsonResponse({"message":"user is not authenticated"},status=401)
        

    if request.method == 'GET':
         
        if request.user.is_authenticated:

            user_id = request.user.id
            profile=User_Details.objects.filter(user=user_id).values('profile__image')
            return JsonResponse(list(profile),safe=False)
        else:
            return JsonResponse({"message":"user is not authenticated"},status=401)
    else:
         return JsonResponse({"message":"invalid request method"},status=400)




def size_unit(size):
        if size>999999:
            size=size/1000000
            file_size=str(size)+' GB'
        elif size>999:
            size=size/1000
            file_size=str(size)+' MB'
        else:
            file_size=str(size)+' KB'
        return file_size



def file_upload(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            file=request.FILES.get('file')
        
            folder_id=request.POST.get('folderid')

            user_id = request.user.id
            owner_id=User.objects.get(id=user_id)
            if file and folder_id:
                folder_exists=Data.objects.filter(id=folder_id).exists()
                if folder_exists:
                    if (Data.objects.filter(file_name=file,owner=owner_id,status=False).exists()):
                        return JsonResponse({"message":"file name already exists"},status=400)
                    else:
                        detail=User_Details.objects.get(user=user_id)
                        folderid=Data.objects.get(id=folder_id)
                        split_tup = os.path.splitext(str(file))
                        file_extension = split_tup[1]
        
                        ex=File_Icon.objects.filter(format=file_extension)
                        if ex.exists():
                            ext=ex.get(format=file_extension)
                        else:
                            ext=File_Icon.objects.get(format='.file')

                        new=Data.objects.create(
                            file_name=file,
                            owner=owner_id,
                            file_size_kb=file.size/1000,
                            last_modified=datetime.now(),
                            parent_folder=folderid,
                            icon=ext,
                            details=detail
                            
                        )
                    return JsonResponse({"message":"file saved succesfully"},status=200)
                else:
                    return JsonResponse({"message":"incorrect folder id"},status=400)
            elif file:
                    if (Data.objects.filter(file_name=file,owner=owner_id).exists()):
                        return JsonResponse({"message":"file name already exists"},status=400)
                    else:
                        detail=User_Details.objects.get(user=user_id)
                        split_tup = os.path.splitext(str(file))
            
                        filename = split_tup[0]
                        file_extension = split_tup[1]
        
                        ex=File_Icon.objects.filter(format=file_extension)
                        if ex.exists():
                            ext=ex.get(format=file_extension)
                        else:
                            ext=File_Icon.objects.get(format='.file')
                        new=Data.objects.create(
                            file_name=file,
                            owner=owner_id,
                            file_size_kb=file.size/1024,
                            last_modified=datetime.now(),
                            icon=ext,
                            details=detail
                        )

                    return JsonResponse({"message":"file saved succesfully"},status=200)
            else:
                return JsonResponse({"message":"no file found"},status=400)
        else:
            return JsonResponse({"messsage":"user is not authenticated "},status=401)
    else:
        return JsonResponse({"message":"invalid request method"},status=400)
    


            

def create_folder(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
        
            data = json.loads(request.body)
            folder=data.get('new_folder')
            p_folder=data.get('parent_id')
            user_id = request.user.id
            owner_id=User.objects.get(id=user_id)
            instance=File_Icon.objects.get(format='.folder')
            
            if folder and p_folder :
                parent_folder=Data.objects.filter(id=p_folder)
                if parent_folder.exists():

                    if Data.objects.filter(owner=owner_id,folder_name=folder,status=False).exists():
                        return JsonResponse({"message":"folder name already exists"},status=400)
                    else:
                        
                        detail=User_Details.objects.get(user=user_id)
                        new=Data.objects.create(
                            owner=owner_id,
                            file_name=None,
                            folder_name=folder,
                            last_modified=datetime.datetime.now(),
                            parent_folder=parent_folder.get(id=p_folder),
                            icon=instance,
                            details=detail
                        )
                
                        return JsonResponse({"message":"folder created successfully"},status=200)
                else:
                    return JsonResponse({"message":"incorrect parent folder id"},status=400)
            elif folder:
                    if Data.objects.filter(owner=owner_id,folder_name=folder).exists():
                        return JsonResponse({"message":"folder name already exists"},status=400)
                    else:
                        detail=User_Details.objects.get(user=user_id)
                        new=Data.objects.create(
                                owner=owner_id,
                                file_name=None,
                                folder_name=folder,
                                last_modified=datetime.datetime.now(),
                                icon=instance,
                                details=detail
                        )
                        return JsonResponse({"message":"folder created successfully"},status=200)
            else:
                return JsonResponse({"message":"invalid data"},status=400)
        else:
            return JsonResponse({"message":"user not authenticated"},status=401)
    else:
        return JsonResponse({"messsage":"invalid method"},status=400)
            



def folder_upload(request):
    if request.method == 'POST':
            if request.user.is_authenticated:
            
                data = json.loads(request.body)
            
                foldername=data.get('folder_name')
                pfolder=data.get('p_folder')
                files=data.FILES.get('files')

                if files and foldername:
                    
                    
                    user_id = request.user.id
                    owner_id=User.objects.get(id=user_id)

                    if Data.objects.filter(owner=user_id,folder_name=foldername).exists():
                        return JsonResponse({"message":"folder name already exists"},status=400)

                    else:
                      new_folder=Data.objects.create(
                            owner=owner_id,
                            file_name=None,
                            folder_name=foldername,
                            last_modified=datetime.datetime.now(),
                            parent_folder=Data.get(id=pfolder),
                            icon="bi bi-folder-fill"
                        )

                    folderid=Data.objects.get(folder_name=foldername,owner=user_id)

                    for file in files:
            
                        size = (file.size)/1024
                        
                        upload=Data.objects.create(

                        file_name=file,
                        owner=owner_id,
                        file_size_kb=file.size/1024,
                        last_modified=datetime.datetime.now(),
                        icon="bi bi-file-earmark-fill"
                        )
          
                    return JsonResponse({"message":"created folder  succesfully"},status=200)
            else:
             return JsonResponse({"message":"user not authenticated"},status=401)
    else:
         return JsonResponse({"message":"invalid request method"},status=400)




def star_icon(star):
    if star==True:
        icon="bi bi-star-fill"
    else:
        icon="bi bi-star"
    return icon




def get_data(request):
    if request.method == 'GET':
         if request.user.is_authenticated:
            userid = request.user.id
            
            folders=Data.objects.filter(owner=userid,binned_date=None,folder_name__isnull=False,status=True,parent_folder=None).order_by('folder_name').all()

            fdata=[]
            for folder in folders:
               details=User_Details.objects.filter(user=folder.owner).first()
               profilepic=details.profile.image
               star=folder.starred
               staricon=star_icon(star)
               
               name='me'
               size='__'
               fdata+=[{
               'folder_name':folder.folder_name,
               'profile_image':str(profilepic),
               'name':name,
               'last_modified':folder.last_modified.date(),
               'id':folder.id,
               'starred':folder.starred,
               'star_icon':staricon,
               'icon':str(folder.icon.image), 
               'name':name,
               'file_size':size
               }]

            files=Data.objects.filter(owner=userid,binned_date=None,status=True,folder_name=None,parent_folder=None).all().order_by('file_name')
            
            data=[]
            for file in files:
               details=User_Details.objects.filter(user=file.owner).first()
               profilepic=details.profile.image
               if userid==file.owner_id:
                   name='me'
               else:
                   name=file.owner.first_name+' '+file.owner.last_name
               size=file.file_size_kb

               total_storage=size_unit(size)
               star=file.starred
               staricon=star_icon(star)
               data+=[{
               'file_name':str(file.file_name),
               'profile_image':str(profilepic),
               'name':name,
               'last_modified':file.last_modified.date(),
               'id':file.id,
               'starred':file.starred,
               'icon':str(file.icon.image), 
               'file_size':total_storage,
               'star_icon':staricon,
               }]
        
            return JsonResponse(fdata+data,safe=False)
    else:
         return JsonResponse({"message":"invalid method"},status=401)




def starred(request):
    
    if request.user.is_authenticated:
        if request.method == 'POST':
        
            data = json.loads(request.body)
        
            star=data.get('star')
            data_id=data.get('id')
            if data_id :
                if star=="true":
                    
                    update=Data.objects.filter(id=data_id).first()
                    update.starred=True
                    update.last_modified=datetime.datetime.now()
                    update.save()
                    return JsonResponse({"message":"updated"},status=200)

                elif star=="False":

                    update=Data.objects.filter(id=data_id).first()
                    update.starred=False
                    update.last_modified=datetime.datetime.now()
                    update.save()
                    return JsonResponse({"message":"updated"},status=200)


                else:
                    return JsonResponse({"message":"invalid data"},status=400)
            else:
                return JsonResponse({"message":"incorrect id"},status=400)
            
       


        if request.method == 'GET':
            userid = request.user.id
            
            folders=Data.objects.filter(owner=userid,starred=True,binned_date__isnull=True,folder_name__isnull=False,parent_folder=None,status=True).all().order_by('folder_name')
            fdata=[]
            for folder in folders:
               

               total_storage='__'
             
               name='me'
              
               fdata+=[{
               'folder_name':str(folder.folder_name),
               'name':name,
               'id':folder.id,
               'last_modified':folder.last_modified.date(),
               'profile':str(folder.details.profile.image),
               'icon':str(folder.icon.image), 
               'file_size_kb':total_storage,
               'location':'My Drive',
               'location_icon':'bi bi-hdd'
               }]

            fshares=Shared.objects.filter(shared_to=userid,starred=True,data__binned_date__isnull=True,data__folder_name__isnull=False,status=True).all().order_by('data__folder_name')

            for fshare in fshares:
               if userid==fshare.owner_id:
                   name='me'
               else:
                   name=fshare.owner.first_name+' '+fshare.owner.last_name

               total_storage='__'
               fdata+=[{
               'file_name':str(fshare.data.file_name),
               'name':name,
               'profile':str(fshare.data.details.profile.image),
               'last_modified':fshare.data.last_modified.date(),
               'id':fshare.id,
               'icon':str(fshare.data.icon.image), 
               'file_size_kb':total_storage,
               'location':'Shared with me',
               'location_icon':'bi bi-people'
               }]


            files=Data.objects.filter(owner=userid,starred=True,binned_date__isnull=True,folder_name__isnull=True,parent_folder=None,status=True).all().order_by('file_name')

            data=[]
            for file in files:
               size=int(file.file_size_kb)
               if userid==file.owner_id:
                   name='me'
               else:
                   name=file.owner.first_name+' '+file.owner.last_name

               total_storage=size_unit(size)
               data+=[{
               'file_name':str(file.file_name),
               'name':name,
               'profile':str(file.details.profile.image),
               'last_modified':file.last_modified.date(),
               'id':file.id,
               'icon':str(file.icon.image), 
               'file_size_kb':total_storage,
               'location':'My Drive',
               'location_icon':'bi bi-hdd'
               }]

            shares=Shared.objects.filter(shared_to=userid,starred=True,data__binned_date__isnull=True,data__folder_name__isnull=True,status=True).all().order_by('data__file_name')

            for share in shares:
               size=int(share.data.file_size_kb)
               if userid==share.owner_id:
                   name='me'
               else:
                   name=share.owner.first_name+' '+share.owner.last_name

               total_storage=size_unit(size)
               data+=[{
               'file_name':str(share.data.file_name),
               'name':name,
               'profile':str(share.data.details.profile.image),
               'last_modified':share.data.last_modified.date(),
               'id':share.id,
               'icon':str(share.data.icon.image), 
               'file_size_kb':total_storage,
               'location':'Shared with me',
               'location_icon':'bi bi-people'
               }]

            return JsonResponse(fdata+data,safe=False)
        
        else:
            return JsonResponse({"message":"invalid request"},status=400)

    else:
        return JsonResponse({"message":"user not authenticated"},status=401)




def shared_star(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
        
            data = json.loads(request.body)
        
            star=data.get('star')
            share_id=data.get('id')
            if share_id :
                if star=="true":
                    
                    update=Shared.objects.filter(id=share_id).first()
                    update.starred=True
                    update.save()
                    return JsonResponse({"message":"updated"},status=200)

                elif star=="False":

                    update=Shared.objects.filter(id=share_id).first()
                    update.starred=False
                    update.save()
                    return JsonResponse({"message":"updated"},status=200)


                else:
                    return JsonResponse({"message":"invalid data"},status=400)
            else:
                return JsonResponse({"message":"incorrect id"},status=400)
        else:
            return JsonResponse({"message":"invalid request"},status=401)
        
    else:
        return JsonResponse({"message":"user not authenticated"},status=400)




def bin(request):
    if request.user.is_authenticated:
        if request.method == 'POST':

            data = json.loads(request.body)
            bin=data.get('bin')
            data_id=data.get('id')

            if data_id:
                update=Data.objects.filter(id=data_id).first()
                if bin=="in":
                    update.binned_date=datetime.datetime.now()
                    update.save()
                    return JsonResponse({"message":"moved to bin"},status=200)

    
                elif bin=="out":
                
                    update.binned_date=None
                    update.save()
                    return JsonResponse({"message":"removed from bin"},status=200)

                elif bin=="permanent":
                
                    update.status=False
                    update.save()
                    return JsonResponse({"message":"deleted the item permanently"},status=200)
                
                else:
                    return JsonResponse({"message":"inccorect bin action"},status=400)
                
            else:
                return JsonResponse({"message":"invalid data_id "},status=400)
            



        if request.method == 'GET':
           

            userid = request.user.id
            folders=Data.objects.filter(owner=userid,status=True,binned_date__isnull=False,folder_name__isnull=False).all()
            
            fdata=[]
            for folder in folders:
               
               start=folder.binned_date
               now=datetime.datetime.now()
               timediff = now - start
               if timediff.seconds>=2592000:
                    folder.status=False
                    folder.save()

               total_storage='__'
             
               name='me'
              
               fdata+=[{
               'folder_name':str(folder.folder_name),
               'owner__first_name':name,
               'binned_date':folder.binned_date.date(),
               'id':folder.id,
               'starred':folder.starred,
               'profile':str(folder.details.profile.image),
               'icon':str(folder.icon.image), 
               'file_size_kb':total_storage
               }]

            files=Data.objects.filter(owner=userid,status=True,binned_date__isnull=False,folder_name__isnull=True).all().order_by('file_name')
            
            data=[]
            for file in files:
               
               start=file.binned_date
               now=datetime.datetime.now()
               timediff = now - start
               if timediff.seconds>=2592000:
                    file.status=False
                    file.save()

               size=file.file_size_kb

               total_storage=size_unit(size)
             
               name='me'
              
               data+=[{
               'file_name':str(file.file_name),
               'owner__first_name':name,
               'binned_date':file.binned_date.date(),
               'id':file.id,
               'starred':file.starred,
               'profile':str(file.details.profile.image),
               'icon':str(file.icon.image), 
               'file_size_kb':total_storage
               }]
            return JsonResponse(fdata+data,safe=False)
        
        else:
            return JsonResponse({"message":"invalid request"},status=400)

    else:
        return JsonResponse({"message":"user not authenticated"},status=401)




def rename(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
        
            data = json.loads(request.body)
        
            rename=data.get('rename')
            dataid=data.get('id')

            file=Data.objects.filter(id=dataid,folder_name=None)

            if rename and file.exists():
                first=file.first()
                initial_path = first.file_name.path
                new_path = settings.MEDIA_ROOT+rename
                os.rename(initial_path, new_path)
                first.file_name=rename
                first.save()

                return JsonResponse({"message":"update file name succesfully"},status=200)
            elif rename:
                new=Data.objects.filter(id=dataid).first()
                new.folder_name=rename
                new.save()
                
                return JsonResponse({"message":"update folder name succesfully"},status=200)

            else:
                return JsonResponse({"message":"invalid details"},status=400)
        else:
            return JsonResponse({"message":"invalid method"},status=400)




def share(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            user_id = request.user.id
            
            all_users=User_Details.objects.values('user__first_name','user__last_name','user','profile__image','user').exclude(user=user_id).order_by('user__first_name')
            
            return JsonResponse(list(all_users),safe=False)
    

        if request.method == 'POST':
            data = json.loads(request.body)
            
            share=data.get('share_to_id')
            user_id = request.user.id
            data=data.get('id')
        
            shareid=User.objects.get(id=share)
            
            check=Data.objects.filter(id=data)

                
            if check.exists():
                add=Shared.objects.create(
                    data=check.get(id=data),
                    shared_to=shareid,
                    owner_id=user_id,
                    shared_on=datetime.datetime.now(),
                    status=True
                )
                return JsonResponse({"message":"shared succesfully"},status=200)

        else:
            return JsonResponse({"message":"invalid request"},status=400)
    else:
        return JsonResponse({"messsage":"user nor authenticated"},status=401)

            


def shared_with_me(request):
    if request.user.is_authenticated:
        if request.method == 'GET':

            userid = request.user.id
            
            files=list(Shared.objects.filter(shared_to=userid,status=True).all())
            
            data=[]
            for file in files:
               details=User_Details.objects.filter(user=file.owner).first()
               profilepic=details.profile.image
               star=file.starred
               staricon=star_icon(star)
               if userid==file.owner_id:
                   name='me'
               else:
                   name=file.owner.first_name+' '+file.owner.last_name
                
               data+=[{
               'file_name':str(file.data.file_name),
               'profile':str(profilepic),
               'owner__first_name':name,
               'shared_on':file.shared_on.date(),
               'id':file.id,
               'folder_name':file.data.folder_name,
               'size':file.data.file_size_kb,
               'icon':str(file.data.icon.image),
               'starred':file.starred,
               'star_icon':staricon
               }]
          
            return JsonResponse(list(data),safe=False)
        
        else:
            return JsonResponse({"message":"invalid request"},status=400)
    else:
        return JsonResponse({"messsage":"user nor authenticated"},status=401)






def recent(request):
    if request.method == 'GET':
         if request.user.is_authenticated:
            userid = request.user.id
            
            files=Data.objects.filter(owner=userid,status=True,binned_date__isnull=True,folder_name__isnull=True).all().order_by("-last_modified")
            
            data=[]
            for file in files:
                if userid==file.owner_id:
                   name='me'
                else:
                   name=file.owner.first_name+' '+file.owner.last_name
                size=file.file_size_kb

                if file.parent_folder:
                   folder=Data.objects.filter(id=file.id).values('parent_folder').first()
                   p_id=folder.get('parent_folder')
                   parent=Data.objects.filter(id=p_id).first()
                   location=parent.folder_name
        
                else:
                   location='My Drive'

                total_storage=size_unit(size)
                datenow=datetime.date.today()
                opened=file.last_opened.date()
                if datenow==opened:
                    time=file.last_opened.time()
                else:
                    time=file.last_opened.date()

                data+=[{
                'file_name':str(file.file_name),
                'profile':str(file.details.profile.image),
                'owner__first_name':name,
                'created':time,
                'id':file.id,
                'starred':file.starred,
                'icon':str(file.icon.image), 
                'file_size_kb':total_storage,
                'location':location
                }]
            
            return JsonResponse(data,safe=False)
         
         else:
            return JsonResponse({"message":"invalid request"},status=400)
    else:
         return JsonResponse({"message":"invalid method"},status=400)  




def storage(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            user_id = request.user.id
            storages=list(Data.objects.filter(owner=user_id,folder_name__isnull=True,status=True).values('file_size_kb'))
            total=0
            for storage in storages:
                storage=storage['file_size_kb']
                total+=storage
            total_storage=size_unit(total)
            return JsonResponse(total_storage,safe=False)
            
        else:
            return JsonResponse({"message":"invalid request"},status=400)
    else:
        return JsonResponse({"messsage":"user nor authenticated"},status=400)
    
    
def suggested(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            user_id = request.user.id



            files=Data.objects.filter(owner=user_id,binned_date=None,folder_name__isnull=True,status=True).values('file_name','icon__image').order_by("-id")[0:4]
            
            return JsonResponse({"files":list(files)})           
        else:
            return JsonResponse({"message":"invalid request"},status=401)
    else:
        return JsonResponse({"messsage":"user nor authenticated"},status=400)





def inside_folder(request):
    if request.user.is_authenticated:
        if request.method == 'POST':

            data = json.loads(request.body)
            folderid=data.get('id')

            user_id = request.user.id
            
            folders=Data.objects.filter(parent_folder=folderid,folder_name__isnull=False,status=True).all()
            fdata=[]
            for folder in folders:
               name='me'
               total_storage='__'
               fdata+=[{
               'folder_name':folder.folder_name,
               'profile':str(folder.details.profile.image),
               'owner__first_name':name,
               'last_modified':folder.last_modified.date(),
               'id':folder.id,
               'starred':folder.starred,
               'icon':str(folder.icon.image), 
               'size':total_storage
               }]
            files=Data.objects.filter(parent_folder=folderid,folder_name__isnull=True,status=True).all()
            data=[]
            for file in files:
               size=file.file_size_kb
               name='me'
               total_storage=size_unit(size)
               data+=[{
               'file_name':str(file.file_name),
               'profile':str(file.details.profile.image),
               'owner__first_name':name,
               'last_modified':file.last_modified.date(),
               'id':file.id,
               'starred':file.starred,
               'icon':str(file.icon.image), 
               'size':total_storage
               }]
            
            return JsonResponse(fdata+data,safe=False)         
        else:
            return JsonResponse({"message":"invalid request"},status=400)
    else:
        return JsonResponse({"messsage":"user nor authenticated"},status=400)




def empty_bin(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            
            user_id = request.user.id
            datas=Data.objects.filter(owner=user_id,binned_date__isnull=False).all()
            for data in datas :
                data.status=False
                data.save()
            return JsonResponse({"message":"bin emptied"},status=200)
        else:
            return JsonResponse({"message":"invalid request"},status=400)
    else:
        return JsonResponse({"messsage":"user not authenticated"},status=400)
        

    
def storage_usage(request):
    if request.method == 'GET':
         if request.user.is_authenticated:
            userid = request.user.id
            
    
            files=Data.objects.filter(owner=userid,status=True,binned_date=None,folder_name__isnull=True).all().order_by("-file_size_kb")

            data=[]
            for file in files:
          
               size=file.file_size_kb
               total_storage=size_unit(size)
               data+=[{
               'file_name':str(file.file_name),
               'icon':str(file.icon.image), 
               'file_size':total_storage
               }]
            
            return JsonResponse(data,safe=False)
         
         else:
            return JsonResponse({"message":"invalid request"},status=401)
    else:
         return JsonResponse({"message":"invalid method"},status=400)



    
def file_format(request):
    if request.user.is_authenticated:
        if request.method == 'POST':

            imagee = request.FILES.get('image')
            formatt = request.POST.get('format')

            user_id = request.user.id

            new=File_Icon.objects.create(
                image=imagee,
                format=formatt,
                status=True
            )
            return JsonResponse({"message":"uploaded"},status=400)
        else:
            return JsonResponse({"message":"invalid request"},status=401)
    else:
        return JsonResponse({"messsage":"user not authenticated"},status=400)
    
    
    

# views.py
import json
import pytesseract
from PIL import Image
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Path of working folder on Disk
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

@csrf_exempt
def upload_file(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']

        # Save the uploaded file
        with open(file.name, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # Recognize text with Tesseract
        result = pytesseract.image_to_string(Image.open(file))

        # Save the text into a JSON file
        data = {'text': result}
        with open('output.json', 'w') as json_file:
            json.dump(data, json_file)

        return JsonResponse({'message': 'File uploaded and text extracted successfully'})

    return JsonResponse({'error': 'No file found'}, status=400)
# import os
# from datetime import datetime
# from PyPDF2 import PdfReader
# import pytesseract
# from django.http import JsonResponse
# from .models import FIR, Data, File_Icon, User_Details

# def extract_text_from_pdf(pdf_file):
#     pdf_reader = PdfReader(pdf_file)
#     text = ''
#     for page_num in range(len(pdf_reader.pages)):
#         text += pdf_reader.pages[page_num].extract_text()
#     return text

# def perform_ocr(image):
#     text = pytesseract.image_to_string(image)
#     return text

# def file_upload2(request):
#     if request.method == 'POST':
#         if request.user.is_authenticated:
#             file = request.FILES.get('file')
#             folder_id = request.POST.get('folderid')
#             user_id = request.user.id

#             if file:
#                 if file.name.endswith('.pdf'):
#                     extracted_text = extract_text_from_pdf(file)
#                 else:
#                     return JsonResponse({"message": "Unsupported file type"}, status=400)

#                 extracted_text += perform_ocr(file)

#                 FIR.objects.create(file=file, extracted_data=extracted_text, status=True)

#                 owner_id = request.user
#                 detail = User_Details.objects.get(user=user_id)

#                 if folder_id:
#                     folder_exists = Data.objects.filter(id=folder_id).exists()
#                     if not folder_exists:
#                         return JsonResponse({"message": "Incorrect folder ID"}, status=400)
#                     parent_folder = Data.objects.get(id=folder_id)
#                 else:
#                     parent_folder = None

#                 if Data.objects.filter(file_name=file.name, owner=owner_id).exists():
#                     return JsonResponse({"message": "File name already exists"}, status=400)

#                 file_extension = os.path.splitext(file.name)[1]

#                 icon, created = File_Icon.objects.get_or_create(format=file_extension, defaults={'image': 'default_image.png', 'status': True})

#                 new_data = Data.objects.create(
#                     file_name=file.name,
#                     owner=owner_id,
#                     file_size_kb=file.size / 1024,
#                     last_modified=datetime.now(),
#                     parent_folder=parent_folder,
#                     icon=icon,
#                     details=detail
#                 )

#                 return JsonResponse({"message": "File saved successfully"}, status=200)
#             else:
#                 return JsonResponse({"message": "No file found"}, status=400)
#         else:
#             return JsonResponse({"message": "User is not authenticated"}, status=401)
#     else:
#         return JsonResponse({"message": "Invalid request method"}, status=400)

import os
from django.utils import timezone
from .models import FIR

def file_upload3(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            file = request.FILES.get('file')
            folder_id = request.POST.get('folderid')
            user_id = request.user.id
            owner_id = User.objects.get(id=user_id)
            
            if file:
                # Check if folder id is provided and exists
                if folder_id:
                    folder_exists = Data.objects.filter(id=folder_id).exists()
                    if not folder_exists:
                        return JsonResponse({"message": "Incorrect folder id"}, status=400)
                
                # Check if file with same name already exists for the user
                if Data.objects.filter(file_name=file.name, owner=owner_id).exists():
                    return JsonResponse({"message": "File name already exists"}, status=400)
                
                # Save file to Data table
                data_instance = Data.objects.create(
                    file_name=file.name,
                    owner=owner_id,
                    file_size_kb=file.size/1024,
                    last_modified=timezone.now(),
                    parent_folder_id=folder_id,
                )
                
                # Save content to FIR table
                fir_instance = FIR.objects.create(
                    file=data_instance,
                    extracted_data=file.read(),  # Store binary content directly
                    status=True  # Default status
                )
                
                return JsonResponse({"message": "File and data saved successfully"}, status=200)
                
            else:
                return JsonResponse({"message": "No file found"}, status=400)
        else:
            return JsonResponse({"message": "User is not authenticated"}, status=401)
    else:
        return JsonResponse({"message": "Invalid request method"}, status=400)
