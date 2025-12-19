from .forms import UserSignUpForm
from django.shortcuts import redirect, render
from django.contrib.auth import login
from django.views import View


class SignUpView(View):
    def get(self, request):
        form = UserSignUpForm()
        return render(request, 'registration/signup.html', {'form': form})

    def post(self, request):
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log the user in after sign-up
            # Redirect to the todo list view after successful sign-up
            return redirect('todo_list')
        return render(request, 'registration/signup.html', {'form': form})
