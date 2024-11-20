from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai
import typing_extensions as typing
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Conversation
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .models import Policy , User , Conversation
from .forms import SignUpForm


# AIzaSyCW1_W1-w3fnWvc4OlCca_zI1607-60XtY
# AIzaSyASINCqIKiWdWEcmz3_Ij-u3ELqSSnBPDQ

# class Response(typing.TypedDict):
#   response_item: str
genai.configure(api_key='AIzaSyCW1_W1-w3fnWvc4OlCca_zI1607-60XtY')
# Initialize the model
model = genai.GenerativeModel('gemini-1.5-pro',
                            #   generation_config={"response_mime_type": "application/json",
                            #                      "response_schema": list[Response]}
                            )
import os

media = os.path.join(os.path.dirname(__file__), 'media')
sample_pdf = genai.upload_file(os.path.join(media, "Financial_Regulations_2015.pdf"))
recruitment_policy = genai.upload_file(os.path.join(media, "Recruitment and Selection Policy and Procedures 2017 .PDF"))
sexual_harassment_policy = genai.upload_file(os.path.join(media, "Sexual Harassment Policy 2010 .PDF"))
staff_discipline_policy = genai.upload_file(os.path.join(media, "Staff Disciplinary and Grievance Procedures Code 2013 .pdf"))
staff_training_policy = genai.upload_file(os.path.join(media, "Staff Training and Development Policy 2018.pdf"))


@csrf_exempt
@login_required
def chat_view(request):
    if request.method == 'POST':
        prompt = request.POST.get('prompt')
        conversation = Conversation.objects.filter(user=request.user).last()
        # get the user status 
        user_details = User.objects.get(username=request.user.username)
        
        # Add specific instructions to the prompt
        instructions = (
             "You are a chatbot for the University of Zambia (UNZA). "
            "Staff and students will ask you questions based on the policies for the school. Determine the user's role based on their status. "
            "Students cannot access staff policies. "
            "Please provide accurate and helpful responses based on the user's role. "
            "Do not ask if the user is a staff member or student. "
            "Do not ask for a lot of details. "
            "Check the policies for the answer. "
            "Do not make up answers. "
            "It is fine if you use my name and status in the conversation. "
            "If the information is in the document, give full details. "
            "Do not say that you don't know the answer; check the document and give a response according to the document."
            
            
        )
        # add the document to the prompt
        # add all the files to the prompt
        
        full_prompt = f"{instructions}\n\nUser: {prompt} \n\nFile1: {sample_pdf} \n\nFile2: {recruitment_policy} \n\nFile3: {sexual_harassment_policy} \n\nFile4: {staff_discipline_policy} \n\nFile5: {staff_training_policy} \n\nConversation:{conversation} \n\nUser Status: {user_details.status} \n\nName: {user_details.username}"

        


        # Check user status and retrieve relevant policies
       
        if user_details.status == 'staff':
            policies = Policy.objects.all()
        else:
            policies = Policy.objects.filter(is_staff_only=False)

        # Fetch the content from the database directly if stored in a TextField
        policy_contents = "\n\n".join([policy.content for policy in policies])

        # Add the policies to the prompt
        full_prompt = f"{full_prompt}\n\nPolicies:\n{policy_contents}"

        # Generate the response using the AI model
        response = model.generate_content(full_prompt)
        bot_response = response.text

        # Save the conversation to the database
        conversation = Conversation(user=request.user, user_input=prompt, bot_response=bot_response)
        conversation.save()

        return JsonResponse({'response': bot_response})

    return render(request, 'app/index.html')

def format_guide_view(request):
    return render(request, 'app/format_guide.html')

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import SignUpForm

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.status = 'student'  # Set the default status
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('chat')
    else:
        form = SignUpForm()
    return render(request, 'app/signup.html', {'form': form})

def custom_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('chat')  # Redirect to the index page after login
    else:
        form = AuthenticationForm()
    return render(request, 'chat/login.html', {'form': form})

def custom_logout_view(request):
    logout(request)
    return render(request, 'login.html') # Redirect to the index page after logout