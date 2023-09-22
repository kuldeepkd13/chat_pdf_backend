from django.http import JsonResponse
from django.contrib import messages, auth
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from .models import User as CustomUser
import json
import os
from dotenv import load_dotenv
from .forms import PdfUploadForm
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain

load_dotenv()

@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        # Check if a user with the same username already exists
        existing_user = CustomUser.objects.filter(username=username).first()
        if existing_user:
            return JsonResponse({'error': 'Username already exists.'}, status=400)

        if password == confirm_password:
            user = CustomUser(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
                confirm_password=confirm_password
            )
            user.save()
            return JsonResponse({'message': 'User registered successfully.'}, status=201)
        else:
            return JsonResponse({'error': 'Passwords do not match.'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)
    

@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        try:
            user = CustomUser.objects.get(username=username)
            if user.password == password:
                # Authentication successful
                auth_login(request, user)
                print(user.username)
                messages.success(request, 'Logged in successfully.')
                return JsonResponse({'message': 'Logged in successfully.','username': user.username}, status=200)
            else:
                return JsonResponse({'error': 'Invalid password for the provided username.'}, status=400)
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'Invalid username or password.'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)
    

pdf_data = {}

# Load or create an empty chat history list in the session
def get_or_create_chat_history(request):
    chat_history = request.session.get('chat_history', [])
    return chat_history

def process_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text=text)
    store_name = pdf_file.name[:-4]  # Extract the name without the '.pdf' extension
    return chunks, store_name

@csrf_exempt
def pdf_upload_view(request):
    pdf_name = None
    if request.method == 'POST':
        form = PdfUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = form.cleaned_data['pdf_file']
            chunks, pdf_name = process_pdf(pdf_file)
            embeddings = OpenAIEmbeddings()
            VectorStore = FAISS.from_texts(chunks, embedding=embeddings)
            pdf_data[pdf_name] = VectorStore  # Store data in memory instead of a file
            response_data = {'pdf_name': pdf_name}
            return JsonResponse(response_data, status=200)
        else:
            error_data = {'error_message': 'Invalid form data.'}
            return JsonResponse(error_data, status=400)
    else:
        form = PdfUploadForm()

    error_data = {'error_message': 'Invalid request method.'}
    return JsonResponse(error_data, status=400)

@csrf_exempt
def chat_view(request):
    pdf_name = request.GET.get('pdf_name')
    chat_history = get_or_create_chat_history(request)  # Get or create chat history
    
    response_data = {}

    if pdf_name:
        VectorStore = pdf_data.get(pdf_name)
        if VectorStore is not None:
            query = request.GET.get('query', '')
            if query:
                docs = VectorStore.similarity_search(query=query, k=3)
                llm = OpenAI()
                chain = load_qa_chain(llm, chain_type="stuff")
                response = chain({"input_documents": docs, "question": query}, return_only_outputs=True)
                response_text = response.get('output_text', "No answer found.")
                chat_history.append({'question': query, 'response': response_text})
                request.session['chat_history'] = chat_history
                response_data['response_text'] = response_text
            else:
                response_data['response_text'] = ""
            response_data['pdf_name'] = pdf_name
            response_data['query'] = query
            response_data['chat_history'] = chat_history
        else:
            error_data = {'error_message': 'PDF data not found.'}
            return JsonResponse(error_data, status=400)
    else:
        error_data = {'error_message': 'PDF name not provided.'}
        return JsonResponse(error_data, status=400)

    return JsonResponse(response_data)


@csrf_exempt
def end_chat_view(request):
    if request.method == 'POST':
        pdf_name = request.POST.get('pdf_name')
        if pdf_name:
            try:
                # Remove the PDF data from the in-memory dictionary
                if pdf_name in pdf_data:
                    del pdf_data[pdf_name]

                # Clear the chat history from the session
                request.session['chat_history'] = []

                response_data = {'message': 'Chat ended successfully.'}
                return JsonResponse(response_data)
            except KeyError:
                pass

    error_data = {'error_message': 'PDF name not provided.'}
    return JsonResponse(error_data, status=400)
    
def menu(request):
    data = {"message": "hello"}
    return JsonResponse(data)