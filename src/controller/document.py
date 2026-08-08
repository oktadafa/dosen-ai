from telegram import Update
from telegram.ext import  ContextTypes
from pdf2image import convert_from_path

async def document(update: Update, context: ContextTypes) -> None:
    if update.message.document:
        if update.message.document.mime_type == "application/pdf":
            try:
                document = update.message.document
                pdf_file = await document.get_file()
                images = convert_from_path(pdf_file.file_path, fmt='jpeg')    
                print(images, 'test')    
                # document = update.message.document
                # file_id = document.file_id
                # file_name = document.file_name
                # file_size = document.file_size
                # file_type= document.mime_type
                # await update.message.reply_text(
                #     f"Received document:\n"
                #     f"File ID: {file_id}\n"
                #     f"File Name: {file_name}\n"
                #     f"File Size: {file_size} bytes"
                #     f"File Type: {file_type}"
                # )
            except Exception as e:
                print(f"Error occurred while processing the document: {e}")
                await update.message.reply_text("Sorry, I encountered an error while processing your document.")
        else:
            return await update.message.reply_text("Please send a PDF document.")
    else:
        await update.message.reply_text("No document found in the message.")