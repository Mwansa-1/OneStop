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
from .models import Policy


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

@csrf_exempt
@login_required
def chat_view(request):
    if request.method == 'POST':
        prompt = request.POST.get('prompt')
        
        # Add specific instructions to the prompt
        instructions = (
            "You are a chatbot for the University of Zambia (UNZA). "
            "Staff and students will ask you questions based on the policies for the school. Determine the user's role based on their status. "
            "Students cannot access staff policies. "
            "Please provide accurate and helpful responses based on the user's role."
            "Do not ask if the user is a staff member or student. "
            "Do not ask for a lot of details"
            "Check the policies for the answer."
          
            
        )
        # add the document to the prompt
        full_prompt = f"{instructions}\n\nUser: {prompt} \n\nFile: {sample_pdf}"

        # Check user status and retrieve relevant policies
        user_status = request.user.status
        if user_status == 'staff':
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

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'chat/signup.html', {'form': form})


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
    return render(request, 'app/logout.html') # Redirect to the index page after logout