## API kulcsok:
 - API Key: f4dafb35805f4fe
 - API Secret: 8264610ae5c224f

## Fájl név és útvonal:
 - EI100-00003
 - /home/alex/university/szakdoli/test_zip/EI100-00003.LZH

## Kétlépcsős feltöltés

1. fájl feltöltés:
curl -X POST 'http://vir-dev.home:8001/api/method/upload_file' \
  -H 'Authorization: token f4dafb35805f4fe:8264610ae5c224f' \
  -F 'file=@/home/alex/university/szakdoli/test_zip/EI100-00003.LZH' \
  -F 'is_private=1'
 
Válasz:
{
  "message": {
    "name": "89e50bf8f3",
    "owner": "cconto_system@email.com",
    "creation": "2025-04-01 15:48:57.271900",
    "modified": "2025-04-01 15:48:57.271900",
    "modified_by": "cconto_system@email.com",
    "docstatus": 0,
    "idx": 0,
    "file_name": "EI100-00003.LZH",
    "is_private": 1,
    "file_type": "BIN",
    "is_home_folder": 0,
    "is_attachments_folder": 0,
    "file_size": 24206,
    "file_url": "/private/files/EI100-00003.LZH",
    "folder": "Home",
    "is_folder": 0,
    "content_hash": "3364131b9ee1b3f95f5baa01b063a624",
    "uploaded_to_dropbox": 0,
    "uploaded_to_google_drive": 0,
    "doctype": "File"
  }
}

name beírása az útvonalba: "file": "http://vir-dev.home:8001/app/file/5c14a80d64"

2. doctype létrehozás:
curl -X POST 'http://vir-dev.home:8001/api/resource/data-packet' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: token f4dafb35805f4fe:8264610ae5c224f' \
  -d '{"file_name": "EI100-00003" , "file": "http://vir-dev.home:8001/app/file/5c14a80d64"}

Válasz:
{
  "data": {
    "name": "EI100-00003",
    "owner": "cconto_system@email.com",
    "creation": "2025-04-01 15:49:22.872700",
    "modified": "2025-04-01 15:49:22.872700",
    "modified_by": "cconto_system@email.com",
    "docstatus": 0,
    "idx": 0,
    "file_name": "EI100-00003",
    "file": "http://vir-dev.home:8001/app/file/89e50bf8f3",
    "is_processed": 0,
    "doctype": "data-packet"
  }
}
