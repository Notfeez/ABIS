from django.shortcuts import render
from django.shortcuts import redirect

def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        
        return view_func(request, *args, **kwargs)
    
    return wrapper_func